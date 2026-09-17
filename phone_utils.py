import re
from typing import Any, List, Dict
from dataclasses import dataclass, field

@dataclass
class ExtractionResult:
    mobile_numbers: List[str] = field(default_factory=list)
    tel_numbers: List[str] = field(default_factory=list)
    unknown_numbers: List[str] = field(default_factory=list)
    empty_count: int = 0
    na_count: int = 0

    @property
    def total_mobile_count(self) -> int:
        return len(self.mobile_numbers)

    @property
    def joined_mobile_numbers(self) -> str:
        return ",".join(self.mobile_numbers)

def clean_phone_number(val: Any) -> str:
    """
    Cleans and normalizes raw cell values into standard phone number string format.
    Handles float conversions (e.g. 9676775035.0), spaces, dashes, and international prefixes (+63 / 63).
    """
    if val is None:
        return ""
    
    val_str = str(val).strip()

    if val_str == "" or val_str.lower() in ("nan", "none"):
        return ""

    # Remove floating point artifact from Excel reading (e.g. "9676775035.0")
    if val_str.endswith(".0"):
        val_str = val_str[:-2]

    # Remove spaces, hyphens, dots, parentheses
    cleaned = re.sub(r'[\s\-\.\(\)]', '', val_str)

    # Normalize international Philippine prefix
    if cleaned.startswith("+63"):
        cleaned = "0" + cleaned[3:]
    elif cleaned.startswith("63") and len(cleaned) == 12:
        cleaned = "0" + cleaned[2:]
    
    # Handle numbers missing leading 0 (e.g. 9178346464 -> 09178346464)
    if len(cleaned) == 10 and cleaned.startswith("9"):
        cleaned = "0" + cleaned

    return cleaned

def categorize_phone_number(cleaned: str, raw_str: str = "") -> str:
    """
    Categorizes cleaned phone number into:
    - 'na': #N/A value
    - 'empty': blank value
    - 'mobile': 11 digits starting with '09'
    - 'landline': 10 digits
    - 'unknown': invalid/unrecognized format
    """
    if raw_str.upper() == "#N/A":
        return "na"
    if not cleaned:
        return "empty"
    
    if cleaned.isnumeric():
        if len(cleaned) == 11 and cleaned.startswith("09"):
            return "mobile"
        elif len(cleaned) == 10:
            return "landline"
    
    return "unknown"

def process_phone_numbers(raw_values: List[Any]) -> ExtractionResult:
    """
    Processes a list of raw cell values and extracts categorized phone numbers.
    """
    result = ExtractionResult()

    for val in raw_values:
        raw_str = str(val).strip() if val is not None else ""
        if raw_str == "" or raw_str.lower() in ("nan", "none"):
            result.empty_count += 1
            continue

        if raw_str.upper() == "#N/A":
            result.na_count += 1
            continue

        cleaned = clean_phone_number(val)
        category = categorize_phone_number(cleaned, raw_str)

        if category == "mobile":
            result.mobile_numbers.append(cleaned)
        elif category == "landline":
            result.tel_numbers.append(cleaned)
        elif category == "empty":
            result.empty_count += 1
        elif category == "na":
            result.na_count += 1
        else:
            result.unknown_numbers.append(cleaned if cleaned else raw_str)

    return result
