# Traefik TLS/SSL Certificate(s) Extractor

## Description
This Python script extracts TLS/SSL certificates and private keys from Traefik's `acme.json` file. It saves the certificates in a specified folder, optionally users can archive old certificates and skip certificates that already exist.

## Features
- Extracts certificates from Traefik's `acme.json`.
- Supports both `letsencrypt` and `acme` key names.
- Optionally archives old certificates before overwriting.
- Skips certificates if they already exist and match the current content.
- Provides both short and long command-line options for user convenience.

## Installation

Ensure you have Python 3 installed. Clone the repository and install the dependencies:

```bash
git clone https://github.com/silvermono/traefik-certificate-extractor.git
cd traefik-certificate-extractor
```

## Usage

### Basic command

`python3 extractor.py --input-file /path/to/acme.json --output-folder /path/to/output-folder`

or short version:

`python3 extractor.py -i /path/to/acme.json -o /path/to/output-folder`

### Available usage keys

`python3 extractor.py --help` or `python3 extractor.py -h`

```bash
usage: extractor.py [-h] [-i INPUT_FILE_ALT] [-o OUTPUT_DIR_ALT] [-a] [-s] [input_file] [output_dir]

Extract certificates from Traefik acme.json file (cron optimized)

positional arguments:
  input_file            Path to the acme.json file (optional if using -i)
  output_dir            Directory where certificates will be saved (optional if using -o)

options:
  -h, --help            show this help message and exit
  -i INPUT_FILE_ALT, --input-file INPUT_FILE_ALT
                        Path to the acme.json file
  -o OUTPUT_DIR_ALT, --output-folder OUTPUT_DIR_ALT
                        Directory where certificates will be saved
  -a, --archive         Option to archive old certificates before overwriting
  -s, --skip-existing   Option to skip certificates that already exist in the output directory with matching content
```
