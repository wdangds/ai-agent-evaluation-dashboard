"""
Discover new Hugginng Face models that may be eligible for evaluation
in the AI Agent Evaluation Dashboard.
"""

from huggingface_hub import HfApi

def fetch_models(limit = 100):
    """
    Fetch recently modifed text-generation models 
    from HFHub.
    """
    api = HfApi()
    models = api.list_models(
        pipeline_tag="text-generation",
        sort = "last_modified",
        limit = limit,
        full = True
    )

    return list(models)







def main():
    
    models = fetch_models(limit=100)
    model = models[0]
    print(model)
if __name__ == "__main__":
    main()