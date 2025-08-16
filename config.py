# Konfiguracja FVMerger

# Domyślny okres pobierania
DEFAULT_PERIOD = "last_month"  # last_month, current_month, year, custom

# Custom daty (używane gdy period = custom)
CUSTOM_FROM = "2025/01/01"
CUSTOM_TO = "2025/12/31"

# Katalogi
TEMP_DIR = "attachments"
JPG_TEMP = "jpg_temp"

# Gmail
CLIENT_SECRET_FILE = "client_secret.json"

# Filtry wiadomości
EMAIL_FILTER = "-is:starred"  # dodatkowe filtry Gmail