import json
import re


def parse_json_from_gemini(json_str: str):
    """Parses a dictionary from a JSON-like object string.

    Args:
      json_str: A string representing a JSON-like object, e.g.:
        ```json
        {
          "key1": "value1",
          "key2": "value2"
        }
        ```

    Returns:
      A dictionary representing the parsed object, or None if parsing fails.
    """

    try:
        # Remove potential leading/trailing whitespace
        json_str = json_str.strip()

        # Extract JSON content from triple backticks and "json" language specifier
        json_match = re.search(r"```json\s*(.*?)\s*```", json_str, re.DOTALL)

        if json_match:
            json_str = json_match.group(1)

        return json.loads(json_str)
    except (json.JSONDecodeError, AttributeError):
        return None