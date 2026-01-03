"""
ARS Statute Parser
Uses Claude to extract structured data from raw statute text
"""

import json
import os
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

client = Anthropic()

PARSE_PROMPT = """You are a legal expert parsing Arizona Revised Statutes for a law enforcement training application.

Given the following statute text, extract structured information in JSON format.

STATUTE SECTION: {section}
STATUTE TEXT:
{text}

Extract the following structure (respond ONLY with valid JSON, no other text):

{{
  "section": "{section}",
  "title": "Short descriptive title of the statute",
  "summary": "1-2 sentence plain English summary for patrol officers",
  "classification": "felony/misdemeanor/petty offense/varies (explain)",

  "elements": [
    {{
      "element": "Description of required element",
      "explanation": "Plain English explanation for officers"
    }}
  ],

  "mental_state": "Required mental state (intentionally, knowingly, recklessly, negligently, strict liability)",

  "officer_authority": [
    "List any specific authority granted to officers (arrest, detain, seize, etc.)"
  ],

  "mandatory_actions": [
    "List any MANDATORY actions officers must take (mandatory arrest, required notifications, etc.)"
  ],

  "penalty": {{
    "base": "Base classification",
    "enhancements": ["List any factors that enhance penalty"],
    "notes": "Any special sentencing notes"
  }},

  "key_definitions": [
    {{
      "term": "Defined term",
      "definition": "Legal definition from statute"
    }}
  ],

  "common_mistakes": [
    "List 2-4 common mistakes officers make with this statute"
  ],

  "practical_tips": [
    "List 2-4 practical tips for patrol officers"
  ],

  "related_statutes": [
    "List related ARS sections that officers should know"
  ],

  "fourth_amendment_notes": "Any search/seizure considerations specific to this offense",

  "miranda_notes": "Any Miranda/custody considerations specific to this offense"
}}

Be thorough but practical. Focus on what a patrol officer needs to know in the field.
If a field doesn't apply to this statute, use null or empty array as appropriate.
"""


def parse_statute(section: str, raw_text: str) -> dict:
    """Use Claude to parse a statute into structured format."""
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": PARSE_PROMPT.format(section=section, text=raw_text)
                }
            ]
        )

        # Extract JSON from response
        content = response.content[0].text

        # Try to parse as JSON
        # Handle case where Claude might wrap in ```json blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        parsed = json.loads(content.strip())
        parsed["_parse_status"] = "success"
        return parsed

    except json.JSONDecodeError as e:
        return {
            "section": section,
            "_parse_status": "json_error",
            "_error": str(e),
            "_raw_response": content if 'content' in dir() else None
        }
    except Exception as e:
        return {
            "section": section,
            "_parse_status": "error",
            "_error": str(e)
        }


def parse_all_statutes(input_file: str, output_file: str):
    """Parse all scraped statutes."""
    with open(input_file, 'r') as f:
        raw_statutes = json.load(f)

    parsed_results = []

    print(f"Parsing {len(raw_statutes)} statutes with Claude...")

    for statute in tqdm(raw_statutes):
        if "error" in statute:
            print(f"  Skipping {statute['section']} (scrape error)")
            continue

        if "raw_text" not in statute:
            print(f"  Skipping {statute['section']} (no text)")
            continue

        parsed = parse_statute(statute['section'], statute['raw_text'])
        parsed['url'] = statute.get('url')
        parsed['scraped_at'] = statute.get('scraped_at')

        parsed_results.append(parsed)

    # Save parsed results
    with open(output_file, 'w') as f:
        json.dump(parsed_results, f, indent=2)

    # Summary
    success = len([r for r in parsed_results if r.get('_parse_status') == 'success'])
    errors = len([r for r in parsed_results if r.get('_parse_status') != 'success'])

    print(f"\nParsing complete:")
    print(f"  Success: {success}")
    print(f"  Errors: {errors}")
    print(f"  Output: {output_file}")

    return parsed_results


def parse_single_statute(section: str, input_file: str = "data/raw_statutes.json"):
    """Parse a single statute for testing."""
    with open(input_file, 'r') as f:
        raw_statutes = json.load(f)

    statute = next((s for s in raw_statutes if s['section'] == section), None)

    if not statute:
        print(f"Section {section} not found in {input_file}")
        return None

    if "raw_text" not in statute:
        print(f"No text for section {section}")
        return None

    print(f"Parsing {section}...")
    parsed = parse_statute(section, statute['raw_text'])

    print(json.dumps(parsed, indent=2))
    return parsed


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Parse ARS statutes with Claude")
    parser.add_argument("--input", default="data/raw_statutes.json", help="Input file from scraper")
    parser.add_argument("--output", default="data/parsed_statutes.json", help="Output file")
    parser.add_argument("--single", help="Parse single section (e.g., 13-3883)")

    args = parser.parse_args()

    if args.single:
        parse_single_statute(args.single, args.input)
    else:
        parse_all_statutes(args.input, args.output)
