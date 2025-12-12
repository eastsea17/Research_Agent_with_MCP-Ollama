import json
import re
from typing import Any, Optional

def extract_json(text: str) -> Optional[Any]:
    """
    Extracts JSON object or array from text.
    Handles Markdown code blocks and raw JSON strings.
    """
    try:
        # 1. Try to find content within ```json ... ``` or ``` ... ```
        pattern = r"```(?:json)?\s*(.*?)```"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            json_str = match.group(1).strip()
            return json.loads(json_str)
        
        # 2. Try to find the first outer-most [...] or {...}
        # Simple heuristic: find first [ or { and last ] or }
        list_start = text.find('[')
        dict_start = text.find('{')
        
        start_idx = -1
        end_char = ''
        
        if list_start != -1 and (dict_start == -1 or list_start < dict_start):
            start_idx = list_start
            end_char = ']'
        elif dict_start != -1:
            start_idx = dict_start
            end_char = '}'
            
        if start_idx != -1:
            end_idx = text.rfind(end_char)
            if end_idx != -1 and end_idx > start_idx:
                json_str = text[start_idx : end_idx + 1]
                return json.loads(json_str)

        # 3. Last fallback: try parsing the whole text
        return json.loads(text)

    except json.JSONDecodeError:
        return None
    except Exception as e:
        print(f"JSON Parsing Error: {e}")
        return None
