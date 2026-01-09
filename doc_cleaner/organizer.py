import os
import shutil
import datetime
from .config import TOPIC_FOLDERS, get_month_folder_name

def create_output_structure(root_path: str, run_id: str, dry_run: bool = False) -> str:
    """
    Creates the main output folder for the run:
    root_path/DocCleaner_Run_<run_id>
    
    Returns the absolute path of the created run folder.
    """
    run_folder_name = f"DocCleaner_Run_{run_id}"
    run_folder_path = os.path.join(root_path, run_folder_name)
    
    if not dry_run and not os.path.exists(run_folder_path):
        os.makedirs(run_folder_path)
        
    return run_folder_path

def determine_destination(output_root: str, topic: str, date_obj: datetime.datetime) -> str:
    """
    Determines the full destination folder path:
    output_root / TOPIC_FOLDER / MonthYear
    """
    folder_name = TOPIC_FOLDERS.get(topic, TOPIC_FOLDERS.get('GENERIC', 'OTROS'))
    month_folder = get_month_folder_name(date_obj)
    
    full_path = os.path.join(output_root, folder_name, month_folder)
    return full_path

def move_file(source_path: str, dest_dir: str, new_name: str, dry_run: bool = False) -> str:
    """
    Moves the source file to dest_dir with new_name.
    Creates dest_dir if it doesn't exist.
    Returns the final absolute path.
    """
    if not dry_run and not os.path.exists(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)
        
    final_path = os.path.join(dest_dir, new_name)
    
    # Handle minor collision in output just in case (e.g. 2 files processed same second same name same topic)
    # Only check collision on disk if not dry_run, or if we want to simulate accurately we might need to track state.
    # For now, simplistic approach: if dry_run, assume no collision or just log it.
    
    counter = 1
    base, ext = os.path.splitext(new_name)
    
    # In dry run, we can't easily check 'os.path.exists' for FILES WE JUST 'MOVED' (simulated).
    # But we can check existing files.
    if not dry_run:
        while os.path.exists(final_path):
            final_path = os.path.join(dest_dir, f"{base}_{counter}{ext}")
            counter += 1
        shutil.move(source_path, final_path)
        
    return final_path
