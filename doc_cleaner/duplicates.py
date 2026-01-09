import os
import hashlib
import shutil
from typing import List, Dict, Any
from . import config

def get_file_hash(file_path: str) -> str:
    """
    Calculates SHA256 hash of a file.
    """
    hasher = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(65536)
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()
    except OSError:
        return "" # Should handle gracefully by skipping or logging

def move_to_duplicated(file_path: str, dry_run: bool = False) -> str:
    """
    Moves a file to the configured DUPLICATED_FOLDER_PATH.
    Creates the folder if it doesn't exist.
    Handles name collisions in destination by appending count.
    Returns the new absolute path of the moved file.
    """
    if not dry_run and not os.path.exists(config.DUPLICATED_FOLDER_PATH):
        os.makedirs(config.DUPLICATED_FOLDER_PATH, exist_ok=True)
        
    filename = os.path.basename(file_path)
    dest_path = os.path.join(config.DUPLICATED_FOLDER_PATH, filename)
    
    # Handle collision if file with same name already exists in duplicated
    counter = 1
    base, ext = os.path.splitext(filename)
    
    # Check collision against existing files on disk
    if not dry_run:
        while os.path.exists(dest_path):
            dest_path = os.path.join(config.DUPLICATED_FOLDER_PATH, f"{base}_{counter}{ext}")
            counter += 1
        shutil.move(file_path, dest_path)
        
    return dest_path

def process_duplicates(file_paths: List[str], dry_run: bool = False) -> List[Dict[str, Any]]:
    """
    Identifies and moves duplicates.
    Grouping is done by file extension first (comparing strictly same types).
    Returns a list of result dictionaries for ALL files:
    [
        {
            "original_path": str,
            "hash": str,
            "is_duplicate": bool,
            "final_path": str (moved path if duplicate, else None/original),
            "error": str (optional)
        },
        ...
    ]
    """
    results = []
    
    # Group by extension
    files_by_ext = {}
    for p in file_paths:
        ext = os.path.splitext(p)[1].lower()
        if ext not in files_by_ext:
            files_by_ext[ext] = []
        files_by_ext[ext].append(p)
    
    # Process each extension group
    for ext, paths in files_by_ext.items():
        seen_hashes = {} # hash -> original_path
        
        for path in paths:
            file_hash = get_file_hash(path)
            
            if not file_hash:
                # Failed to read
                results.append({
                    "original_path": path,
                    "hash": None,
                    "is_duplicate": False,
                    "final_path": path,
                    "error": "ReadFailed"
                })
                continue
            
            if file_hash in seen_hashes:
                # It's a duplicate
                try:
                    new_path = move_to_duplicated(path, dry_run=dry_run)
                    results.append({
                        "original_path": path,
                        "hash": file_hash,
                        "is_duplicate": True,
                        "final_path": new_path
                    })
                except Exception as e:
                     results.append({
                        "original_path": path,
                        "hash": file_hash,
                        "is_duplicate": True, # It IS a duplicate but failed to move
                        "final_path": path,
                        "error": str(e)
                    })
            else:
                # New unique file (for this extension)
                seen_hashes[file_hash] = path
                results.append({
                    "original_path": path,
                    "hash": file_hash,
                    "is_duplicate": False,
                    "final_path": path
                })
                
    return results
