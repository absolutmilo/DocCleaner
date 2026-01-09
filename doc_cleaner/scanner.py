import os
import pathlib
from typing import List
from .config import ALLOWED_EXTENSIONS

def scan_folder(root_path: str, recursive: bool = True) -> List[str]:
    """
    Scans the root_path for files with allowed extensions.
    recursive: if True, scans subdirectories. If False, only root_path.
    Returns a list of absolute file paths.
    """
    valid_files = []
    
    # Ensure root_path is absolute
    root_path = os.path.abspath(root_path)
    
    if recursive:
        # Recursive scan using walk
        for root, dirs, files in os.walk(root_path):
            # Exclude internal folders, hidden folders, and previous run outputs
            dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('__') and not d.startswith('DocCleaner_Run_')]
            
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in ALLOWED_EXTENSIONS:
                    full_path = os.path.join(root, file)
                    valid_files.append(full_path)
    else:
        # Non-recursive: just list the top directory
        try:
             # Manual listdir
             with os.scandir(root_path) as it:
                for entry in it:
                    if entry.is_file():
                        ext = os.path.splitext(entry.name)[1].lower()
                        if ext in ALLOWED_EXTENSIONS:
                            valid_files.append(entry.path)
        except OSError as e:
            print(f"Error checking directory {root_path}: {e}")

    return valid_files
