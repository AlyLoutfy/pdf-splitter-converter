# PDF Splitter and Converter

This script allows you to split a PDF file into new PDFs based on instructions and convert the resulting PDFs into PNG and JPEG images.

## Requirements

To run this script, you need Python and a few Python packages. Follow these steps to set up your environment:

### 1. Install Python

Ensure you have Python installed. You can download it from the [official Python website](https://www.python.org/downloads/).

### 2. Install Required Packages

You need to install the following Python packages:

- `PyPDF2` for PDF manipulation
- `pdf2image` for converting PDF pages to images
- `tqdm` for displaying a progress bar

You can install these packages using pip. Open your terminal and run:

```sh
pip install PyPDF2 pdf2image tqdm
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
├── Instructions.txt
├── PDFs/ (this will be created by the script if it doesn't exist)
├── PNGs/ (this will be created by the script if it doesn't exist)
└── JPEGs/ (this will be created by the script if it doesn't exist)
```

### 2. Instructions.txt

Create an Instructions.txt file with lines specifying page ranges and filenames in the following format:

```plaintext
4-5 C3
66-68 I4(A&B&C&D)
66,67,69 I4(E)
66,67,70 I4(F&G)
66,67,71 I4(H)
```

Use commas to specify individual pages (e.g., 66, 67, 71).
Use hyphens to specify page ranges (e.g., 66-68).
Important: Ensure there are no empty lines at the end of the file.

### 3. Run the Script

Open your terminal, navigate to the directory containing the script, and run:

```sh
python3 split.py <folder_path>
```

Replace `<folder_path>` with the path to your folder containing `Material.pdf` and `Instructions.txt`.

You can also optionally, specify the `dpi` argument to set the resolution for converting PDF pages to images (default is 100)

```sh
python3 split.py <folder_path> --dpi <dpi>
```
