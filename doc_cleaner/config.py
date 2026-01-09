import os
import json
import logging

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
USER_HOME = os.path.expanduser("~")

# Default Values (Fallbacks)
DEFAULT_CONFIG = {
    "allowed_extensions": [".pdf", ".docx", ".pptx", ".xlsx"],
    "topic_keywords": {
        "FORMATO": ["formato", "template", "plantilla", "formulario"],
        "PROCEDIMIENTO": ["procedimiento", "procedure", "instructivo", "manual", "guia"],
        "ACTA": ["acta", "minutes", "minuta", "reunion", "meeting"],
        "PROCESO": ["proceso", "process", "diagrama", "flujo"]
    },
    "topic_folders": {
        "FORMATO": "FORMATOS",
        "PROCEDIMIENTO": "PROCEDIMIENTOS",
        "ACTA": "ACTAS",
        "PROCESO": "PROCESOS",
        "GENERIC": "OTROS"
    },
    "folder_month_format": "%b%Y",
    "filename_date_format": "%Y-%m-%d"
}

def load_config():
    """Loads configuration from JSON file, falling back to defaults."""
    if not os.path.exists(CONFIG_PATH):
        logging.warning(f"Config file not found at {CONFIG_PATH}. Using defaults.")
        return DEFAULT_CONFIG.copy()
    
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading config file: {e}. Using defaults.")
        return DEFAULT_CONFIG.copy()

_config_data = load_config()

# Expose constants for compatibility
ALLOWED_EXTENSIONS = set(_config_data.get("allowed_extensions", DEFAULT_CONFIG["allowed_extensions"]))
TOPIC_KEYWORDS = _config_data.get("topic_keywords", DEFAULT_CONFIG["topic_keywords"])
TOPIC_FOLDERS = _config_data.get("topic_folders", DEFAULT_CONFIG["topic_folders"])
FOLDER_MONTH_FORMAT = _config_data.get("folder_month_format", DEFAULT_CONFIG["folder_month_format"])
FILENAME_DATE_FORMAT = _config_data.get("filename_date_format", DEFAULT_CONFIG["filename_date_format"])

# Derived Paths
# Allow overriding duplicated path via enviroment variable or keep default
DUPLICATED_FOLDER_PATH = os.environ.get("DOCCLEANER_DUPLICATED_PATH", os.path.join(USER_HOME, "Desktop", "duplicated"))

def get_month_folder_name(date_obj):
    """
    Returns folder name like 'Ene2025' or 'Jan2025' depending on locale.
    Ideally we want Spanish if the user context implies it.
    Simple manual mapping for Spanish months to ensure consistency without locale issues.
    """
    months = {
        1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
        7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
    }
    return f"{months[date_obj.month]}{date_obj.year}"
