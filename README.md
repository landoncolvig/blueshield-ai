# Jack LEO Training Tool

AI-powered law enforcement training software using Arizona Revised Statutes.

## Setup

```bash
cd ~/Documents/jack-leo-training-tool
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Set your Anthropic API key:
```bash
export ANTHROPIC_API_KEY=your_key_here
```

## Usage

### Scrape Priority Statutes (MVP)
```bash
python src/scraper.py
```

### Scrape All Title 13
```bash
python src/scraper.py --all
```

### Parse Scraped Statutes
```bash
python src/parser.py
```

### Parse Single Statute (testing)
```bash
python src/parser.py --single 13-3883
```

### Run Full Pipeline
```bash
cd scripts
python run_pipeline.py
```

## Project Structure

```
jack-leo-training-tool/
├── src/
│   ├── scraper.py      # ARS web scraper
│   └── parser.py       # Claude-powered statute parser
├── scripts/
│   └── run_pipeline.py # Full scrape->parse pipeline
├── data/
│   ├── raw_statutes.json    # Scraped statute text
│   └── parsed_statutes.json # Structured training data
└── requirements.txt
```

## Priority Statutes (MVP)

- **Arrest**: 13-3883, 13-3884, 13-3881
- **Domestic Violence**: 13-3601, 13-3602
- **Use of Force**: 13-401 through 13-411
- **Patrol Offenses**: 13-2904, 13-1502/3/4, 13-1805
- **Assault**: 13-1201 through 13-1204
- **Obstruction**: 13-2503, 13-2504, 13-2506
- **Weapons**: 13-3101, 13-3102
- **Drugs**: 13-3401, 13-3407, 13-3408
