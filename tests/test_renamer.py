import unittest
from doc_cleaner import renamer

class TestRenamerVersion(unittest.TestCase):
    
    def test_version_extraction(self):
        cases = [
            ("Manual v1", "Manual", "_v1"),
            ("Reporte version 2.0", "Reporte", "_v2.0"),
            ("Instructivo_ver3", "Instructivo", "_v3"),
            ("Documento-v12.5", "Documento", "_v12.5"),
            ("No Version Here", "No Version Here", ""),
            ("Titulo con v en medio", "Titulo con v en medio", ""),
            ("Final - versión 1", "Final", "_v1"),
            ("Nombre.Complejo.v1", "Nombre.Complejo", "_v1")
        ]
        
        for input_name, expected_base, expected_suffix in cases:
            base, suffix = renamer.extract_version(input_name)
            self.assertEqual(base, expected_base, f"Failed base extraction for {input_name}")
            self.assertEqual(suffix, expected_suffix, f"Failed suffix extraction for {input_name}")

if __name__ == '__main__':
    unittest.main()
