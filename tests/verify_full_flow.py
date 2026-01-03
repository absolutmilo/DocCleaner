import os
import shutil
import tempfile
import sys
import datetime
# Add root to sys path to import doc_cleaner
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from doc_cleaner import main, config

def verify_flow():
    print("Setting up test environment...")
    
    # Create temp root
    base_dir = tempfile.mkdtemp()
    source_dir = os.path.join(base_dir, "input_docs")
    os.makedirs(source_dir)
    
    # Mock Desktop/duplicated
    mock_files_dir = base_dir # temp root
    mock_desktop_duplicated = os.path.join(base_dir, "Desktop", "duplicated")
    # Patch config path
    config.DUPLICATED_FOLDER_PATH = mock_desktop_duplicated
    # Ensure it doesn't verify existence of real desktop
    
    print(f"Test Root: {base_dir}")
    print(f"Duplicated Path (Mock): {mock_desktop_duplicated}")
    
    # Create Dummy Files
    # 1. Procedimiento Word (Fake content)
    # Note: creating real .docx with text is complex without library usage in setup.
    # We will just write text files with correct extensions 
    # BUT content_reader depends on libs reading them. 
    # If content_reader fails, it returns empty metadata -> GENERIC topic.
    # To test classifier, we might need to mock content_reader OR create somewhat valid files/patch content_reader.
    # Let's patch content_reader.read_content for this test to avoid creating strict binary files.
    
    from doc_cleaner import content_reader
    
    original_read_content = content_reader.read_content
    
    def mock_read_content(path):
        fname = os.path.basename(path).lower()
        if "procedimiento" in fname:
            return {"title": "Manual de Calidad", "subtitle": "Procedimiento", "sample_text": "bla bla"}
        if "formato" in fname:
            return {"title": "", "subtitle": "", "sample_text": "este es un formato standard"}
        if "duplicate" in fname:
            return {"title": "Same Content", "subtitle": "", "sample_text": "duplicate content"}
        return {"title": "", "subtitle": "", "sample_text": ""}
        
    content_reader.read_content = mock_read_content
    
    # Create files
    # A. Procedure
    with open(os.path.join(source_dir, "old_procedimiento.docx"), 'w') as f:
        f.write("dummy docx content")
        
    # B. Format
    with open(os.path.join(source_dir, "formato_v1.xlsx"), 'w') as f:
        f.write("dummy xlsx content")
        
    # C. Duplicate 1
    with open(os.path.join(source_dir, "dup1.pdf"), 'w') as f:
        f.write("CONTENT_HASH_123")
        
    # D. Duplicate 2 (Different name)
    with open(os.path.join(source_dir, "dup2_copy.pdf"), 'w') as f:
        f.write("CONTENT_HASH_123")
        
    print("Files created. Running main...")
    
    # Mock sys.argv
    sys.argv = ["main.py", source_dir]
    
    try:
        main.main()
    except Exception as e:
        print(f"Main failed: {e}")
        # cleanup
        # shutil.rmtree(base_dir)
        raise e
        
    print("Main finished. Verifying results...")
    
    # Checks
    # 1. Duplicated folder should have 1 pdf
    if os.path.exists(mock_desktop_duplicated):
        dups = os.listdir(mock_desktop_duplicated)
        print(f"Duplicated folder content: {dups}")
        if len(dups) != 1:
            print("FAIL: Expected 1 duplicate file")
        else:
            print("PASS: Duplicate moved")
    else:
        print("FAIL: Duplicated folder not created")
        
    # 2. Output folder creation
    items_in_source = os.listdir(source_dir)
    run_folders = [d for d in items_in_source if d.startswith("DocCleaner_Run_")]
    if not run_folders:
        print("FAIL: No run output folder found")
        return
        
    run_path = os.path.join(source_dir, run_folders[0])
    print(f"Run folder: {run_path}")
    
    # 3. Structure check
    # We expect PROCEDIMIENTOS and FORMATOS folders
    expected_proc = os.path.join(run_path, "PROCEDIMIENTOS")
    expected_form = os.path.join(run_path, "FORMATOS")
    
    if os.path.exists(expected_proc) and os.path.exists(expected_form):
        print("PASS: Topic folders created")
    else:
        print(f"FAIL: Topic folders missing. Found: {os.listdir(run_path)}")
        
    # 4. JSON check
    if os.path.exists(os.path.join(run_path, "doccleaner_result_map.json")):
        print("PASS: Result map JSON found")
    else:
        print("FAIL: Result map JSON missing")
        
    # Cleanup
    shutil.rmtree(base_dir)
    print("Test Complete.")

if __name__ == "__main__":
    verify_flow()
