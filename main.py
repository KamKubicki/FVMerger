import os
import datetime
import logging
import shutil
import argparse
from fpdf import FPDF
from simplegmail import Gmail
from PyPDF2 import PdfMerger
from simplegmail.query import construct_query
import config

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
DATE_FORMAT = "%Y/%m/%d"

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='FVMerger - download invoices from Gmail')
    parser.add_argument('--period', choices=['last_month', 'current_month', 'year', 'custom'], 
                       default=config.DEFAULT_PERIOD,
                       help='Download period (default: last_month)')
    parser.add_argument('--from', dest='date_from', type=str,
                       help='Start date (YYYY/MM/DD) - used with --period custom')
    parser.add_argument('--to', dest='date_to', type=str,
                       help='End date (YYYY/MM/DD) - used with --period custom')
    return parser.parse_args()

def get_date_range(period, date_from=None, date_to=None):
    """Returns date range based on selected period"""
    now = datetime.datetime.now()
    
    if period == 'last_month':
        # Previous month
        if now.month == 1:
            start_date = datetime.datetime(now.year - 1, 12, 1)
        else:
            start_date = datetime.datetime(now.year, now.month - 1, 1)
        end_date = datetime.datetime(now.year, now.month, 1)
        
    elif period == 'current_month':
        # Current month
        start_date = now.replace(day=1)
        end_date = now
        
    elif period == 'year':
        # Entire year
        start_date = datetime.datetime(now.year, 1, 1)
        end_date = now
        
    elif period == 'custom':
        # Custom range
        if not date_from or not date_to:
            # Use dates from config.py if no arguments provided
            date_from = config.CUSTOM_FROM
            date_to = config.CUSTOM_TO
        
        try:
            start_date = datetime.datetime.strptime(date_from, DATE_FORMAT)
            end_date = datetime.datetime.strptime(date_to, DATE_FORMAT)
        except ValueError:
            logging.error("Invalid date format. Use YYYY/MM/DD")
            raise
    
    return start_date, end_date

# Parse arguments
args = parse_arguments()

# Create Gmail object and authenticate
gmail = Gmail(config.CLIENT_SECRET_FILE)

# Create path to temporary directory for attachments
temp_dir = config.TEMP_DIR
jpg_temp = config.JPG_TEMP
os.makedirs(temp_dir, exist_ok=True)
os.makedirs(jpg_temp, exist_ok=True)

# Get date range based on arguments
start_date, end_date = get_date_range(args.period, args.date_from, args.date_to)

# Prepare Gmail query
query_params_1 = {
    "after": start_date.strftime(DATE_FORMAT),
    "before": end_date.strftime(DATE_FORMAT),
    "exact_phrase": config.EMAIL_FILTER
}

logging.info(f"Period: {args.period}")
logging.info(f"Searching messages from: {start_date.strftime(DATE_FORMAT)} to: {end_date.strftime(DATE_FORMAT)}")

messages = gmail.get_messages(query=construct_query(query_params_1))

# Prepare list of attachment files
attachments = []

def sanitize_filename(filename):
    """Cleans filename from unwanted characters"""
    return filename.replace('/', '_').replace('\\', '_').replace(':', '_')

def get_better_filename(original_name, message_date, sender):
    """Creates better filename with date and sender"""
    if message_date:
        try:
            if isinstance(message_date, str):
                # If it's a string, use current date
                date_str = datetime.datetime.now().strftime("%Y-%m-%d")
            else:
                date_str = message_date.strftime("%Y-%m-%d")
        except (AttributeError, TypeError):
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    else:
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    sender_clean = sender.split('@')[0] if '@' in sender else sender
    sender_clean = ''.join(c for c in sender_clean if c.isalnum() or c in '-_')[:20]
    
    name, ext = os.path.splitext(original_name)
    return f"{date_str}_{sender_clean}_{sanitize_filename(name)}{ext}"

# Process each message
logging.info(f"Found {len(messages)} messages")
for i, message in enumerate(messages, 1):
    if message.attachments:
        sender = message.sender if hasattr(message, 'sender') else 'unknown'
        msg_date = message.date if hasattr(message, 'date') else None
        
        logging.info(f"Processing message {i} from {sender}")
        
        for attachment in message.attachments:
            try:
                if attachment.filename.lower().endswith('.pdf'):
                    better_name = get_better_filename(attachment.filename, msg_date, sender)
                    file_path = os.path.join(temp_dir, better_name)
                    attachment.save(file_path, overwrite=True)
                    attachments.append(file_path)
                    logging.info(f"Saved PDF: {better_name}")
                    
                elif attachment.filetype == 'image/jpeg' or attachment.filename.lower().endswith(('.jpg', '.jpeg')):
                    pdf = FPDF()
                    temp_img_path = os.path.join(jpg_temp, sanitize_filename(attachment.filename))
                    attachment.save(temp_img_path, overwrite=True)

                    pdf.add_page()
                    pdf.image(temp_img_path, x=10, y=10, w=100)
                    
                    better_name = get_better_filename(attachment.filename.replace('.jpg', '.pdf').replace('.JPG', '.pdf'), msg_date, sender)
                    pdf_path = os.path.join(temp_dir, better_name)
                    pdf.output(pdf_path)
                    attachments.append(pdf_path)
                    logging.info(f"Converted JPG to PDF: {better_name}")
                    
            except (OSError, IOError, ValueError) as e:
                logging.error(f"Error processing attachment {attachment.filename}: {e}")

# Generate collective PDF file (for preview)
if attachments:
    try:
        merger = PdfMerger()
        for attachment in attachments:
            merger.append(attachment)
        
        pdf_file = 'attachments.pdf'
        merger.write(pdf_file)
        merger.close()
        logging.info(f"Created collective file: {pdf_file}")
    except (OSError, IOError) as e:
        logging.error(f"Error creating collective PDF: {e}")
    
    # Clean temporary JPG files
    try:
        if os.path.exists(jpg_temp):
            shutil.rmtree(jpg_temp)
            os.makedirs(jpg_temp, exist_ok=True)
    except (OSError, IOError) as e:
        logging.warning(f"Failed to clean {jpg_temp}: {e}")

# Generate text for sending to accountant
print("Hello, I\'m sending the following documents in the attachment:")
print()
for i, att in enumerate(attachments, start=1):
    filename = os.path.basename(att)
    print(f"\t{i}. {filename}")
print('')
print('Best regards')
print('Kamil Kubicki')
print()
print("--- SUMMARY ---")
print(f"Period: {args.period} ({start_date.strftime(DATE_FORMAT)} - {end_date.strftime(DATE_FORMAT)})")
print(f"Files found: {len(attachments)}")
print(f"Files are located in directory: {temp_dir}/")
if attachments:
    print("Collective PDF (for preview): attachments.pdf")
else:
    print("No attachments found in the specified period.")
