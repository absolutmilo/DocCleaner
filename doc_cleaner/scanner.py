import os
import pathlib
from typing import List
from .config import ALLOWED_EXTENSIONS

def scan_folder(root_path: str) -> List[str]:
    """
    Recursively scans the root_path for files with allowed extensions.
    Returns a list of absolute file paths.
    """
    valid_files = []
    
    # Ensure root_path is absolute
    root_path = os.path.abspath(root_path)
    
    for root, dirs, files in os.walk(root_path):
        # Exclude internal folders if ever created inside source before scan finishes, 
        # though ideally output is created first. 
        # Exclude internal folders, hidden folders, and previous run outputs
        dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('__') and not d.startswith('DocCleaner_Run_')]
        
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in ALLOWED_EXTENSIONS:
                full_path = os.path.join(root, file)
                valid_files.append(full_path)
                
    return valid_files
