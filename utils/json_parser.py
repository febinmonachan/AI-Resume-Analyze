import json
import re

def safe_parse_json(text):

    text = re.sub(r"```json", "", text)
    text = re.sub(r"```", "", text)

    text = text.strip()

    try:
        return json.loads(text)

    except json.JSONDecodeError:

        match = re.search(
            r'(\{.*\})',
            text,
            re.DOTALL
        )

        if match:

            try:
                return json.loads(
                    match.group(1)
                )

            except:
                return None

    return None
