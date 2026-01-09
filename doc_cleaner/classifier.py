import re
from typing import Dict, List
from .config import TOPIC_KEYWORDS

def classify_document(metadata: Dict[str, str]) -> str:
    """
    Classifies the document based on extracted metadata (title, subtitle, sample_text).
    Returns the detected topic key (e.g., 'PROCEDIMIENTO', 'FORMATO') or 'GENERIC'.
    Uses a scoring system with regex word boundary checks.
    """
    # Combine all text for search
    full_text = f"{metadata.get('title', '')} {metadata.get('subtitle', '')} {metadata.get('sample_text', '')}".lower()
    
    scores = {topic: 0 for topic in TOPIC_KEYWORDS.keys()}
    
    for topic, keywords in TOPIC_KEYWORDS.items():
        if topic == 'GENERIC': continue 
        
        for kw in keywords:
            # Escape keyword just in case, though currently they are simple words
            pattern = r'\b' + re.escape(kw.lower()) + r'\b'
            matches = re.findall(pattern, full_text)
            scores[topic] += len(matches)
            
    # Find topic with highest score
    best_topic = 'GENERIC'
    max_score = 0
    
    for topic, score in scores.items():
        if score > max_score:
            max_score = score
            best_topic = topic
            
    return best_topic
