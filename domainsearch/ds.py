import os
import csv
import requests
import argparse
from dotenv import load_dotenv

# Load API key from .env file or environment
load_dotenv()
api_key = os.getenv('DOMAINR_KEY')
rapidapi_proxy_secret = os.getenv('RAPIDAPI_PROXY_SECRET')

# Domainr API details
url = "https://domainr.p.rapidapi.com/v2/search"
headers = {
    "X-RapidAPI-Key": api_key,
    "X-RapidAPI-Host": "domainr.p.rapidapi.com",
    "X-RapidAPI-Proxy-Secret": rapidapi_proxy_secret
}

def check_domain_availability(domain):
    """Check if a domain is available."""
    querystring = {"domain": domain}
    response = requests.get(url, headers=headers, params=querystring)
    
    # Inspect the response
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")

    try:
        data = response.json()
        return data.get('availability') == 'available'
    except requests.exceptions.JSONDecodeError:
        print("Failed to decode JSON from response.")
        return False  # Or handle as appropriate

def process_csv(file_path):
    """Process the CSV file to check domain availability."""
    updated_rows = []
    available_count = 0
    unavailable_count = 0

    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            domain = row['name']
            is_available = check_domain_availability(domain)
            print(f"Checking {domain}: {'Available' if is_available else 'Not Available'}")
            updated_rows.append({**row, 'available': int(is_available)})
            if is_available:
                available_count += 1
            else:
                unavailable_count += 1

    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        fieldnames = reader.fieldnames + ['available']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)

    print(f"\nSummary: {available_count} domains available, {unavailable_count} domains not available.")

def main():
    parser = argparse.ArgumentParser(description='Check domain availability from a CSV file.')
    parser.add_argument('csv_file', help='Path to the CSV file')
    args = parser.parse_args()
    process_csv(args.csv_file)

if __name__ == "__main__":
    main()
