import json
import os
from typing import List, Dict, Any
from .config import TOPIC_FOLDERS

def generate_reports(results: List[Dict[str, Any]], output_path: str):
    """
    Generates JSON reports in the output_path:
    - doccleaner_result_map.json
    - doccleaner_organization_plan.json
    
    results: list of dicts with keys:
    original_path, current_path, topic, created_at, modified_at, is_duplicate
    (and optional hash, etc)
    """
    
    # 1. doccleaner_result_map.json
    map_file = os.path.join(output_path, "doccleaner_result_map.json")
    with open(map_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    # 2. doccleaner_organization_plan.json
    # Aggregate by Topic
    plan = {}
    
    for res in results:
        if res.get('is_duplicate'):
            continue
            
        topic = res.get('topic', 'GENERIC')
        final_path = res.get('current_path')
        
        # We want relative path from output_path for cleaner view?
        # Or just the full path. Spec says "PROCEDIMIENTOS/Ene2025/..." which implies relative structure
        try:
             rel_path = os.path.relpath(final_path, output_path)
        except ValueError:
            rel_path = final_path
            
        if topic not in plan:
            suggested_root = TOPIC_FOLDERS.get(topic, 'OTROS')
            plan[topic] = {
                "suggested_root": suggested_root,
                "files": []
            }
            
        plan[topic]["files"].append(rel_path)
        
    plan_file = os.path.join(output_path, "doccleaner_organization_plan.json")
    with open(plan_file, 'w', encoding='utf-8') as f:
         json.dump(plan, f, indent=2, ensure_ascii=False)
