# Lucky Kerala

**Lucky Kerala** is a lottery result verification and image processing system that allows users to check their Kerala lottery results.

## Features

- **Lottery Result Checking**: Scrapes the latest Kerala lottery results from the official website and verifies if a given number has won any prizes.
- **Optical Character Recognition (OCR)**: Uses EasyOCR and YOLO to detect and extract lottery numbers from images.
- **Image Processing**: Overwrites old lottery numbers on images and replaces them with a new manually entered number.
- **Django Web Interface**: Provides a web-based platform for checking lottery results and processing images.

## Installation

### Prerequisites
- Python 3.x
- Django
- OpenCV
- EasyOCR
- Ultralytics YOLO
- BeautifulSoup (for web scraping)
- Requests
- NumPy

### Setup Instructions
1. Clone this repository:
   ```bash
   git clone https://github.com/Aromalunni-U/Lucky-Kerala.git
   cd project
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Django server:
   ```bash
   python manage.py runserver
   ```
4. Open the web app in your browser at:
   ```
   http://127.0.0.1:8000/
   ```

## Usage

### Checking Lottery Results
1. Upload an image of your lottery ticket.
2. Select the lottery name from the dropdown menu.
3. Click the "Check Result" button.
4. The system will extract the lottery number and compare it with the latest results.

