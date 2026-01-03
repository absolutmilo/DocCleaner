import os
import re
import datetime
from .config import FILENAME_DATE_FORMAT

def sanitize_filename(name: str) -> str:
    """
    Removes forbidden characters and normalizes spaces.
    """
    # Keep alphanumeric, dot, hyphens, underscores, spaces
    # Remove others
    name = re.sub(r'[^\w\s\.-]', '', name)
    # Replace multiple spaces with single space and strip
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def extract_version(base_name: str) -> tuple[str, str]:
    """
    Extracts version information from the end of the filename.
    Returns (clean_base_name_without_version, standardized_version_string).
    Example: "Reporte v2.1" -> ("Reporte", "_v2.1")
    """
    # Regex for common version patterns at the end of the string:
    # Matches: v1, v1.0, ver 2, version 3.5, -v1 (case insensitive)
    # The pattern explanation:
    # (?:[\s_.-]?) -> Optional separator (space, _, ., -)
    # (?:v|ver|version|versión) -> version keyword
    # [.\s]? -> Optional gap (dot or space)
    # (\d+(?:\.\d+)?) -> The version number (Integers or decimals like 1.0)
    # $ -> End of string
    pattern = r"(?:[\s_.-]?(?:v|ver|version|versión)[.\s]?(\d+(?:\.\d+)?))$"
    
    match = re.search(pattern, base_name, re.IGNORECASE)
    if match:
        version_num = match.group(1)
        # Verify it's not part of a bigger word (though separator check helps)
        # Extract base name up to the start of the match
        new_base = base_name[:match.start()].strip()
        
        # Remove trailing separators left over on new_base if any
        new_base = re.sub(r'[\s_.-]+$', '', new_base)
        
        return new_base, f"_v{version_num}"
        
    return base_name, ""

def generate_new_name(original_path: str, topic: str, date_obj: datetime.datetime) -> str:
    """
    Generates the new filename pattern: YYYY-MM-DD_TEMATICA_original-name_vX.ext
    """
    original_filename = os.path.basename(original_path)
    base, ext = os.path.splitext(original_filename)
    
    # 1. Extract Version
    base_no_version, version_suffix = extract_version(base)
    
    # 2. Sanitize base name
    clean_base = sanitize_filename(base_no_version)
    
    # Replace spaces with hyphens for the "higienizado" part
    clean_base = clean_base.replace(' ', '-')
    
    date_str = date_obj.strftime(FILENAME_DATE_FORMAT)
    
    # 3. Assemble: Date_Topic_Name_Version.ext
    new_name = f"{date_str}_{topic}_{clean_base}{version_suffix}{ext}"
    return new_name
