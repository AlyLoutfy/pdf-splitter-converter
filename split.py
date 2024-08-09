import os
import argparse
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path
from tqdm import tqdm
import pandas as pd
import pdfplumber
import re

def split(folder_path, dpi=100):
    material_path = os.path.join(folder_path, 'Material.pdf')
    instructions_path = os.path.join(folder_path, 'Instructions.xlsx')
    output_folder_pdfs = os.path.join(folder_path, 'PDFs')
    output_folder_pngs = os.path.join(folder_path, 'PNGs')
    output_folder_jpegs = os.path.join(folder_path, 'JPEGs')

    # Create the output folders if they don't exist
    os.makedirs(output_folder_pdfs, exist_ok=True)
    os.makedirs(output_folder_pngs, exist_ok=True)
    os.makedirs(output_folder_jpegs, exist_ok=True)
    
    # Read the instructions from Excel
    instructions_df = pd.read_excel(instructions_path)
    instructions = instructions_df.values.tolist()

    # Load the original PDF
    reader = PdfReader(material_path)

    # Initialize progress tracking
    total_instructions = len(instructions)
    print(f"Processing {total_instructions} instructions...")

    for idx, (unit_id, page_list) in enumerate(tqdm(instructions, desc="Processing Instructions", bar_format="{l_bar}{bar}")):
        page_list = str(page_list).strip()
        if not page_list:
            continue  # Skip empty lines

        # Parse page list which can contain ranges, specific pages, or a single page
        pages_to_extract = set()
        for segment in page_list.split(','):
            if '-' in segment:
                # Handle page range
                start_page, end_page = map(int, segment.split('-'))
                pages_to_extract.update(range(start_page, end_page + 1))
            else:
                # Handle specific pages or single page
                pages_to_extract.add(int(segment))

        # Create a new PDF writer
        writer = PdfWriter()

        # Add the specified pages to the new PDF
        for page_num in sorted(pages_to_extract):
            if page_num - 1 < len(reader.pages):
                writer.add_page(reader.pages[page_num - 1])  # Page numbers in PdfReader are zero-indexed
            else:
                print(f"Warning: Page number {page_num} is out of range in the original PDF.")

        # Save the new PDF
        output_pdf_path = os.path.join(output_folder_pdfs, f'{unit_id}.pdf')
        with open(output_pdf_path, 'wb') as output_pdf:
            writer.write(output_pdf)

        # Convert the new PDF to PNG and JPEG images
        pages = convert_from_path(output_pdf_path, dpi=dpi)
        for i, page in enumerate(pages):
            output_png_path = os.path.join(output_folder_pngs, f'{unit_id}_page_{i + 1}.png')
            output_jpeg_path = os.path.join(output_folder_jpegs, f'{unit_id}_page_{i + 1}.jpeg')
            page.save(output_png_path, 'PNG')
            page.save(output_jpeg_path, 'JPEG')

    print("PDFs, PNGs, and JPEGs have been successfully split and saved.")

def clean_value(value):
    """Remove whitespace from a value."""
    if isinstance(value, str):
        return re.sub(r'\s+', '', value)
    return value

def extract_data(folder_path):
    output_file = os.path.join(folder_path, 'Extracted Data.xlsx')

    # Initialize DataFrame
    columns = ['Unit ID', 'BUA', 'Bedrooms', 'Covered Terrace', 'Uncovered Terrace']
    df = pd.DataFrame(columns=columns)

    def extract_details(pdf_path):
        details = {
            'Bedrooms': '',
            'BUA': '',
            'Covered Terrace': '',
            'Uncovered Terrace': ''
        }

        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                full_text += page.extract_text()

        # Define regex patterns to find the details
        patterns = {
            'Bedrooms': r'Bedrooms\s*[:\-]?\s*([\d]+)',
            'BUA': r'BUA\s*[:\-]?\s*([\d\s,]+(?:\.\d+)?)\s*(?:sqm|m²|square\s*meters)?',
            'Covered Terrace': r'Covered\s*Terrace\s*[:\-]?\s*([\d\s,]+(?:\.\d+)?)\s*(?:sqm|m²)?',
            'Uncovered Terrace': r'Uncovered\s*Terrace\s*[:\-]?\s*([\d\s,]+(?:\.\d+)?)\s*(?:sqm|m²)?'
        }

        # Search for patterns and extract details
        for key, pattern in patterns.items():
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                details[key] = match.group(1).strip()

        return details

    for pdf_filename in os.listdir(os.path.join(folder_path, 'PDFs')):
        if pdf_filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(folder_path, 'PDFs', pdf_filename)
            unit_id = os.path.splitext(pdf_filename)[0]
            details = extract_details(pdf_path)

            # Clean data
            details = {key: clean_value(value) for key, value in details.items()}

            # Append data to DataFrame
            df = pd.concat([df, pd.DataFrame([[unit_id, details['BUA'], details['Bedrooms'], details['Covered Terrace'], details['Uncovered Terrace']]], columns=columns)], ignore_index=True)

    # Sort DataFrame alphabetically by Unit ID
    df = df.sort_values(by='Unit ID').reset_index(drop=True)

    # Save DataFrame to Excel
    df.to_excel(output_file, index=False)
    print(f"Extracted data has been saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split a PDF, convert to images, and/or extract data.")
    parser.add_argument('folder_path', type=str, help='Folder path containing Material.pdf and Instructions.xlsx')
    parser.add_argument('--dpi', type=int, default=100, help='DPI for converting PDFs to images')
    parser.add_argument('--action', choices=['split', 'extract', 'both'], default='both', help='Action to perform: split only, extract only, or both')
    args = parser.parse_args()

    if args.action in ['split', 'both']:
        split(args.folder_path, dpi=args.dpi)

    if args.action in ['extract', 'both']:
        extract_data(args.folder_path)
