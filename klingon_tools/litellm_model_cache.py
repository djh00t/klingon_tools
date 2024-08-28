"""
klingon_model_cache.py
------------------------

This module is part of the `klingon_tools` library and is designed to fetch,
cache, and filter a list of supported LLM models from a remote JSON file. It
caches the fetched model data locally to avoid redundant downloads and provides
functionality for filtering the models based on inclusion and exclusion regex
patterns. Additionally, it updates an environment variable, `KLINGON_MODELS`,
with the filtered model names.

### Main Features:
1. **Caching**: The JSON file from the remote source is downloaded and stored
in a local cache. The cache is only refreshed if the remote data changes.
2. **Regex-based Filtering**: The models can be filtered using two criteria:
   - `allowed_regexes`: A dictionary of regex patterns specifying which models
     to include.
   - `ignored_regexes`: A list of regex patterns specifying which models to
     exclude.
3. **Environment Variable Update**: The filtered model names are stored in the
   `KLINGON_MODELS` environment variable as a comma-separated string.

### File Structure:
- `fetch_model_data()`: Fetches and caches the model list from a remote URL.
- `filter_models()`: Filters models based on allowed and ignored regex
patterns.
- `update_env_variable()`: Updates the environment variable with the filtered
model names.
- `get_supported_models()`: Orchestrates fetching, filtering, and environment
variable updates.

### Example Usage:

```python
# Example of allowed and ignored regex patterns
allowed = {
    'openai': 'gpt-4.*',  # Allow models starting with 'gpt-4'
}
ignored = [
    'sample_spec',  # Ignore 'sample_spec' model
]

# Get the supported models based on filtering
models = get_supported_models(allowed, ignored)

# Models returned
print(models)
# Output might be: {'gpt-4': {...}, 'gpt-4o': {...}}

# The KLINGON_MODELS environment variable will be set to:
# "gpt-4,gpt-4o"
print(os.environ.get('KLINGON_MODELS'))
"""

import os
import json
import hashlib
import requests
import re
from typing import List, Dict


# URL of the file to be downloaded (source of model names)
MODEL_URL = (
    "https://raw.githubusercontent.com/BerriAI/litellm/main/"
    "model_prices_and_context_window.json"
)
# Path to store the cached JSON file locally
CACHE_FILE = "/tmp/klingon_models_cache.json"

# Global settings for allowed and ignored model regex patterns
ALLOWED_REGEXES = {
    'openai': 'gpt-4.*',  # Allow models starting with 'gpt-4'
    'ollama': 'ollama/.*',  # Allow models starting with 'ollama/'
    # Allow models starting with 'anthropic/'
    'anthropic': 'anthropic/.*|claude.*',
    'allow_all': '.*',  # Allow all models - only for testing purposes
}

IGNORED_REGEXES = [
        'ai21',  # Ignore 'ai21' models until tested
        'amazon',  # Ignore 'amazon' models until tested
        'anyscale',  # Ignore 'anyscale' models until tested
        'bedrock',  # Ignore 'bedrock' models until tested
        'bison',  # Ignore 'bison' models until tested
        'dolphin',  # Ignore 'dolphin' models until tested
        'gecko',  # Ignore 'gecko' models until tested
        'cloudflare',  # Ignore 'cloudflare' models until tested
        'codestral',  # Ignore 'codestral' models until tested
        'cohere',  # Ignore 'cohere' models until tested
        'command',  # Ignore 'command' models until tested
        'dall-e',  # Ignore 'dall-e' models until tested
        'databricks',  # Ignore 'databricks' models until tested
        'deepinfra',  # Ignore 'deepinfra' models until tested
        'dolphin',  # Ignore 'dolphin' models until tested
        'deepseek',  # Ignore 'deepseek' models until tested
        'fireworks_ai',  # Ignore 'fireworks_ai' models until tested
        'friendliai',  # Ignore 'friendliai' models until tested
        'ft:',  # Ignore 'ft:' models until tested
        'j2-',  # Ignore 'j2-' models until tested
        'jamba',  # Ignore 'jamba' models until tested
        'luminous',  # Ignore 'luminous' models until tested
        'stable-diffusion',  # Ignore 'stable-diffusion' models until tested
        'medlm',  # Ignore 'medlm' models until tested
        'meta.llama',  # Ignore 'meta.llama' models until tested
        'mistral.mistral',  # Ignore 'mistral.mistral' models until tested
        'mistral.mixtral',  # Ignore 'mistral.mixtral' models until tested
        'mistral/',  # Ignore 'mistral/' models until tested
        'openrouter',  # Ignore 'openrouter' models until tested
        'palm',  # Ignore 'palm' models until tested
        'perplexity',  # Ignore 'perplexity' models until tested
        'replicate',  # Ignore 'replicate' models until tested
        'text-',  # Ignore 'text-' models until tested
        'sagemaker',  # Ignore 'sagemaker' models until tested
        'sample_spec',  # Ignore 'sample_spec' models until tested
        'together',  # Ignore 'together' models until tested
        'vertex',  # Ignore 'vertex' models until tested
        'voyage',  # Ignore 'voyage' models until tested
        'whisper',  # Ignore 'whisper' models until tested
        'tts',  # Ignore 'tts' models until tested
        'babbage',  # Ignore 'babbage' models until tested
        'davinci',  # Ignore 'davinci' models until tested
        'embed-',  # Ignore 'embed-' models until tested
]


def fetch_model_data() -> Dict[str, dict]:
    """
    Fetches the list of models from the remote JSON file and caches it locally.
    If a cached version exists and is identical to the new one, it is returned
    instead.

    Returns:
        Dict[str, dict]: A dictionary where keys are model names and values are
        model details.

    Raises:
        requests.exceptions.RequestException: If the HTTP request fails.

    Example:
        >>> fetch_model_data()
        {'gpt-4': {...}, 'gpt-4o': {...}, 'sample_spec': {...}}
    """
    # Check if a cached version exists and load it
    cached_data = None
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            cached_data = json.load(f)

    # Fetch the new data from the remote JSON file
    response = requests.get(MODEL_URL)
    response.raise_for_status()  # Raise an error if the request failed
    new_data = response.json()

    # Calculate hashes to compare the old cached data and the new fetched data
    new_data_hash = hashlib.md5(
        json.dumps(new_data, sort_keys=True).encode()).hexdigest()
    cached_data_hash = (
        hashlib.md5(
            json.dumps(cached_data, sort_keys=True).encode()
        ).hexdigest()
        if cached_data else None
    )

    # If the cached data is the same, return the cached model list
    if cached_data and new_data_hash == cached_data_hash:
        return cached_data

    # Cache the new data if it's different from the previous one
    with open(CACHE_FILE, 'w') as f:
        json.dump(new_data, f)

    return new_data


def filter_models(
    models: Dict[str, dict],
    allowed_regexes: Dict[str, str],
    ignored_regexes: List[str]
) -> Dict[str, dict]:
    """
    Filters the models based on allowed and ignored regex patterns.

    Args:
        models (Dict[str, dict]): The dictionary of models fetched from the
        remote source.
        allowed_regexes (Dict[str, str]): A dictionary of regex patterns where
        keys are model names or categories, and values are regex patterns. Only
        models matching these patterns are allowed.
        ignored_regexes (List[str]): A list of regex patterns. Models matching
        these patterns will be excluded.

    Returns:
        Dict[str, dict]: A filtered dictionary of models based on the allowed
        and ignored regex patterns.

    Example:
        >>> models = {'gpt-4': {...}, 'gpt-4o': {...}, 'sample_spec': {...}}
        >>> allowed = {'openai': 'gpt-4.*'}
        >>> ignored = ['sample_spec']
        >>> filter_models(models, allowed, ignored)
        {'gpt-4': {...}, 'gpt-4o': {...}}
    """
    filtered_models = {}

    for model_name, model_data in models.items():
        # Check if the model matches any of the ignored patterns
        if any(re.search(ignored_pattern, model_name)
               for ignored_pattern in ignored_regexes):
            continue

        # Check if the model matches any of the allowed patterns
        if any(re.search(allowed_pattern, model_name)
               for allowed_pattern in allowed_regexes.values()):
            filtered_models[model_name] = model_data

    return filtered_models


def update_env_variable(model_list: List[str]):
    """
    Updates the environment variable KLINGON_MODELS with a comma-separated list
    of model names.

    Args:
        model_list (List[str]): A list of model names to be set in the
        environment variable.

    Example:
        >>> update_env_variable(['gpt-4', 'gpt-4o', 'sample_spec'])
        # KLINGON_MODELS will be set to "gpt-4,gpt-4o,sample_spec"
    """
    os.environ['KLINGON_MODELS'] = ','.join(model_list)


def get_supported_models() -> Dict[str, dict]:
    """
    Retrieves the supported models, filters them based on global allowed and
    ignored regex patterns, updates the KLINGON_MODELS environment variable,
    and returns the filtered dictionary of models.

    Returns:
        Dict[str, dict]: A filtered dictionary of models based on the allowed
        and ignored regex patterns.

    Example:
        >>> models = get_supported_models()
        >>> print(models)
        {'gpt-4': {...}, 'gpt-4o': {...}}
    """
    # Fetch models from cache or remote
    models = fetch_model_data()
    # Filter models based on global allowed and ignored regexes
    filtered_models = filter_models(models, ALLOWED_REGEXES, IGNORED_REGEXES)
    # Update environment variable with filtered model names
    update_env_variable(list(filtered_models.keys()))
    return filtered_models


# Example usage when the script is run directly
if __name__ == "__main__":
    # Get the supported models based on global filtering settings
    models = get_supported_models()

    # Sort the model names alphabetically and create a list of sorted names
    model_names_only = sorted(models.keys())

    # Print the list of model names
    print(model_names_only)
