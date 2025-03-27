import os
import argparse
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path
from tqdm import tqdm
import pandas as pd
import pdfplumber
import re
import shutil
from datetime import datetime

def split(folder_path, dpi=100, create_images=False):
    # Find the first PDF and Excel file in the folder
    pdf_file = None
    excel_file = None
    
    for file in os.listdir(folder_path):
        if file.lower().endswith('.pdf') and not pdf_file:
            pdf_file = file
        elif file.lower().endswith(('.xlsx', '.xls')) and not excel_file:
            excel_file = file
    
    if not pdf_file:
        raise FileNotFoundError("No PDF file found in the specified folder.")
    if not excel_file:
        raise FileNotFoundError("No Excel file found in the specified folder.")
    
    material_path = os.path.join(folder_path, pdf_file)
    instructions_path = os.path.join(folder_path, excel_file)
    output_folder_pdfs = os.path.join(folder_path, 'PDFs')
    
    # Create output folders
    os.makedirs(output_folder_pdfs, exist_ok=True)
    if create_images:
        output_folder_pngs = os.path.join(folder_path, 'PNGs')
        output_folder_jpegs = os.path.join(folder_path, 'JPEGs')
        os.makedirs(output_folder_pngs, exist_ok=True)
        os.makedirs(output_folder_jpegs, exist_ok=True)

    print(f"Using PDF file: {pdf_file}")
    print(f"Using Excel file: {excel_file}")
    
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
        pages_to_extract = []
        for segment in page_list.split(','):
            segment = segment.strip()
            if '-' in segment:
                # Handle page range
                start_page, end_page = map(int, segment.split('-'))
                pages_to_extract.extend(list(range(start_page, end_page + 1)))
            else:
                # Handle specific pages or single page
                pages_to_extract.append(int(segment))

        # Create a new PDF writer
        writer = PdfWriter()

        # Add the specified pages to the new PDF in the exact order they were specified
        for page_num in pages_to_extract:
            if page_num - 1 < len(reader.pages):
                writer.add_page(reader.pages[page_num - 1])  # Page numbers in PdfReader are zero-indexed
            else:
                print(f"Warning: Page number {page_num} is out of range in the original PDF.")

        # Save the new PDF
        output_pdf_path = os.path.join(output_folder_pdfs, f'{unit_id}.pdf')
        with open(output_pdf_path, 'wb') as output_pdf:
            writer.write(output_pdf)

        # Convert the new PDF to PNG and JPEG images if requested
        if create_images:
            pages = convert_from_path(output_pdf_path, dpi=dpi)
            for i, page in enumerate(pages):
                output_png_path = os.path.join(output_folder_pngs, f'{unit_id}_page_{i + 1}.png')
                output_jpeg_path = os.path.join(output_folder_jpegs, f'{unit_id}_page_{i + 1}.jpeg')
                page.save(output_png_path, 'PNG')
                page.save(output_jpeg_path, 'JPEG')

    print("PDFs have been successfully split and saved.")
    if create_images:
        print("PNGs and JPEGs have been successfully created.")

def clean_value(value):
    """Remove whitespace from a value."""
    if isinstance(value, str):
        return re.sub(r'\s+', '', value)
    return value

def extract_data(folder_path):
    print("Extracting Data..")

    output_file = os.path.join(folder_path, 'Extracted Data.xlsx')
    pdf_folder = os.path.join(folder_path, 'PDFs')
    
    if not os.path.exists(pdf_folder):
        raise FileNotFoundError(f"PDF folder not found at {pdf_folder}")

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

        # If BUA is not found explicitly, find the first occurrence of a numeric value followed by "sqm"
        if not details['BUA']:
            sqm_pattern = r'(\d+[\d\s,]*\d*)\s*(sqm|SQM|m²)'
            sqm_match = re.search(sqm_pattern, full_text, re.IGNORECASE)
            if sqm_match:
                details['BUA'] = sqm_match.group(1).strip()

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
    parser.add_argument('folder_path', type=str, help='Folder path containing one PDF and one Excel file')
    args = parser.parse_args()

    # Ask user what they want to do
    print("\nWelcome to PDF Split Tool!")
    print("------------------------")
    
    # Ask about image conversion
    while True:
        create_images = input("\nWould you like to create PNG and JPEG images? (y/n): ").lower()
        if create_images in ['y', 'yes', 'n', 'no']:
            create_images = 'yes' if create_images in ['y', 'yes'] else 'no'
            break
        print("Please answer with 'y' or 'n'")
    
    # Ask about data extraction
    while True:
        extract_data_choice = input("\nWould you like to extract data from the PDFs? (y/n): ").lower()
        if extract_data_choice in ['y', 'yes', 'n', 'no']:
            extract_data_choice = 'yes' if extract_data_choice in ['y', 'yes'] else 'no'
            break
        print("Please answer with 'y' or 'n'")
    
    # Ask about zipping PDFs
    while True:
        zip_pdfs = input("\nWould you like to create a zip file of the PDFs folder? (y/n): ").lower()
        if zip_pdfs in ['y', 'yes', 'n', 'no']:
            zip_pdfs = 'yes' if zip_pdfs in ['y', 'yes'] else 'no'
            break
        print("Please answer with 'y' or 'n'")
    
    # Ask about DPI if creating images
    dpi = 100
    if create_images == 'yes':
        while True:
            try:
                dpi = int(input("\nEnter DPI for image conversion (default: 100): ") or "100")
                if dpi > 0:
                    break
                print("DPI must be greater than 0")
            except ValueError:
                print("Please enter a valid number")

    # Process the PDF splitting
    print("\nStarting PDF splitting process...")
    split(args.folder_path, dpi=dpi, create_images=create_images == 'yes')

    # Extract data if requested
    if extract_data_choice == 'yes':
        print("\nExtracting data from PDFs...")
        extract_data(args.folder_path)

    # Create zip file if requested
    if zip_pdfs == 'yes':
        print("\nCreating zip file of PDFs folder...")
        pdfs_folder = os.path.join(args.folder_path, 'PDFs')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"PDFs_{timestamp}.zip"
        zip_path = os.path.join(args.folder_path, zip_filename)
        
        try:
            shutil.make_archive(
                os.path.splitext(zip_path)[0],  # path without .zip extension
                'zip',
                pdfs_folder
            )
            print(f"Zip file created successfully: {zip_filename}")
        except Exception as e:
            print(f"Error creating zip file: {str(e)}")

    print("\nProcess completed successfully!")
