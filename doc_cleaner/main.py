import os
import sys
import datetime
import argparse
import logging
from . import scanner, duplicates, content_reader, classifier, renamer, organizer, exporter

def get_file_dates(path):
    """Returns created and modified dates as ISO 8601 strings and a datetime object for renaming (using modified)."""
    stats = os.stat(path)
    created = datetime.datetime.fromtimestamp(stats.st_ctime)
    modified = datetime.datetime.fromtimestamp(stats.st_mtime)
    
    # Use modified date for organization/renaming by default as it's often more stable than creation on Windows copy
    # user spec says "creación o última modificación", can implement option. Defaulting to modified.
    ref_date = modified 
    
    return created.isoformat(), modified.isoformat(), ref_date

def main():
    parser = argparse.ArgumentParser(description="DocCleaner: Intelligent Document Organization")
    parser.add_argument("folder", help="Root input folder to clean")
    args = parser.parse_args()
    
    root_path = os.path.abspath(args.folder)
    
    if not os.path.exists(root_path):
        print(f"Error: Folder does not exist: {root_path}")
        return

    print(f"Starting DocCleaner on: {root_path}")
    
    # 1. Create Output Structure
    run_timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_root = organizer.create_output_structure(root_path, run_timestamp)
    print(f"Output folder created: {output_root}")
    
    # Setup Logging
    log_dir = os.path.join(output_root, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "doccleaner.log")
    
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        encoding='utf-8'
    )
    logging.info(f"Started execution on {root_path}")
    
    # 2. Scan
    print("Scanning files...")
    all_files = scanner.scan_folder(root_path)
    print(f"Found {len(all_files)} files with allowed extensions.")
    
    # 3. Detect Duplicates
    print("Detecting duplicates...")
    dup_results = duplicates.process_duplicates(all_files)
    
    # 4. Process Non-duplicates
    final_results = []
    
    moved_dups = 0
    processed_count = 0
    
    for item in dup_results:
        original_path = item['original_path']
        is_dup = item['is_duplicate']
        
        # Determine timestamps for report
        try:
             created_iso, modified_iso, ref_date = get_file_dates(original_path)
        except FileNotFoundError:
             # File might have been moved if it was a duplicate?
             # If it was duplicate, duplicates module moved it. 
             # So we check final_path or original depending on state.
             if is_dup and item.get('final_path'):
                  created_iso, modified_iso, ref_date = get_file_dates(item['final_path'])
             else:
                  # Should not happen if non-dup
                  created_iso, modified_iso, ref_date = "", "", datetime.datetime.now()

        res_entry = {
            "original_path": original_path,
            "created_at": created_iso,
            "modified_at": modified_iso,
            "is_duplicate": is_dup,
            "topic": None,
            "current_path": item.get('final_path', original_path)
        }
        
        if is_dup:
            moved_dups += 1
            final_results.append(res_entry)
            msg = f"Duplicate found: {os.path.basename(original_path)} -> Moved to duplicated folder"
            print(msg)
            logging.info(msg)
            continue
            
        # Non-duplicate processing
        try:
            print(f"Processing: {os.path.basename(original_path)}")
            
            # Read Content
            metadata = content_reader.read_content(original_path)
            
            # Classify
            topic = classifier.classify_document(metadata)
            res_entry['topic'] = topic
            
            if topic == 'GENERIC':
                logging.warning(f"Classified as GENERIC (Edge Case): {original_path} - Metadata found: {metadata}")
            
            # Rename
            new_name = renamer.generate_new_name(original_path, topic, ref_date)
            
            # Organize
            dest_dir = organizer.determine_destination(output_root, topic, ref_date)
            final_path = organizer.move_file(original_path, dest_dir, new_name)
            
            res_entry['current_path'] = final_path
            final_results.append(res_entry)
            processed_count += 1
            
        except Exception as e:
            msg = f"Error processing {original_path}: {e}"
            print(msg)
            logging.error(msg, exc_info=True)
            res_entry['error'] = str(e)
            res_entry['current_path'] = original_path # Not moved
            final_results.append(res_entry)
        
    # 5. Export
    exporter.generate_reports(final_results, output_root)
    
    # Summary
    print("\n" + "="*40)
    print("DocCleaner Execution Complete")
    print("="*40)
    print(f"Total files scanned: {len(all_files)}")
    print(f"Duplicates moved: {moved_dups}")
    print(f"Files organized: {processed_count}")
    print(f"Output location: {output_root}")
    print("="*40)

if __name__ == "__main__":
    main()
