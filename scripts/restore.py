import json
import os
import shutil
import argparse
import sys

def restore_files(manifest_path, dry_run=False):
    if not os.path.exists(manifest_path):
        print(f"Error: Manifest file not found: {manifest_path}")
        return

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    print(f"Loaded manifest with {len(manifest)} entries.")
    
    restored_count = 0
    errors = 0

    for entry in manifest:
        original = entry.get('original_path')
        current = entry.get('current_path')
        
        if not original or not current:
            continue
            
        if original == current:
            continue
            
        # Check if current file exists (it should, unless moved again)
        if not os.path.exists(current):
            print(f"Warning: Current file not found: {current}. Skipping.")
            errors += 1
            continue
            
        # Check if original location is free
        if os.path.exists(original):
            print(f"Warning: Original location occupied: {original}. Skipping to prevent overwrite.")
            errors += 1
            continue
            
        try:
            if dry_run:
                print(f"[Dry Run] Restore: {current} -> {original}")
            else:
                # Ensure parent dir exists
                os.makedirs(os.path.dirname(original), exist_ok=True)
                shutil.move(current, original)
                print(f"Restored: {os.path.basename(original)}")
                restored_count += 1
        except Exception as e:
            print(f"Error restoring {current}: {e}")
            errors += 1
            
    print("-" * 30)
    print(f"Restore complete. Restored: {restored_count}, Errors/Skipped: {errors}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Restore files moved by DocCleaner using manifest.json")
    parser.add_argument("manifest", help="Path to manifest.json file")
    parser.add_argument("--dry-run", action="store_true", help="Simulate restoration")
    
    args = parser.parse_args()
    restore_files(args.manifest, args.dry_run)
