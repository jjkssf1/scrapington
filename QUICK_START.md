# 🚀 Quick Start Guide

**Get scraping in 2 minutes!**

## Step 1: Setup (30 seconds)
```bash
git clone https://github.com/jjkssf1/scrapington.git
cd scrapington
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Step 2: Find Your URL (30 seconds)
1. Go to any ArcGIS map service
2. Look for a URL ending with `/FeatureServer/0/query`
3. Copy the full URL

**Example URLs:**
- School Districts: `https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_School_Districts/FeatureServer/0/query`
- Counties: `https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Counties_Generalized/FeatureServer/0/query`

## Step 3: Scrape! (30 seconds)
```bash
python universal_scraper.py --url "YOUR_URL_HERE" --output "my_data.geojson"
```

## Step 4: Deploy (30 seconds)
```bash
python deploy.py
```

**Done!** Your data is in `geojson_export/my_data.geojson` and pushed to GitHub.

## 🎯 Pro Tips

### Filter Your Data
```bash
python universal_scraper.py \
  --url "YOUR_URL" \
  --output "california_schools.geojson" \
  --where "STATE_NAME = 'California'"
```

### Use Configuration Files
```bash
# Create config
python universal_scraper.py --create-config my_config.json

# Edit the URL in my_config.json
# Then run
python universal_scraper.py --config my_config.json
```

### Large Datasets
```bash
python universal_scraper.py \
  --url "YOUR_URL" \
  --output "big_data.geojson" \
  --max-records 10000 \
  --batch-size 500
```

## 🔧 Troubleshooting

**"Invalid URL"** → Make sure URL ends with `/query`
**"No features"** → Check your WHERE clause
**"Timeout"** → Increase `--timeout` or reduce `--batch-size`

## 📞 Need Help?

- Check the full README.md for detailed docs
- Use `--verbose` for detailed logging
- Test with `--max-records 100` first
