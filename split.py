import os
import sys
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path
from tqdm import tqdm

def split(folder_path, dpi=100):
    material_path = os.path.join(folder_path, 'Material.pdf')
    instructions_path = os.path.join(folder_path, 'Instructions.txt')
    output_folder_pdfs = os.path.join(folder_path, 'PDFs')
    output_folder_pngs = os.path.join(folder_path, 'PNGs')
    output_folder_jpegs = os.path.join(folder_path, 'JPEGs')

    # Create the output folders if they don't exist
    os.makedirs(output_folder_pdfs, exist_ok=True)
    os.makedirs(output_folder_pngs, exist_ok=True)
    os.makedirs(output_folder_jpegs, exist_ok=True)

    # Read the instructions file
    with open(instructions_path, 'r') as file:
        instructions = file.readlines()

    # Load the original PDF
    reader = PdfReader(material_path)

    # Initialize progress tracking
    total_instructions = len(instructions)
    print(f"Processing {total_instructions} instructions...")

    for idx, instruction in enumerate(tqdm(instructions, desc="Processing Instructions")):
        instruction = instruction.strip()
        if not instruction:
            continue  # Skip empty lines

        # Split the instruction line
        parts = instruction.split(' ')
        if len(parts) != 2:
            print(f"Skipping invalid instruction line: {instruction}")
            continue

        page_list = parts[0]
        new_filename = parts[1]

        # Parse page list which can contain ranges and specific pages
        pages_to_extract = set()
        for segment in page_list.split(','):
            if '-' in segment:
                # Handle page range
                start_page, end_page = map(int, segment.split('-'))
                pages_to_extract.update(range(start_page, end_page + 1))
            else:
                # Handle specific pages
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
        output_pdf_path = os.path.join(output_folder_pdfs, f'{new_filename}.pdf')
        with open(output_pdf_path, 'wb') as output_pdf:
            writer.write(output_pdf)

        # Convert the new PDF to PNG and JPEG images
        pages = convert_from_path(output_pdf_path, dpi=dpi)
        for i, page in enumerate(pages):
            output_png_path = os.path.join(output_folder_pngs, f'{new_filename}_page_{i + 1}.png')
            output_jpeg_path = os.path.join(output_folder_jpegs, f'{new_filename}_page_{i + 1}.jpeg')
            page.save(output_png_path, 'PNG')
            page.save(output_jpeg_path, 'JPEG')

    print("PDFs, PNGs, and JPEGs have been successfully split and saved.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 split.py <folder_path>")
        sys.exit(1)

    folder_path = sys.argv[1]
    split(folder_path)
