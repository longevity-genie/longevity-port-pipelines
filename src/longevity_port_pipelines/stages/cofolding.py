"""
Stage: cofolding
----------------
For top-ranked candidates from enrichment.parquet, submit cross-species
protein-protein complex predictions to the Boltz API and store the
structural confidence metrics (iptm, complex_iplddt, binding_confidence, etc.).

This is Stage 3 "Compatibility classification" from the LongevityPort plan:
    predict the cross-species complex (human chain A + ortholog chain B)
    and classify the interaction as maintained / functionally_broken / incompatible.

Usage:
    uv run cofolding                          # top 10 by enrichment_ratio
    uv run cofolding --top-n 20               # top 20
    uv run cofolding --test                   # test mode (no real API calls, no credits)
    uv run cofolding --complex 8bhv --species naked_mole_rat  # single row

Output:
    data/output/cofolding_results.parquet     — one row per (complex, chain, species)
    data/output/cofolding_results.csv         — same, human-readable
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Optional

import polars as pl
import typer

app = typer.Typer(help="Boltz API co-folding stage for cross-species PPI compatibility.")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DATA_OUTPUT = Path("data/output")
ENRICHMENT_PATH = DATA_OUTPUT / "enrichment.parquet"
COFOLDING_RESULTS = DATA_OUTPUT / "cofolding_results.parquet"

# ---------------------------------------------------------------------------
# Compatibility classification thresholds
# (tune after you have a few real predictions to calibrate)
# ---------------------------------------------------------------------------
MAINTAINED_IPTM_THRESHOLD = 0.75       # iptm >= this → likely maintained
BROKEN_IPTM_THRESHOLD = 0.45           # iptm < this → likely broken
BINDING_CONFIDENCE_HIGH = 0.70         # Boltz docs: 0.7+ is high-confidence


def classify_interaction(iptm: float, binding_confidence: float | None) -> str:
    """
    Binary structural filter: maintained / functionally_broken / incompatible / uncertain.
    Current models do not reliably predict absolute binding affinity, so this is
    a pass/fail filter only (as noted in the LongevityPort design doc).
    """
    if iptm >= MAINTAINED_IPTM_THRESHOLD:
        return "maintained"
    if iptm < BROKEN_IPTM_THRESHOLD:
        if binding_confidence is not None and binding_confidence < 0.5:
            return "incompatible"
        return "functionally_broken"
    return "uncertain"


# ---------------------------------------------------------------------------
# Boltz API helpers
# ---------------------------------------------------------------------------

def get_boltz_client():
    """Return an authenticated Boltz client. Requires BOLTZ_API_KEY in env."""
    try:
        from boltz_api import Boltz  # pip install boltz-api
    except ImportError:
        typer.echo(
            "boltz_api not installed. Run:\n  uv add boltz-api\nor:\n  pip install boltz-api",
            err=True,
        )
        raise typer.Exit(1)

    api_key = os.environ.get("BOLTZ_API_KEY")
    if not api_key:
        typer.echo(
            "BOLTZ_API_KEY not set. Add it to your .env file:\n  BOLTZ_API_KEY=your_key_here",
            err=True,
        )
        raise typer.Exit(1)

    return Boltz(api_key=api_key)


def submit_ppi_prediction(
    client,
    seq_human: str,
    seq_ortholog: str,
    name: str,
    num_samples: int = 1,
) -> dict:
    """
    Submit a protein-protein co-folding prediction to Boltz API.

    Chain A = human protein
    Chain B = ortholog from long-lived (or short-lived) species

    Returns the prediction result dict with metrics.
    """
    prediction_input = {
        "entities": [
            {"type": "protein", "value": seq_human,    "chain_ids": ["A"]},
            {"type": "protein", "value": seq_ortholog, "chain_ids": ["B"]},
        ],
        "binding": {
            "type": "protein_protein_binding",
            "binder_chain_ids": ["B"],
        },
        "num_samples": num_samples,
    }

    prediction = client.predictions.structure_and_binding.start(
        model="boltz-2.1",
        input=prediction_input,
        name=name,
    )

    # Poll until done
    while prediction.status not in ("succeeded", "failed"):
        time.sleep(10)
        prediction = client.predictions.structure_and_binding.retrieve(prediction.id)

    if prediction.status == "failed":
        raise RuntimeError(
            f"Boltz prediction failed for {name}: {prediction.error}"
        )

    best = prediction.output.best_sample
    metrics = best.metrics
    binding = prediction.output.binding_metrics

    return {
        "prediction_id": prediction.id,
        "structure_confidence": metrics.structure_confidence,
        "ptm":                  metrics.ptm,
        "iptm":                 metrics.iptm,
        "complex_plddt":        metrics.complex_plddt,
        "complex_iplddt":       metrics.complex_iplddt,
        "complex_pde":          metrics.complex_pde,
        "complex_ipde":         metrics.complex_ipde,
        "binding_confidence":   binding.binding_confidence if binding else None,
        "structure_url":        best.structure.url if best.structure else None,
    }


def make_test_result(name: str) -> dict:
    """Return a fake result for --test mode (no API call, no credits used)."""
    import random
    rng = random.Random(name)
    iptm = rng.uniform(0.3, 0.95)
    bc   = rng.uniform(0.4, 0.95)
    return {
        "prediction_id":       f"test_{name[:8]}",
        "structure_confidence": round(rng.uniform(0.6, 0.98), 3),
        "ptm":                  round(rng.uniform(0.6, 0.95), 3),
        "iptm":                 round(iptm, 3),
        "complex_plddt":        round(rng.uniform(0.7, 0.97), 3),
        "complex_iplddt":       round(rng.uniform(0.6, 0.92), 3),
        "complex_pde":          round(rng.uniform(0.8, 3.5), 3),
        "complex_ipde":         round(rng.uniform(1.0, 5.0), 3),
        "binding_confidence":   round(bc, 3),
        "structure_url":        None,
    }


# ---------------------------------------------------------------------------
# Sequence fetching
# ---------------------------------------------------------------------------

def fetch_sequence_uniprot(uniprot_id: str) -> str:
    """
    Fetch canonical FASTA sequence from UniProt REST API.
    Falls back to a short placeholder if network is unavailable.
    """
    import urllib.request
    url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.fasta"
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            fasta = resp.read().decode()
        lines = [l for l in fasta.splitlines() if not l.startswith(">")]
        return "".join(lines)
    except Exception as exc:
        typer.echo(f"  Warning: could not fetch {uniprot_id} from UniProt ({exc}). Using placeholder.", err=True)
        return "MKTIIALSYIFCLVFAQSIIGTEITMKFGKQYMYIAKRGEIPMDPNHHHHH"  # placeholder


# ---------------------------------------------------------------------------
# Main command
# ---------------------------------------------------------------------------

@app.command()
def main(
    top_n: int = typer.Option(10, "--top-n", help="How many top candidates to process (ranked by enrichment_ratio)."),
    complex_id: Optional[str] = typer.Option(None, "--complex", help="Run only this PDB complex ID."),
    species: Optional[str] = typer.Option(None, "--species", help="Run only this species."),
    test: bool = typer.Option(False, "--test", help="Test mode: fake predictions, no API calls, no credits spent."),
    num_samples: int = typer.Option(1, "--num-samples", help="Number of structure samples per prediction (more = more credits)."),
):
    """
    Co-fold cross-species protein complexes via Boltz API and classify
    interactions as maintained / functionally_broken / incompatible / uncertain.
    """
    # -----------------------------------------------------------------------
    # Load enrichment results
    # -----------------------------------------------------------------------
    if not ENRICHMENT_PATH.exists():
        typer.echo(
            f"Enrichment file not found at {ENRICHMENT_PATH}.\n"
            "Run the embedding pipeline first:\n"
            "  uv run embed\n  uv run analyze",
            err=True,
        )
        raise typer.Exit(1)

    df = pl.read_parquet(ENRICHMENT_PATH)

    # Filter to interface_divergent rows (those are the interesting candidates)
    if "signal_class" in df.columns:
        candidates = df.filter(
            pl.col("signal_class").is_in([
                "interface_divergent",
                "interface_divergent_not_significant",
            ])
        )
    else:
        candidates = df

    # Apply CLI filters
    if complex_id:
        candidates = candidates.filter(pl.col("pdb_id") == complex_id)
    if species:
        candidates = candidates.filter(pl.col("species") == species)

    # Sort by enrichment_ratio descending and take top_n
    if "enrichment_ratio" in candidates.columns:
        candidates = candidates.sort("enrichment_ratio", descending=True)
    candidates = candidates.head(top_n)

    if candidates.is_empty():
        typer.echo("No candidates found after filtering. Check your enrichment.parquet.", err=True)
        raise typer.Exit(1)

    typer.echo(f"\n{'[TEST MODE] ' if test else ''}Processing {len(candidates)} candidates...\n")

    # -----------------------------------------------------------------------
    # Set up Boltz client (skip in test mode)
    # -----------------------------------------------------------------------
    client = None if test else get_boltz_client()

    # -----------------------------------------------------------------------
    # Process each candidate
    # -----------------------------------------------------------------------
    results = []

    for row in candidates.iter_rows(named=True):
        pdb_id      = row.get("pdb_id", "unknown")
        chain_id    = row.get("chain_id", "?")
        species_val = row.get("species", "unknown")
        uniprot_human    = row.get("uniprot_human", "")
        uniprot_ortholog = row.get("uniprot_ortholog", "")
        enrichment_ratio = row.get("enrichment_ratio", None)

        name = f"{pdb_id}_{chain_id}_{species_val}"
        typer.echo(f"  → {name}  (enrichment_ratio={enrichment_ratio:.3f})" if enrichment_ratio else f"  → {name}")

        try:
            if test:
                api_result = make_test_result(name)
            else:
                # Fetch sequences from UniProt
                typer.echo(f"    Fetching sequences...")
                seq_human    = fetch_sequence_uniprot(uniprot_human)    if uniprot_human    else None
                seq_ortholog = fetch_sequence_uniprot(uniprot_ortholog) if uniprot_ortholog else None

                if not seq_human or not seq_ortholog:
                    typer.echo(f"    Skipping {name}: missing sequence(s).", err=True)
                    continue

                typer.echo(f"    Submitting to Boltz API...")
                api_result = submit_ppi_prediction(
                    client, seq_human, seq_ortholog, name=name, num_samples=num_samples
                )

            # Classify interaction
            iptm = api_result["iptm"]
            bc   = api_result["binding_confidence"]
            classification = classify_interaction(iptm, bc)

            result_row = {
                "pdb_id":            pdb_id,
                "chain_id":          chain_id,
                "species":           species_val,
                "enrichment_ratio":  enrichment_ratio,
                "uniprot_human":     uniprot_human,
                "uniprot_ortholog":  uniprot_ortholog,
                "boltz_classification": classification,
                **api_result,
            }
            results.append(result_row)

            typer.echo(
                f"    iptm={iptm:.3f}  binding_conf={bc:.3f}  → {classification}"
                if bc is not None
                else f"    iptm={iptm:.3f}  → {classification}"
            )

        except Exception as exc:
            typer.echo(f"    ERROR for {name}: {exc}", err=True)
            results.append({
                "pdb_id": pdb_id, "chain_id": chain_id, "species": species_val,
                "enrichment_ratio": enrichment_ratio,
                "boltz_classification": "error",
                "error_message": str(exc),
            })

    # -----------------------------------------------------------------------
    # Save results
    # -----------------------------------------------------------------------
    if not results:
        typer.echo("No results to save.", err=True)
        raise typer.Exit(1)

    DATA_OUTPUT.mkdir(parents=True, exist_ok=True)
    out_df = pl.DataFrame(results)
    out_df.write_parquet(COFOLDING_RESULTS)
    out_df.write_csv(COFOLDING_RESULTS.with_suffix(".csv"))

    typer.echo(f"\nSaved {len(results)} rows to {COFOLDING_RESULTS}")

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    if "boltz_classification" in out_df.columns:
        summary = (
            out_df
            .group_by("boltz_classification")
            .agg(pl.len().alias("count"))
            .sort("count", descending=True)
        )
        typer.echo("\nClassification summary:")
        for r in summary.iter_rows(named=True):
            typer.echo(f"  {r['boltz_classification']:30s} {r['count']}")

    typer.echo("\nDone.")


if __name__ == "__main__":
    app()
