#!/usr/bin/env python

import argparse
import csv
import os

import requests
from dotenv import load_dotenv

# Load API key from .env file or environment
load_dotenv()
api_key = os.getenv("DOMAINR_KEY")
rapidapi_proxy_secret = os.getenv("RAPIDAPI_PROXY_SECRET")

# Domainr API details
url = "https://domainr.p.rapidapi.com/v2/search"
headers = {
    "X-RapidAPI-Key": api_key,
    "X-RapidAPI-Host": "domainr.p.rapidapi.com",
    "X-RapidAPI-Proxy-Secret": rapidapi_proxy_secret,
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
        return data.get("availability") == "available"
    except requests.exceptions.JSONDecodeError:
        print("Failed to decode JSON from response.")
        return False  # Or handle as appropriate


def process_csv(file_path, out_file_path=None):
    """Process the CSV file to check domain availability."""
    updated_rows = []
    available_count = 0
    unavailable_count = 0

    with open(file_path, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            domain = row["name"]
            if "available" not in row:
                is_available = check_domain_availability(domain)
                print(
                    f"Checking {domain}: "
                    f"{'Available' if is_available else 'Not Available'}"
                )
                updated_rows.append({**row, "available": int(is_available)})
                if is_available:
                    available_count += 1
                else:
                    unavailable_count += 1
            else:
                print(f"Skipping {domain}: Results already available")
                updated_rows.append(row)

    out_file_path = out_file_path or file_path
    with open(out_file_path, mode="w", newline="", encoding="utf-8") as file:
        fieldnames = reader.fieldnames + ["available"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)

    print(
        f"\nSummary: {available_count} domains available, "
        f"{unavailable_count} domains not available."
    )


def check_domains(domains, out_file_path=None):
    """Check the availability of a list of domains."""
    results = []
    for domain in domains:
        is_available = check_domain_availability(domain)
        print(
            f"Checking {domain}: "
            f"{'Available' if is_available else 'Not Available'}"
        )
        results.append({"name": domain, "available": int(is_available)})

    if out_file_path:
        with open(
            out_file_path, mode="w", newline="", encoding="utf-8"
        ) as file:
            fieldnames = ["name", "available"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    else:
        for result in results:
            print(
                f"{result['name']}: "
                f"{'Available' if result['available'] else 'Not Available'}"
            )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Check domain availability from a CSV file or command line."
        ),
    )
    parser.add_argument(
        "--in-file", help="Path to the CSV file containing domain names"
    )
    parser.add_argument(
        "--out-file", help="Path to the CSV file to write results to"
    )
    parser.add_argument(
        "-d",
        "--domain",
        help="Comma separated list of domain names to check",
    )
    args = parser.parse_args()
    if args.domain:
        check_domains(args.domain.split(","), args.out_file)
    else:
        process_csv(args.in_file, args.out_file)


if __name__ == "__main__":
    main()
