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

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_arguments():
    """Parsuj argumenty wiersza poleceń"""
    parser = argparse.ArgumentParser(description='FVMerger - pobieranie faktur z Gmail')
    parser.add_argument('--period', choices=['last_month', 'current_month', 'year', 'custom'], 
                       default=config.DEFAULT_PERIOD,
                       help='Okres pobierania faktur (domyślnie: last_month)')
    parser.add_argument('--from', dest='date_from', type=str,
                       help='Data początkowa (YYYY/MM/DD) - używane z --period custom')
    parser.add_argument('--to', dest='date_to', type=str,
                       help='Data końcowa (YYYY/MM/DD) - używane z --period custom')
    return parser.parse_args()

def get_date_range(period, date_from=None, date_to=None):
    """Zwraca zakres dat na podstawie wybranego okresu"""
    now = datetime.datetime.now()
    
    if period == 'last_month':
        # Poprzedni miesiąc
        if now.month == 1:
            start_date = datetime.datetime(now.year - 1, 12, 1)
        else:
            start_date = datetime.datetime(now.year, now.month - 1, 1)
        end_date = datetime.datetime(now.year, now.month, 1)
        
    elif period == 'current_month':
        # Bieżący miesiąc
        start_date = now.replace(day=1)
        end_date = now
        
    elif period == 'year':
        # Cały rok
        start_date = datetime.datetime(now.year, 1, 1)
        end_date = now
        
    elif period == 'custom':
        # Custom zakres
        if not date_from or not date_to:
            # Użyj dat z config.py jeśli nie podano argumentów
            date_from = config.CUSTOM_FROM
            date_to = config.CUSTOM_TO
        
        try:
            start_date = datetime.datetime.strptime(date_from, "%Y/%m/%d")
            end_date = datetime.datetime.strptime(date_to, "%Y/%m/%d")
        except ValueError:
            logging.error(f"Nieprawidłowy format daty. Użyj YYYY/MM/DD")
            raise
    
    return start_date, end_date

# Parsuj argumenty
args = parse_arguments()

# Utwórz obiekt Gmail i zaloguj się
gmail = Gmail(config.CLIENT_SECRET_FILE)

# Utwórz ścieżkę do katalogu tymczasowego dla załączników
temp_dir = config.TEMP_DIR
jpg_temp = config.JPG_TEMP
os.makedirs(temp_dir, exist_ok=True)
os.makedirs(jpg_temp, exist_ok=True)

# Pobierz zakres dat na podstawie argumentów
start_date, end_date = get_date_range(args.period, args.date_from, args.date_to)

# Przygotuj query dla Gmail
query_params_1 = {
    "after": start_date.strftime("%Y/%m/%d"),
    "before": end_date.strftime("%Y/%m/%d"),
    "exact_phrase": config.EMAIL_FILTER
}

logging.info(f"Okres: {args.period}")
logging.info(f"Szukam wiadomości od: {start_date.strftime('%Y/%m/%d')} do: {end_date.strftime('%Y/%m/%d')}")

messages = gmail.get_messages(query=construct_query(query_params_1))

# Przygotuj listę plików załączników
attachments = []

def sanitize_filename(filename):
    """Czyści nazwę pliku z niepożądanych znaków"""
    return filename.replace('/', '_').replace('\\', '_').replace(':', '_')

def get_better_filename(original_name, message_date, sender):
    """Tworzy lepszą nazwę pliku z datą i nadawcą"""
    if message_date:
        try:
            if isinstance(message_date, str):
                # Jeśli to string, użyj obecnej daty
                date_str = datetime.datetime.now().strftime("%Y-%m-%d")
            else:
                date_str = message_date.strftime("%Y-%m-%d")
        except:
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    else:
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    sender_clean = sender.split('@')[0] if '@' in sender else sender
    sender_clean = ''.join(c for c in sender_clean if c.isalnum() or c in '-_')[:20]
    
    name, ext = os.path.splitext(original_name)
    return f"{date_str}_{sender_clean}_{sanitize_filename(name)}{ext}"

# Przejdź przez każdą wiadomość
logging.info(f"Znaleziono {len(messages)} wiadomości")
for i, message in enumerate(messages, 1):
    if message.attachments:
        sender = message.sender if hasattr(message, 'sender') else 'unknown'
        msg_date = message.date if hasattr(message, 'date') else None
        
        logging.info(f"Przetwarzam wiadomość {i} od {sender}")
        
        for attachment in message.attachments:
            try:
                if attachment.filename.lower().endswith('.pdf'):
                    better_name = get_better_filename(attachment.filename, msg_date, sender)
                    file_path = os.path.join(temp_dir, better_name)
                    attachment.save(file_path, overwrite=True)
                    attachments.append(file_path)
                    logging.info(f"Zapisano PDF: {better_name}")
                    
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
                    logging.info(f"Konwertowano JPG na PDF: {better_name}")
                    
            except Exception as e:
                logging.error(f"Błąd przy przetwarzaniu załącznika {attachment.filename}: {e}")

# Generuj zbiorczy plik PDF (do podglądu)
if attachments:
    try:
        merger = PdfMerger()
        for attachment in attachments:
            merger.append(attachment)
        
        pdf_file = 'attachments.pdf'
        merger.write(pdf_file)
        merger.close()
        logging.info(f"Utworzono zbiorczy plik: {pdf_file}")
    except Exception as e:
        logging.error(f"Błąd przy tworzeniu zbiorcza PDF: {e}")
    
    # Wyczyść pliki tymczasowe JPG
    try:
        if os.path.exists(jpg_temp):
            shutil.rmtree(jpg_temp)
            os.makedirs(jpg_temp, exist_ok=True)
    except Exception as e:
        logging.warning(f"Nie udało się wyczyścić {jpg_temp}: {e}")

# Wygeneruj tekst do wysłania ksiegowej
print(f'Witam, w załączniku przesyłam następujące dokumenty:')
print()
for i, att in enumerate(attachments, start=1):
    filename = os.path.basename(att)
    print(f"\t{i}. {filename}")
print('')
print(f'Pozdrawiam')
print(f'Kamil Kubicki')
print()
print(f"--- PODSUMOWANIE ---")
print(f"Okres: {args.period} ({start_date.strftime('%Y/%m/%d')} - {end_date.strftime('%Y/%m/%d')})")
print(f"Znalezionych plików: {len(attachments)}")
print(f"Pliki znajdują się w katalogu: {temp_dir}/")
if attachments:
    print(f"Zbiorczy PDF (do podglądu): attachments.pdf")
else:
    print("Nie znaleziono żadnych załączników w podanym okresie.")
