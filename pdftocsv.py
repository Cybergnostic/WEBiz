import pdfplumber
import csv

# Step 1: Extract the table from all pages of the PDF using pdfplumber
pdf_file_path = "sifre_dg.pdf"

all_tables = []
with pdfplumber.open(pdf_file_path) as pdf:
    for page in pdf.pages:
        # Extract tables from each page
        tables = page.extract_tables()
        all_tables.extend(tables)

# Step 2: Process the extracted data (optional)
# Depending on your table's structure, you may need to clean and process the data here

# Step 3: Write data to CSV
csv_file_path = "dg.csv"

with open(csv_file_path, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    for table in all_tables:
        for row in table:
            writer.writerow(row)

print("Table has been successfully converted to CSV.")
