# PDF Splitter, Converter, and Data Extractor

This script allows you to `Split` a PDF file into new PDFs based on instructions, `Convert` the resulting PDFs into PNG and JPEG images, and `Extract` specific details from the PDFs to save into an Excel file.

## Requirements

To run this script, you need Python and a few Python packages. Follow these steps to set up your environment:

### 1. Install Python

Ensure you have Python installed. You can download it from the [official Python website](https://www.python.org/downloads/).

### 2. Install Required Packages

You need to install the following Python packages:

- `PyPDF2` for PDF manipulation
- `pdf2image` for converting PDF pages to images
- `tqdm` for displaying a progress bar
- `pandas` for handling Excel files and data manipulation
- `pdfplumber` for extracting text and data from PDF documents

You can install these packages using pip. Open your terminal and run:

```sh
pip install PyPDF2 pdf2image tqdm pandas pdfplumber
```

### 3. Install Poppler

`pdf2image` requires Poppler to be installed.

On Ubuntu/Debian:

```sh
sudo apt-get install poppler-utils
```

On macOS (using Homebrew):

Install Homebrew (if not already installed). You can install Homebrew by running:

```sh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Install Poppler using Homebrew:

```sh
brew install poppler
```

## Usage

### 1. Prepare Your Folder Structure

Place your files in a folder with the following structure:

```plaintext
<folder_path>/
├── Material.pdf
├── Instructions.xlsx
├── PDFs/ (this will be created by the script if it doesn't exist)
├── PNGs/ (this will be created by the script if it doesn't exist)
└── JPEGs/ (this will be created by the script if it doesn't exist)
```

### 2. Instructions.xlsx

Create an Instructions.xlsx file with two columns: `Unit ID` and `Pages`, specifying filenames and page ranges in the following format:

| Unit ID | Pages |
| ------- | ----- |
| C3      | 1-3   |
| C4      | 5-7   |
| D1      | 5,8,9 |
| I4(H)   | 10-15 |

> [!TIP]
> Page Ranges and Specific Pages: Instructions in the Excel file can include both ranges (e.g., "1-3") and specific pages (e.g., "2,3,5") for splitting PDFs.

### 3. Extract Data from PDFs

This script can also extract specific details (Unit ID, BUA, Bedrooms, Covered Terrace, Uncovered Terrace) from the split PDFs and save the extracted data into an Excel file `Extracted Data.xlsx`.

By default, the script will perform both the PDF split and data extraction tasks. However, if you only want to extract data without splitting the PDF, you can use the `--action` argument to specify the operation.

Refer to the section below on how to use the `--action` argument to control whether the script splits the PDF, extracts data, or does both.

> [!WARNING]
> The data extraction feature is still under development, and the results may not be entirely accurate. The only reliable and stable data extracted so far is the `Unit ID` column. Please verify the other extracted data manually.

### 4. Run the Script

Open your terminal, navigate to the directory containing the script, and run:

```sh
python3 split.py <folder_path>
```

Replace `<folder_path>` with the path to your folder containing `Material.pdf` and `Instructions.xlsx`.

> [!NOTE]
> By default, the script will both split the PDF and extract data.

You can optionally specify the `dpi` argument to set the resolution for converting PDF pages to images (default is 100):

```sh
python3 split.py <folder_path> --dpi <dpi>
```

> [!TIP]
> If you want to specify the action, you can use the --action argument:

To only split the PDF:

```sh
python3 split.py <folder_path> --action split
```

To only extract data:

```sh
python3 split.py <folder_path> --action extract
```
