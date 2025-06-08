"""debug_pipeline_steps.py - Step-by-step pipeline debugger for Sluggi.

Prints the output after each step in the Sluggi pipeline for a given input string.
Useful for debugging and understanding transformations.

Example usage:
    python scripts/debug_pipeline_steps.py
"""

from sluggi.api import ReplacementConfig, ReplacementEngine, SlugPipeline


def debug_pipeline(text):
    """Print the output after each step in the Sluggi pipeline for the given
    input string.

    Args:
        text (str): The input string to process through the pipeline.

    Returns:
        str: The final output after all pipeline steps.

    """
    separator = "-"
    lowercase = True
    replacement_config = ReplacementConfig()
    engine = ReplacementEngine(replacement_config)
    config = {
        "separator": separator,
        "stopwords": None,
        "lowercase": lowercase,
        "word_regex": None,
        "decode_entities": True,
        "decode_decimal": True,
        "decode_hexadecimal": True,
        "max_length": None,
        "word_boundary": True,
        "process_emoji": True,
        "engine": engine,
        "replacement_config": replacement_config,
    }
    pipeline = SlugPipeline.default_pipeline(separator=separator, lowercase=lowercase)
    x = text
    print(f"Input: {x!r}")
    for i, step in enumerate(pipeline):
        x = step(x, config)
        print(f"After step {i+1} ({step.__name__}): {x!r}")
    return x


if __name__ == "__main__":
    debug_pipeline("Flags 🇺🇸🇯🇵")
