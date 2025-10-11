#!/usr/bin/env python3
import json
import base64
import os
import argparse
import sys
import shutil
from datetime import datetime

def compare_certificates(cert_file, key_file, certificate, key):
    """
    Compare the new certificate and key with the existing ones.
    Returns True if the files are identical, False otherwise.
    """
    if os.path.exists(cert_file) and os.path.exists(key_file):
        try:
            with open(cert_file, 'r') as f:
                existing_cert = f.read()
            with open(key_file, 'r') as f:
                existing_key = f.read()

            if existing_cert == certificate and existing_key == key:
                return True  # The certificate and key are the same
        except Exception as e:
            print(f"Error comparing files: {e}")
    
    return False  # The files don't match or don't exist

def extract_certificates(acme_file, output_dir, archive_old=False, skip_existing=False):
    """
    Extract certificates and private keys from Traefik's acme.json file.
    Organizes them into domain-specific folders for cron job usage.
    Optionally archives old certificates before overwriting.
    Skips certificates if they already exist in the output directory.
    """
    try:
        with open(acme_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{acme_file}' not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: '{acme_file}' is not a valid JSON file")
        sys.exit(1)
    
    os.makedirs(output_dir, exist_ok=True)
    extracted_count = 0
    
    # Support both 'letsencrypt' and 'acme' key names
    certificates_data = data.get('letsencrypt', {}).get('Certificates', [])
    if not certificates_data:
        certificates_data = data.get('acme', {}).get('Certificates', [])
    
    if not certificates_data:
        print("No certificates found in the file")
        return
    
    for cert_data in certificates_data:
        # Handle different domain formats
        domain = "unknown"
        if 'domain' in cert_data:
            if 'main' in cert_data['domain']:
                domain = cert_data['domain']['main']
            else:
                domain = list(cert_data['domain'].values())[0] if cert_data['domain'] else "unknown"
        elif 'domains' in cert_data:
            domain = cert_data['domains'][0]['main'] if cert_data['domains'] else "unknown"
        
        certificate_b64 = cert_data.get('certificate', '')
        key_b64 = cert_data.get('key', '')
        
        if certificate_b64 and key_b64:
            try:
                # Decode from base64
                certificate = base64.b64decode(certificate_b64).decode('utf-8')
                key = base64.b64decode(key_b64).decode('utf-8')
                
                # Sanitize domain name for folder name
                sanitized_domain = domain.replace('*', 'wildcard')
                
                # Create domain-specific folder
                domain_folder = os.path.join(output_dir, sanitized_domain)
                os.makedirs(domain_folder, exist_ok=True)
                
                # Check if files already exist and handle accordingly
                cert_file = os.path.join(domain_folder, "certificate.pem")
                key_file = os.path.join(domain_folder, "private_key.pem")
                combined_file = os.path.join(domain_folder, "combined.pem")
                
                # Skip existing files if skip_existing is True and the content matches
                if skip_existing and compare_certificates(cert_file, key_file, certificate, key):
                    print(f"Skipping {domain}, certificates already exist with matching content.")
                    continue
                
                # Optionally archive old certificates
                if archive_old:
                    archive_folder = os.path.join(domain_folder, 'archive')
                    os.makedirs(archive_folder, exist_ok=True)
                    for file_name in ["certificate.pem", "private_key.pem", "combined.pem"]:
                        old_file = os.path.join(domain_folder, file_name)
                        if os.path.exists(old_file):
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            archived_file = os.path.join(archive_folder, f"{file_name}_{timestamp}")
                            try:
                                shutil.move(old_file, archived_file)
                                print(f"Archived old {file_name} to {archived_file}")
                            except Exception as e:
                                print(f"Error archiving {file_name}: {e}")
                
                # Save certificate
                try:
                    with open(cert_file, 'w') as f:
                        f.write(certificate)
                except IOError as e:
                    print(f"Error writing certificate for {domain}: {e}")
                    continue  # Skip this certificate and move on
                
                # Save private key
                try:
                    with open(key_file, 'w') as f:
                        f.write(key)
                except IOError as e:
                    print(f"Error writing private key for {domain}: {e}")
                    continue  # Skip this certificate and move on
                
                # Save combined file (certificate + key)
                try:
                    with open(combined_file, 'w') as f:
                        f.write(certificate)
                        f.write(key)
                except IOError as e:
                    print(f"Error writing combined file for {domain}: {e}")
                    continue  # Skip this certificate and move on
                
                # Set secure permissions on key files
                try:
                    os.chmod(key_file, 0o600)
                    os.chmod(combined_file, 0o600)
                except Exception as e:
                    print(f"Error setting permissions for {domain}: {e}")
                    continue
                
                extracted_count += 1
            except Exception as e:
                # Handle error for this certificate and continue with the next one
                print(f"Error processing {domain}: {str(e)}")
    
    # Only output final result for cron logging
    print(f"Extracted {extracted_count} certificates to {output_dir}")

def main():
    parser = argparse.ArgumentParser(
        description='Extract certificates from Traefik acme.json file (cron optimized)'
    )
    
    parser.add_argument(
        'input_file', 
        nargs='?',
        help='Path to the acme.json file (optional if using -i)'
    )
    
    parser.add_argument(
        'output_dir', 
        nargs='?',
        help='Directory where certificates will be saved (optional if using -o)'
    )
    
    # Adding long versions for the flags
    parser.add_argument(
        '-i', '--input-file',
        dest='input_file_alt',
        help='Path to the acme.json file'
    )
    
    parser.add_argument(
        '-o', '--output-folder',
        dest='output_dir_alt',
        help='Directory where certificates will be saved'
    )
    
    parser.add_argument(
        '-a', '--archive',
        action='store_true',
        help='Option to archive old certificates before overwriting'
    )
    
    parser.add_argument(
        '-s', '--skip-existing',
        action='store_true',
        help='Option to skip certificates that already exist in the output directory with matching content'
    )
    
    args = parser.parse_args()
    
    # Determine input file and output directory
    acme_file = args.input_file_alt or args.input_file
    output_dir = args.output_dir_alt or args.output_dir
    
    if not acme_file or not output_dir:
        print("Error: Both input file and output directory are required")
        sys.exit(1)
    
    # Expand user directory (~) if present
    acme_file = os.path.expanduser(acme_file)
    output_dir = os.path.expanduser(output_dir)
    
    extract_certificates(acme_file, output_dir, archive_old=args.archive, skip_existing=args.skip_existing)

if __name__ == "__main__":
    main()
