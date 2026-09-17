"""
Discover new Hugging Face models that may be eligible
for evaluation in the AI Agent Evaluation Dashboard.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from huggingface_hub import HfApi

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "huggingface"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
   
KNOWN_MODELS_PATH = PROCESSED_DIR / "known_hf_models.json"
NEW_MODELS_PATH = PROCESSED_DIR / "new_hf_models.json"

MIN_DOWNLOADS = 100

def fetch_models(limit=100):
    """
    Fetch modified text-generation models
    from the Hugging Face Hub.
    """

    api = HfApi()
    models = api.list_models(pipeline_tag="text-generation", sort="last_modified", limit=limit, full=True, gated=False)
    return list(models)


def model_to_dict(model):
    """
    Convert a Hugging Face ModelInfo object into
    a Python dictionary.
    """

    return {
        "model_id": model.id,
        "author": model.author,
        "sha": model.sha,
        "last_modified": (
            model.last_modified.isoformat() if model.last_modified else None
        ),
        "discovered_at": datetime.now(timezone.utc).isoformat(),
        "pipeline_tag": model.pipeline_tag,
        "downloads": model.downloads,
        "likes": model.likes,
        "tags": model.tags or [],
        "private": model.private,
        "gated": model.gated,
    }

def save_raw_snapshot(records):
    """
    Save the unfiltered Hugging Face response from
    this discovery run.
    """

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = RAW_DIR / f"models_{timestamp}.json"
    save_json(records,output_path)
    return output_path


def is_eligible_model(record):
    """
    Determine whether a model should enter the
    evaluation pipeline.
    """

    if record["pipeline_tag"]!= "text-generation":
        return False

    if record["private"] or record["gated"]:
        return False
    
    if record["downloads"] < MIN_DOWNLOADS:
        return False

    return True


def filter_eligible_models(records):
    """
    Filter discovered models using the project
    eligibility rules.
    """

    return [record for record in records if is_eligible_model(record)]


def load_known_model_ids():
    """
    Load model IDs encountered during previous
    discovery runs.
    """

    if not KNOWN_MODELS_PATH.exists():
        return set()

    with KNOWN_MODELS_PATH.open("r", encoding="utf-8") as f:
        records = json.load(f)

    return {record["model_id"] for record in records}


def find_new_models(eligible_models,known_ids):
    """
    Find eligible models that the pipeline has not
    seen previously.
    """

    return [model for model in eligible_models if model["model_id"] not in known_ids]

def save_json(data, path):
    """
    Save data as formatted JSON.
    """

    path.parent.mkdir(parents=True,exist_ok=True)

    with path.open("w",encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def update_known_models(eligible_models,known_ids):
    """
    Update the registry of models that have already
    been discovered.
    """

    existing = []

    if KNOWN_MODELS_PATH.exists():
        with KNOWN_MODELS_PATH.open("r", encoding="utf-8") as f:
            existing = json.load(f)

    newly_seen = [model for model in eligible_models if model["model_id"] not in known_ids]
    updated = existing + newly_seen
    save_json(updated,KNOWN_MODELS_PATH)
    

def main():
    models = fetch_models(limit=100)

    records = [model_to_dict(model) for model in models]
    raw_path = save_raw_snapshot(records)

    eligible_models = filter_eligible_models(records)
    known_ids = load_known_model_ids()
    new_models = find_new_models(eligible_models, known_ids)
    save_json(new_models,NEW_MODELS_PATH)
    update_known_models(eligible_models,known_ids)

    print(f"Fetched models: {len(records)}")
    print(f"Eligible models: {len(eligible_models)}")
    print(f"New models: {len(new_models)}")
    print(f"Raw snapshot: {raw_path}")
    print(f"New-model output: {NEW_MODELS_PATH}")

if __name__ == "__main__":
    main()