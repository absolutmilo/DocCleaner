import unittest
from doc_cleaner import classifier

class TestClassifier(unittest.TestCase):
    
    def test_generic_fallback(self):
        metadata = {"title": "Unknown", "subtitle": "", "sample_text": "nothing here"}
        self.assertEqual(classifier.classify_document(metadata), "GENERIC")
        
    def test_regex_boundary(self):
        # 'acta' should match 'acta', 'ACTA', 'Acta.'
        # Should NOT match 'impacta', 'lactancia'
        
        # Positive
        meta1 = {"title": "Esta es el Acta de reunion", "subtitle": "", "sample_text": ""}
        self.assertEqual(classifier.classify_document(meta1), "ACTA")
        
        # Negative
        meta2 = {"title": "Poliza de lactancia", "subtitle": "", "sample_text": "No debe confundirse"}
        # If lactancia contains 'acta', regex \bacta\b ensures no match.
        # Assuming ACTA keywords are ['acta', ...]. 
        # If it matched partial, it would return ACTA.
        self.assertEqual(classifier.classify_document(meta2), "GENERIC")

    def test_scoring_priority(self):
        # Suppose text has 1 FORMATO keyword and 2 PROCEDIMIENTO keywords.
        # It should be PROCEDIMIENTO.
        # FORMATO kw: 'formato'
        # PROCEDIMIENTO kw: 'procedimiento', 'manual'
        
        text = "Este es un formato de procedimiento manual para operaciones"
        # 'formato' -> 1 hit for FORMATO
        # 'procedimiento', 'manual' -> 2 hits for PROCEDIMIENTO
        
        meta = {"title": text, "subtitle": "", "sample_text": ""}
        self.assertEqual(classifier.classify_document(meta), "PROCEDIMIENTO")
