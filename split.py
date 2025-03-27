import os
import argparse
from typing import List, Tuple, Dict, Optional
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path
from tqdm import tqdm
import pandas as pd
import pdfplumber
import re
import shutil
from datetime import datetime

def find_input_files(folder_path: str) -> Tuple[str, str]:
    """Find PDF and Excel files in the specified folder."""
    pdf_file = next((f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')), None)
    excel_file = next((f for f in os.listdir(folder_path) if f.lower().endswith(('.xlsx', '.xls'))), None)
    
    if not pdf_file:
        raise FileNotFoundError("No PDF file found in the specified folder.")
    if not excel_file:
        raise FileNotFoundError("No Excel file found in the specified folder.")
    
    return pdf_file, excel_file

def parse_page_list(page_list: str) -> List[int]:
    """Parse page list string into a list of page numbers."""
    pages_to_extract = []
    for segment in page_list.split(','):
        segment = segment.strip()
        if '-' in segment:
            start_page, end_page = map(int, segment.split('-'))
            pages_to_extract.extend(range(start_page, end_page + 1))
        else:
            pages_to_extract.append(int(segment))
    return pages_to_extract

def split(folder_path: str, dpi: int = 100, create_images: bool = False) -> None:
    """Split PDF file into multiple PDFs based on Excel instructions."""
    pdf_file, excel_file = find_input_files(folder_path)
    material_path = os.path.join(folder_path, pdf_file)
    instructions_path = os.path.join(folder_path, excel_file)
    output_folder_pdfs = os.path.join(folder_path, 'PDFs')
    
    # Create output folders
    os.makedirs(output_folder_pdfs, exist_ok=True)
    if create_images:
        for folder in ['PNGs', 'JPEGs']:
            os.makedirs(os.path.join(folder_path, folder), exist_ok=True)

    print(f"Using PDF file: {pdf_file}")
    print(f"Using Excel file: {excel_file}")
    
    # Read instructions and load PDF
    instructions_df = pd.read_excel(instructions_path)
    instructions = instructions_df.values.tolist()
    reader = PdfReader(material_path)

    print(f"Processing {len(instructions)} instructions...")
    for unit_id, page_list in tqdm(instructions, desc="Processing Instructions", bar_format="{l_bar}{bar}"):
        page_list = str(page_list).strip()
        if not page_list:
            continue

        pages_to_extract = parse_page_list(page_list)
        writer = PdfWriter()

        # Add pages to new PDF
        for page_num in pages_to_extract:
            if page_num - 1 < len(reader.pages):
                writer.add_page(reader.pages[page_num - 1])
            else:
                print(f"Warning: Page number {page_num} is out of range in the original PDF.")

        # Save PDF
        output_pdf_path = os.path.join(output_folder_pdfs, f'{unit_id}.pdf')
        with open(output_pdf_path, 'wb') as output_pdf:
            writer.write(output_pdf)

        # Convert to images if requested
        if create_images:
            pages = convert_from_path(output_pdf_path, dpi=dpi)
            for i, page in enumerate(pages):
                for ext, folder in [('png', 'PNGs'), ('jpeg', 'JPEGs')]:
                    output_path = os.path.join(folder_path, folder, f'{unit_id}_page_{i + 1}.{ext}')
                    page.save(output_path, ext.upper())

    print("PDFs have been successfully split and saved.")
    if create_images:
        print("PNGs and JPEGs have been successfully created.")

def clean_value(value: str) -> str:
    """Remove whitespace from a value."""
    if isinstance(value, str):
        return re.sub(r'\s+', '', value)
    return value

def extract_details(pdf_path: str) -> Dict[str, str]:
    """Extract details from a PDF file."""
    details = {
        'Bedrooms': '',
        'BUA': '',
        'Covered Terrace': '',
        'Uncovered Terrace': ''
    }

    with pdfplumber.open(pdf_path) as pdf:
        full_text = " ".join(page.extract_text() for page in pdf.pages)

    patterns = {
        'Bedrooms': r'Bedrooms\s*[:\-]?\s*([\d]+)',
        'BUA': r'BUA\s*[:\-]?\s*([\d\s,]+(?:\.\d+)?)\s*(?:sqm|m²|square\s*meters)?',
        'Covered Terrace': r'Covered\s*Terrace\s*[:\-]?\s*([\d\s,]+(?:\.\d+)?)\s*(?:sqm|m²)?',
        'Uncovered Terrace': r'Uncovered\s*Terrace\s*[:\-]?\s*([\d\s,]+(?:\.\d+)?)\s*(?:sqm|m²)?'
    }

    for key, pattern in patterns.items():
        if match := re.search(pattern, full_text, re.IGNORECASE):
            details[key] = match.group(1).strip()

    if not details['BUA']:
        if match := re.search(r'(\d+[\d\s,]*\d*)\s*(sqm|SQM|m²)', full_text, re.IGNORECASE):
            details['BUA'] = match.group(1).strip()

    return details

def extract_data(folder_path: str) -> None:
    """Extract data from PDFs and save to Excel."""
    print("Extracting Data..")
    output_file = os.path.join(folder_path, 'Extracted Data.xlsx')
    pdf_folder = os.path.join(folder_path, 'PDFs')
    
    if not os.path.exists(pdf_folder):
        raise FileNotFoundError(f"PDF folder not found at {pdf_folder}")

    columns = ['Unit ID', 'BUA', 'Bedrooms', 'Covered Terrace', 'Uncovered Terrace']
    data = []

    for pdf_filename in os.listdir(pdf_folder):
        if pdf_filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(pdf_folder, pdf_filename)
            unit_id = os.path.splitext(pdf_filename)[0]
            details = extract_details(pdf_path)
            details = {key: clean_value(value) for key, value in details.items()}
            data.append([unit_id, details['BUA'], details['Bedrooms'], 
                        details['Covered Terrace'], details['Uncovered Terrace']])

    df = pd.DataFrame(data, columns=columns)
    df = df.sort_values(by='Unit ID').reset_index(drop=True)
    df.to_excel(output_file, index=False)
    print(f"Extracted data has been saved to {output_file}")

def get_user_input(prompt: str) -> str:
    """Get yes/no input from user."""
    while True:
        response = input(f"\n{prompt} (y/n): ").lower()
        if response in ['y', 'yes', 'n', 'no']:
            return 'yes' if response in ['y', 'yes'] else 'no'
        print("Please answer with 'y' or 'n'")

def get_dpi() -> int:
    """Get DPI value from user."""
    while True:
        try:
            dpi = int(input("\nEnter DPI for image conversion (default: 100): ") or "100")
            if dpi > 0:
                return dpi
            print("DPI must be greater than 0")
        except ValueError:
            print("Please enter a valid number")

def create_zip_file(folder_path: str) -> None:
    """Create a zip file of the PDFs folder."""
    print("\nCreating zip file of PDFs folder...")
    pdfs_folder = os.path.join(folder_path, 'PDFs')
    parent_folder_name = os.path.basename(folder_path)
    zip_filename = f"{parent_folder_name}-PDFs.zip"
    zip_path = os.path.join(folder_path, zip_filename)
    
    try:
        shutil.make_archive(os.path.splitext(zip_path)[0], 'zip', pdfs_folder)
        print(f"Zip file created successfully: {zip_filename}")
    except Exception as e:
        print(f"Error creating zip file: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split a PDF, convert to images, and/or extract data.")
    parser.add_argument('folder_path', type=str, help='Folder path containing one PDF and one Excel file')
    args = parser.parse_args()

    print("\nWelcome to PDF Split Tool!")
    print("------------------------")
    
    create_images = get_user_input("Would you like to create PNG and JPEG images?")
    extract_data_choice = get_user_input("Would you like to extract data from the PDFs?")
    zip_pdfs = get_user_input("Would you like to create a zip file of the PDFs folder?")
    
    dpi = get_dpi() if create_images == 'yes' else 100

    print("\nStarting PDF splitting process...")
    split(args.folder_path, dpi=dpi, create_images=create_images == 'yes')

    if extract_data_choice == 'yes':
        print("\nExtracting data from PDFs...")
        extract_data(args.folder_path)

    if zip_pdfs == 'yes':
        create_zip_file(args.folder_path)

    print("\nProcess completed successfully!")
