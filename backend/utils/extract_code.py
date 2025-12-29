import re

def extract_jav_code(title: str) -> str:
    match = re.search(r"([A-Z]{2,5})-?(\d{1,4})", title, re.IGNORECASE)
    if match:
        code = match.group(1).upper() + "-" + match.group(2)
        return code
    return title.upper()