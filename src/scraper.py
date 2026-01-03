"""
ARS Title 13 Web Scraper
Scrapes Arizona Revised Statutes from azleg.gov
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from pathlib import Path
from tqdm import tqdm

BASE_URL = "https://www.azleg.gov"
TITLE_13_INDEX = f"{BASE_URL}/arsDetail/?title=13"

# Priority statutes for MVP (patrol-focused)
PRIORITY_SECTIONS = [
    # Critical - Arrest & Procedure
    "13-3883",  # Warrantless arrest
    "13-3884",  # Arrest by private person
    "13-3881",  # Method of arrest
    "13-3903",  # Release procedures

    # Critical - Domestic Violence
    "13-3601",  # DV definition & mandatory arrest
    "13-3602",  # Order of protection

    # Critical - Use of Force / Justification
    "13-401",   # Unavailability of justification defense
    "13-402",   # Justification defenses
    "13-403",   # Justification - use of physical force
    "13-404",   # Justification - self defense
    "13-405",   # Justification - deadly force
    "13-406",   # Justification - defense of third person
    "13-407",   # Justification - defense of premises
    "13-408",   # Justification - defense of property
    "13-409",   # Justification - crime prevention
    "13-410",   # Justification - law enforcement
    "13-411",   # Justification - arrest

    # Critical - Common Patrol Offenses
    "13-2904",  # Disorderly conduct
    "13-1502",  # Criminal trespass 3rd degree
    "13-1503",  # Criminal trespass 2nd degree
    "13-1504",  # Criminal trespass 1st degree

    # High Priority - Theft/Property
    "13-1805",  # Shoplifting
    "13-1802",  # Theft

    # High Priority - Assault
    "13-1201",  # Endangerment
    "13-1202",  # Threatening/intimidating
    "13-1203",  # Assault
    "13-1204",  # Aggravated assault

    # High Priority - Obstruction
    "13-2503",  # Resisting arrest
    "13-2504",  # Hindering prosecution
    "13-2506",  # Obstructing justice
    "13-2508",  # Refusing to aid officer

    # High Priority - Weapons
    "13-3101",  # Weapons definitions
    "13-3102",  # Misconduct involving weapons

    # High Priority - Drugs
    "13-3401",  # Drug definitions
    "13-3407",  # Possession/use of dangerous drugs
    "13-3408",  # Narcotic drugs violations

    # Other Common
    "13-1303",  # Unlawful imprisonment
    "13-1304",  # Kidnapping
    "13-2905",  # Loitering
    "13-2906",  # Obstructing highway
    "13-2911",  # Interference with educational institution
    "13-2921",  # Harassment
    "13-2923",  # Stalking
]


def get_title_index():
    """Fetch the Title 13 index page and extract all section links."""
    print("Fetching Title 13 index...")
    response = requests.get(TITLE_13_INDEX)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    sections = []

    # Find all links to individual statute sections
    for link in soup.find_all('a', href=True):
        href = link['href']
        # Match pattern like /ars/13/03883.htm
        if re.match(r'/ars/13/\d+\.htm', href):
            section_num = re.search(r'/ars/13/0*(\d+)\.htm', href)
            if section_num:
                raw_num = section_num.group(1)
                # Format as 13-XXXX
                if len(raw_num) <= 4:
                    formatted = f"13-{raw_num}"
                else:
                    # Handle sections like 13-3883
                    formatted = f"13-{raw_num}"

                sections.append({
                    "section": formatted,
                    "url": f"{BASE_URL}{href}",
                    "title": link.get_text(strip=True)
                })

    return sections


def scrape_section(url: str) -> dict:
    """Scrape a single statute section."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the main content
        content_div = soup.find('div', class_='statuteText') or soup.find('body')

        if content_div:
            # Get raw text
            raw_text = content_div.get_text(separator='\n', strip=True)

            # Get HTML for structure preservation
            raw_html = str(content_div)

            return {
                "raw_text": raw_text,
                "raw_html": raw_html,
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }

        return {"error": "No content found", "url": url}

    except Exception as e:
        return {"error": str(e), "url": url}


def scrape_priority_statutes(output_dir: str = "data"):
    """Scrape only the priority statutes for MVP."""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    results = []

    print(f"Scraping {len(PRIORITY_SECTIONS)} priority statutes...")

    for section in tqdm(PRIORITY_SECTIONS):
        # Convert section number to URL format
        # 13-3883 -> 03883, 13-401 -> 00401
        section_num = section.split("-")[1]
        padded_num = section_num.zfill(5)
        url = f"{BASE_URL}/ars/13/{padded_num}.htm"

        content = scrape_section(url)

        result = {
            "section": section,
            "url": url,
            **content
        }
        results.append(result)

        # Rate limiting
        time.sleep(0.5)

    # Save raw scraped data
    output_file = output_path / "raw_statutes.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Saved {len(results)} statutes to {output_file}")

    # Report any errors
    errors = [r for r in results if "error" in r]
    if errors:
        print(f"\nWarning: {len(errors)} sections had errors:")
        for e in errors:
            print(f"  - {e['section']}: {e['error']}")

    return results


def scrape_all_title_13(output_dir: str = "data"):
    """Scrape all of Title 13 (comprehensive)."""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Get index of all sections
    sections = get_title_index()
    print(f"Found {len(sections)} sections in Title 13")

    results = []

    for section_info in tqdm(sections):
        content = scrape_section(section_info['url'])

        result = {
            **section_info,
            **content
        }
        results.append(result)

        # Rate limiting
        time.sleep(0.5)

    # Save
    output_file = output_path / "all_title_13.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Saved {len(results)} statutes to {output_file}")
    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Scrape ARS Title 13")
    parser.add_argument("--all", action="store_true", help="Scrape all of Title 13 (not just priority)")
    parser.add_argument("--output", default="data", help="Output directory")

    args = parser.parse_args()

    if args.all:
        scrape_all_title_13(args.output)
    else:
        scrape_priority_statutes(args.output)
