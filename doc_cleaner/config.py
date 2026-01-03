import os

# Allowed extensions (modern office formats + PDF)
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.pptx', '.xlsx'}

# Topic Keywords
TOPIC_KEYWORDS = {
    'FORMATO': ['formato', 'template', 'plantilla', 'formulario'],
    'PROCEDIMIENTO': ['procedimiento', 'procedure', 'instructivo', 'manual', 'guia'],
    'ACTA': ['acta', 'minutes', 'minuta', 'reunion', 'meeting'],
    'PROCESO': ['proceso', 'process', 'diagrama', 'flujo'],
}

# Topic Output Folders mapping
TOPIC_FOLDERS = {
    'FORMATO': 'FORMATOS',
    'PROCEDIMIENTO': 'PROCEDIMIENTOS',
    'ACTA': 'ACTAS',
    'PROCESO': 'PROCESOS',
    'GENERIC': 'OTROS',
}

# Date Formats
FOLDER_MONTH_FORMAT = "%b%Y"  # e.g. Ene2025 (implementation might need locale handling or custom map)
FILENAME_DATE_FORMAT = "%Y-%m-%d"

# Paths
# Defaults to User Desktop/duplicated. Can be overridden.
USER_HOME = os.path.expanduser("~")
DUPLICATED_FOLDER_PATH = os.path.join(USER_HOME, "Desktop", "duplicated")

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
