# PDF Split Tool

A Python script that splits a PDF file into multiple PDFs based on page ranges specified in an Excel file. The script can also convert the split PDFs to images and extract specific data from them.

## Features

- Split a PDF file into multiple PDFs based on page ranges from an Excel file
- Support for custom page ordering (e.g., "1-15, 76, 40-43, 70-75")
- Convert split PDFs to PNG and JPEG images (optional)
- Extract specific data from PDFs (optional)
- Create a zip file of all split PDFs (optional)
- Interactive command-line interface
- Progress bar for processing instructions

## Requirements

- Python 3.6 or higher
- PyPDF2
- pdf2image
- pandas
- pdfplumber
- tqdm
- poppler (for pdf2image)

## Installation

1. Clone this repository or download the script
2. Install the required packages:
   ```bash
   pip install PyPDF2 pdf2image pandas pdfplumber tqdm
   ```
3. Install poppler:
   - Windows: Download and install poppler from [poppler releases](http://blog.alivate.com.au/poppler-windows/)
   - Linux: `sudo apt-get install poppler-utils`
   - macOS: `brew install poppler`

## Usage

1. Place your input files in a folder:

   - One PDF file (any name)
   - One Excel file (any name) with two columns:
     - Unit ID: The identifier for the output PDF
     - Page List: Comma-separated list of page ranges and specific pages (e.g., "1-15, 76, 40-43, 70-75")

2. Run the script:

   ```bash
   python split.py path/to/your/folder
   ```

3. Answer the interactive prompts:
   - Would you like to create PNG and JPEG images? (y/n)
   - Would you like to extract data from the PDFs? (y/n)
   - Would you like to create a zip file of the PDFs folder? (y/n)
   - If creating images, enter DPI value (default: 100)

## Output

The script will create the following folders in your input directory:

- `PDFs/`: Contains the split PDF files
- `PNGs/`: Contains PNG images (if requested)
- `JPEGs/`: Contains JPEG images (if requested)
- `PDFs_YYYYMMDD_HHMMSS.zip`: Zip file of all PDFs (if requested)
- `Extracted Data.xlsx`: Excel file with extracted data (if requested)

## Data Extraction

If data extraction is enabled, the script will look for the following information in each PDF:

- BUA (Built-up Area)
- Number of Bedrooms
- Covered Terrace area
- Uncovered Terrace area

## Notes

- The script will use the first PDF and Excel file it finds in the specified folder
- Page numbers in the Excel file should match the actual page numbers in the PDF
- The script supports both .xlsx and .xls Excel file formats
- All prompts accept both 'y'/'yes' and 'n'/'no' as valid inputs
