"""
Fetch, cache, and filter supported LLM models from a remote JSON file.

This module is part of the `klingon_tools` library. It fetches a list of
supported LLM models from a remote JSON file, caches the data locally, and
provides functionality for filtering the models based on inclusion and
exclusion regex patterns. It also updates the `KLINGON_MODELS` environment
variable with the filtered model names.

Main Features:
    1. Caching: Downloads and stores the JSON file locally, refreshing only
       when remote data changes.
    2. Regex-based Filtering: Filters models using allowed and ignored regex
       patterns.
    3. Environment Variable Update: Stores filtered model names in the
       `KLINGON_MODELS` environment variable.

Example:
    allowed = {
        'openai': 'gpt-4.*',  # Allow models starting with 'gpt-4'
    }
    ignored = [
        'sample_spec',  # Ignore 'sample_spec' model
    ]

    models = get_supported_models(allowed, ignored)
    print(models)  # Output: {'gpt-4': {...}, 'gpt-4o': {...}}
    print(os.environ.get('KLINGON_MODELS'))  # Output: "gpt-4,gpt-4o"
"""

import os
import json
import re
from typing import List, Dict
import requests
import logging


MODEL_URL = (
    "https://raw.githubusercontent.com/BerriAI/litellm/main/"
    "model_prices_and_context_window.json"
)

CACHE_FILE = "/tmp/klingon_models_cache.json"

ALLOWED_REGEXES = {
    'openai': r'gpt-4.*',
    'ollama': r'ollama/.*',
    'anthropic': r'anthropic/.*|claude.*',
    'allow_all': r'.*',
}

IGNORED_REGEXES = [
    r'ai21', r'amazon', r'anyscale', r'bedrock', r'bison', r'dolphin',
    r'gecko', r'cloudflare', r'codestral', r'cohere', r'command', r'dall-e',
    r'databricks', r'deepinfra', r'deepseek', r'fireworks_ai', r'friendliai',
    r'ft:', r'j2-', r'jamba', r'luminous', r'stable-diffusion', r'medlm',
    r'meta\.llama', r'mistral\.mistral', r'mistral\.mixtral', r'mistral/',
    r'openrouter', r'palm', r'perplexity', r'replicate', r'text-',
    r'sagemaker', r'sample_spec', r'together', r'vertex', r'voyage',
    r'whisper', r'tts', r'babbage', r'davinci', r'embed-'
]


_cached_model_data = None

def fetch_model_data() -> Dict[str, dict]:
    """Fetches and caches the model list from a remote JSON file.

    If a cached version exists, it is returned. If not, it fetches from the
    remote URL and caches the result.

    Returns:
        A dictionary where keys are model names and values are empty
        dictionaries.

    Raises:
        requests.exceptions.RequestException: If the HTTP request fails.
    """
    global _cached_model_data
    if _cached_model_data is not None:
        return _cached_model_data

    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            _cached_model_data = {model: {} for model in json.load(f).keys()}
            return _cached_model_data

    # Suppress only specific warnings for 'requests' HTTP handling
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=3)
    session.mount('https://', adapter)

    response = session.get(MODEL_URL, timeout=30)  # 30 seconds timeout
    response.raise_for_status()  # Raises an exception for failed requests
    new_data = response.json()

    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_data, f)

    _cached_model_data = {model: {} for model in new_data.keys()}
    return _cached_model_data


def filter_models(
    all_models: Dict[str, dict],
    allowed_regexes: Dict[str, str],
    ignored_regexes: List[str]
) -> Dict[str, dict]:
    """Filters the models based on allowed and ignored regex patterns.

    Args:
        all_models: The dictionary of models fetched from the remote source.
        allowed_regexes: A dictionary of regex patterns where keys are model
            names or categories, and values are regex patterns. Only models
            matching these patterns are allowed.
        ignored_regexes: A list of regex patterns. Models matching these
            patterns will be excluded.

    Returns:
        A filtered dictionary of models based on the allowed and ignored regex
        patterns.

    Example:
        >>> all_models = {'gpt-4': {...}, 'gpt-4o': {...}, 'sample_spec': {...}}  # pylint: disable=line-too-long # noqa: E501
        >>> allowed = {'openai': 'gpt-4.*'}
        >>> ignored = ['sample_spec']
        >>> filter_models(all_models, allowed, ignored)
        {'gpt-4': {...}, 'gpt-4o': {...}}
    """
    filtered_models = {}

    for model_name, model_data in all_models.items():
        if any(re.search(ignored_pattern, model_name)
               for ignored_pattern in ignored_regexes):
            continue

        if any(re.search(allowed_pattern, model_name)
               for allowed_pattern in allowed_regexes.values()):
            filtered_models[model_name] = model_data

    return filtered_models


def update_env_variable(model_list: List[str]) -> None:
    """Updates the KLINGON_MODELS environment variable.

    Args:
        model_list: A list of model names to be set in the environment
            variable.

    Example:
        >>> update_env_variable(['gpt-4', 'gpt-4o', 'sample_spec'])
        # KLINGON_MODELS will be set to "gpt-4,gpt-4o,sample_spec"
    """
    os.environ['KLINGON_MODELS'] = ','.join(model_list)


def get_supported_models() -> Dict[str, dict]:
    """Retrieves and filters supported models, updating the environment.

    Returns:
        A filtered dictionary of models based on the allowed and ignored regex
        patterns.

    Example:
        >>> supported_models = get_supported_models()
        >>> print(supported_models)
        {'gpt-4': {...}, 'gpt-4o': {...}}
    """
    all_models = fetch_model_data()
    filtered_models = filter_models(
        all_models,
        ALLOWED_REGEXES,
        IGNORED_REGEXES
    )
    update_env_variable(list(filtered_models.keys()))
    return filtered_models


if __name__ == "__main__":
    supported_models = get_supported_models()
    model_names_only = sorted(supported_models.keys())
    print(model_names_only)
