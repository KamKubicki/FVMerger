# FVMerger

Automated invoice download and processing system for Gmail. The script downloads invoices from email attachments, converts images to PDF, and organizes files for sending to the accountant.

## ✨ Features

- 🗓️ **Configurable periods** - previous month, current month, entire year, or custom range
- 📄 **PDF and JPG support** - automatic conversion of invoice photos to PDF
- 📝 **Smart file naming** - automatic naming with date and sender
- 📊 **Collective preview** - single PDF file for quick review of all invoices
- 🔍 **Detailed logging** - complete information about the download process
- ⚙️ **Easy configuration** - all settings in config.py file

## 📋 Requirements

- Python 3.7+
- Gmail account with API enabled
- Internet access

## 🚀 Installation

### 1. Clone repository
```bash
git clone <repository-url>
cd FVMerger
```

### 2. Create virtual environment (recommended)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Gmail API Configuration

#### Step 1: Enable Gmail API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
5. Select "Desktop application"
6. Download JSON file and save as `client_secret.json` in project directory

#### Step 2: First run
```bash
python main.py
```
On first run, you'll be redirected to browser for Gmail access authorization.

## 📖 Usage

### Basic commands

```bash
# Default - previous month (perfect for sending to accountant by 10th of each month)
python main.py

# Current month
python main.py --period current_month

# Entire year
python main.py --period year

# Custom date range
python main.py --period custom --from 2025/01/01 --to 2025/03/31

# Help
python main.py --help
```

### Available periods

| Period | Description | Example usage |
|--------|-------------|---------------|
| `last_month` | Previous month (default) | Sending invoices to accountant |
| `current_month` | Current month | Checking invoices during the month |
| `year` | Entire year | Annual summary |
| `custom` | Custom range | Specific billing period |

## ⚙️ Configuration

Edit `config.py` file to customize settings:

```python
# Default download period
DEFAULT_PERIOD = "last_month"

# Directories
TEMP_DIR = "attachments"
JPG_TEMP = "jpg_temp"

# Gmail
CLIENT_SECRET_FILE = "client_secret.json"

# Message filters
EMAIL_FILTER = "-is:starred"
```

## 📁 File structure

```
FVMerger/
├── main.py              # Main script
├── config.py            # Configuration
├── requirements.txt     # Python dependencies
├── README.md           # This documentation
├── client_secret.json  # Gmail API keys (you must add)
├── attachments/        # Downloaded invoices (separate files)
│   ├── 2025-07-15_orlen_Invoice_F_1498K19.pdf
│   └── 2025-08-12_siemens_statement_invoice.pdf
├── jpg_temp/          # Temporary files (automatically cleaned)
└── attachments.pdf    # Collective PDF for preview
```

## 📋 Usage examples

### Monthly accountant routine
```bash
# At the beginning of the month, download invoices from previous month
python main.py

# Check collective file
# → attachments.pdf

# Send separate files from attachments/ directory to accountant
```

### Check invoices during the month
```bash
python main.py --period current_month
```

### Annual summary
```bash
python main.py --period year
```

### Specific period (e.g., quarter)
```bash
python main.py --period custom --from 2025/01/01 --to 2025/03/31
```

## 🔧 Troubleshooting

### Gmail authorization issues
```bash
# Remove old token and authorize again
rm gmail_token.json
python main.py
```

### "No module named..." error
```bash
# Check if virtual environment is active
pip install -r requirements.txt
```

### No invoices found
- Check if email contains PDF/JPG attachments
- Check filters in config.py (EMAIL_FILTER)
- Check date range

### JPG conversion issues
- Make sure JPG files are not corrupted
- Check if you have enough disk space

## 📊 Example output

```
2025-08-15 23:12:19,716 - INFO - Period: last_month
2025-08-15 23:12:19,716 - INFO - Searching messages from: 2025/07/01 to: 2025/08/01
2025-08-15 23:12:19,716 - INFO - Found 4 messages
2025-08-15 23:12:19,716 - INFO - Processing message 1 from ORLEN PAY <orlenpay@orlen.pl>
2025-08-15 23:12:19,716 - INFO - Saved PDF: 2025-07-15_orlenpay_Invoice_F_1920K19.pdf
...

Hello, I'm sending the following documents in the attachment:

	1. 2025-07-15_orlenpay_Invoice_F_1920K19_0980_25_Orlen_Pay.pdf
	2. 2025-08-12_siemens_2025-08-12_INVOICES_01849_08_25_SLMLO_256131.pdf

Best regards
Kamil Kubicki

--- SUMMARY ---
Period: last_month (2025/07/01 - 2025/08/01)
Files found: 2
Files are located in directory: attachments/
Collective PDF (for preview): attachments.pdf
```

## 🤝 Support

In case of problems:
1. Check "Troubleshooting" section
2. Run with `--help` to see all options
3. Check logs in console

## 📄 License

Project for personal use.