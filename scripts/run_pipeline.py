#!/usr/bin/env python3
"""
Full pipeline: Scrape -> Parse -> Output
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scraper import scrape_priority_statutes
from parser import parse_all_statutes


def main():
    print("=" * 60)
    print("ARS STATUTE PIPELINE")
    print("=" * 60)

    # Step 1: Scrape
    print("\n[1/2] SCRAPING PRIORITY STATUTES...")
    print("-" * 40)
    scrape_priority_statutes(output_dir="../data")

    # Step 2: Parse
    print("\n[2/2] PARSING WITH CLAUDE...")
    print("-" * 40)
    parse_all_statutes(
        input_file="../data/raw_statutes.json",
        output_file="../data/parsed_statutes.json"
    )

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print("\nOutput files:")
    print("  - data/raw_statutes.json (scraped HTML/text)")
    print("  - data/parsed_statutes.json (structured for training)")


if __name__ == "__main__":
    main()
