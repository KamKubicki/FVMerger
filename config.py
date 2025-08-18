# FVMerger Configuration

# Default download period
DEFAULT_PERIOD = "last_month"  # last_month, current_month, year, custom

# Custom dates (used when period = custom)
CUSTOM_FROM = "2025/01/01"
CUSTOM_TO = "2025/12/31"

# Directories
TEMP_DIR = "attachments"
JPG_TEMP = "jpg_temp"

# Gmail
CLIENT_SECRET_FILE = "client_secret.json"

# Message filters
EMAIL_FILTER = "-is:starred"  # additional Gmail filters