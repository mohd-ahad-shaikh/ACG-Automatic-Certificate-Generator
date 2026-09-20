# ACG — Automatic Certificate Generator

ACG (Automatic Certificate Generator) is a Python and Flask based universal certificate creation platform.

It allows users to create professional certificates without changing the source code. Users can enter certificate information, add custom fields, customize the design, upload assets such as logos and signatures, generate PDF certificates, and generate multiple certificates using CSV data.

---

## Project Objective

The main objective of ACG is to make certificate creation simple, flexible, fast, and reusable.

Instead of manually designing every certificate, users can enter the required information through a web interface and generate professional PDF certificates automatically.

---

## Key Features

- Universal certificate creation
- Professional PDF certificate generation
- Single certificate generation
- Bulk certificate generation using CSV
- Dynamic custom fields
- Custom certificate type
- Custom recipient information
- Certificate ID support
- Automatic or manual date and time
- Multiple certificate themes
- Custom colors
- Custom fonts
- Custom title and text settings
- Background upload
- Logo upload
- Signature upload
- Seal/emblem upload
- Professional certificate layout
- Save and load certificate designs
- Certificate history
- Certificate ID based record verification
- ZIP download for bulk-generated certificates
- Mobile-friendly Flask web interface
- No source-code modification required for normal certificate creation

---

## Technologies Used

- Python
- Flask
- ReportLab
- Pillow
- HTML
- CSS
- JavaScript
- CSV File Handling

---

## Main Project Modules

### app.py

The main Flask application.

It handles:

- Web interface
- User input
- Certificate generation requests
- Design settings
- File uploads
- Bulk generation
- Saved designs
- Certificate history
- Verification

### certificate_engine.py

The main certificate generation engine.

It creates the final professional PDF certificate using ReportLab.

It handles:

- Page orientation
- Certificate layout
- Background
- Borders
- Logo
- Seal
- Signature
- Recipient information
- Dynamic fields
- Certificate ID
- Date and time
- Organization information

### design_engine.py

Manages certificate design settings and themes.

### template_manager.py

Manages uploaded certificate assets such as:

- Backgrounds
- Logos
- Signatures
- Seals
- Fonts
- Templates

### csv_manager.py

Handles CSV files used for bulk certificate generation.

### data_manager.py

Manages dynamic certificate fields and their values.

### date_manager.py

Handles automatic and manual date/time settings.

### ID_manager.py

Handles certificate ID generation and validation.

### Universal_data.py

Provides a universal certificate data structure.

### Validation_manager.py

Validates certificate information, IDs, custom fields, and other input data.

### Layout_manager.py

Manages certificate layout and visual elements.

---

## Project Structure

```text
ACG-Automatic-Certificate-Generator/
│
├── app.py
├── certificate_engine.py
├── design_engine.py
├── template_manager.py
├── csv_manager.py
├── data_manager.py
├── date_manager.py
├── ID_manager.py
├── Universal_data.py
├── Validation_manager.py
├── Layout_manager.py
│
├── templates/
│
├── uploads/
│   ├── backgrounds/
│   ├── logos/
│   ├── signatures/
│   ├── seals/
│   └── fonts/
│
├── output/
│
├── data/
│
├── requirements.txt
├── .gitignore
└── README.md