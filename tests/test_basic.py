import unittest
import os
import shutil
import tempfile
from doc_cleaner import scanner, duplicates, config

class TestDocCleanerBasic(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.dup_dir = tempfile.mkdtemp()
        
        # Override config path for testing
        config.DUPLICATED_FOLDER_PATH = self.dup_dir
        
    def tearDown(self):
        shutil.rmtree(self.test_dir)
        shutil.rmtree(self.dup_dir)
        
    def create_dummy_file(self, filename, content="test content"):
        path = os.path.join(self.test_dir, filename)
        with open(path, 'w') as f:
            f.write(content)
        return path
        
    def test_scanner(self):
        self.create_dummy_file("test1.docx")
        self.create_dummy_file("test2.pdf")
        self.create_dummy_file("ignore.txt")
        
        files = scanner.scan_folder(self.test_dir)
        self.assertEqual(len(files), 2)
        extensions = sorted([os.path.splitext(f)[1] for f in files])
        self.assertEqual(extensions, ['.docx', '.pdf'])

    def test_duplicates(self):
        # Create original
        p1 = self.create_dummy_file("original.docx", "CONTENT_A")
        # Create duplicate
        p2 = self.create_dummy_file("copy.docx", "CONTENT_A")
        # Create distinct
        p3 = self.create_dummy_file("unique.docx", "CONTENT_B")
        
        files = [p1, p2, p3]
        results = duplicates.process_duplicates(files)
        
        # We expect 3 results
        self.assertEqual(len(results), 3)
        
        # Count duplicates
        dups = [r for r in results if r['is_duplicate']]
        self.assertEqual(len(dups), 1)
        self.assertEqual(dups[0]['original_path'], p2) 
        # Note: logic relies on order passed. if p1 is first, p1 is org.
        
        # Verify p2 moved to duplicated folder
        self.assertTrue(os.path.exists(os.path.join(self.dup_dir, "copy.docx")))
        self.assertFalse(os.path.exists(p2))

if __name__ == '__main__':
    unittest.main()
