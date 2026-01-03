from typing import Dict, List
from .config import TOPIC_KEYWORDS

def classify_document(metadata: Dict[str, str]) -> str:
    """
    Classifies the document based on extracted metadata (title, subtitle, sample_text).
    Returns the detected topic key (e.g., 'PROCEDIMIENTO', 'FORMATO') or 'GENERIC'.
    """
    # Combine all text for search
    full_text = f"{metadata.get('title', '')} {metadata.get('subtitle', '')} {metadata.get('sample_text', '')}".lower()
    
    # Priority classification? Or simple check?
    # Spec says: "Combina title, subtitle y parte de sample_text en minúsculas. Aplica un conjunto de reglas basadas en palabras clave"
    
    # We iterate through config topics.
    # Note: Dictionary order is insertion order in modern Python, allowing priority if defined in order.
    # config.TOPIC_KEYWORDS should ideally be ordered by priority if overlaps exist.
    
    for topic, keywords in TOPIC_KEYWORDS.items():
        if topic == 'GENERIC': continue # Skip fallback in loop
        
        for kw in keywords:
            # Simple substring match. Could be enhanced with regex or word boundaries.
            if kw.lower() in full_text:
                return topic
                
    return "GENERIC"
