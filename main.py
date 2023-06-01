import os
import datetime
from fpdf import FPDF
from simplegmail import Gmail
from PyPDF2 import PdfMerger
from simplegmail.query import construct_query

# Utwórz obiekt Gmail i zaloguj się
gmail = Gmail("credentials.json")

# Utwórz ścieżkę do katalogu tymczasowego dla załączników
temp_dir = 'attachments'
jpg_temp = 'jpg_temp'
os.makedirs(temp_dir, exist_ok=True)
os.makedirs(jpg_temp, exist_ok=True)

# Pobierz wiadomości z bieżącego miesiąca
now = datetime.datetime.now()
start_date = now.replace(day=1, hour=0, minute=0, second=0)
end_date = (now + datetime.timedelta(days=1)).replace(day=1, hour=0, minute=0, second=0)
query = f'after:{start_date.strftime("%Y/%m/%d")} before:{end_date.strftime("%Y/%m/%d")}'
query_params_1 = {
    "after": "2023/5/01",
    "exact_phrase": "-is:starred"
}
# after:2023/4/20 before:2023/6/21
messages = gmail.get_messages(query=construct_query(query_params_1))

# Przygotuj listę plików załączników
attachments = []

# Przejdź przez każdą wiadomość
for message in messages:
    # Sprawdź, czy wiadomość ma załączniki
    if message.attachments:
        # Pobierz załączniki
        # Zapisz załączniki do plików tymczasowych
        for attachment in message.attachments:
            if attachment.filename.lower().endswith('.pdf'):
                file_path = os.path.join(temp_dir, attachment.filename.replace('/', '_'))
                attachment.save(file_path, overwrite=True)
                attachments.append(file_path)
            if attachment.filetype in 'image/jpg':
                pdf = FPDF()
                file_path = os.path.join(jpg_temp, attachment.filename.replace('/', '_'))
                attachment.save(file_path, overwrite=True)

                # Dodaj stronę do dokumentu
                pdf.add_page()

                # Wstaw obrazek
                pdf.image(file_path, x=10, y=10, w=100)
                pdf_path = os.path.join(temp_dir, attachment.filename.replace('.JPG', '.pdf'))
                pdf.output(pdf_path)
                attachments.append(pdf_path)

# Wygeneruj plik PDF z załączników
merger = PdfMerger()

for attachment in attachments:
    merger.append(attachment)

pdf_file = 'attachments.pdf'
merger.write(pdf_file)
merger.close()

print(f'Witam w załączniku przesyłam plik zbiorczy attachments.pdf zawierający następujące dokumenty:')
print()
for i, att in enumerate(attachments, start=1):
    print(f"\t{i}. {att.replace('attachments','')}")
print('')
print(f'Pozdrawiam \n\rKamil Kubicki')
