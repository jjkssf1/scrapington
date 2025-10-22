# 🗺️ Scrapington

**Universal GeoJSON Scraper for ArcGIS Feature Services**

A production-ready toolkit for extracting geospatial data from any ArcGIS Feature Service with just a URL. Perfect for data scientists, GIS professionals, and developers who need reliable, scalable data extraction.

## ✨ Features

- **🎯 Universal**: Works with any ArcGIS Feature Service URL
- **⚡ Production Ready**: Handles pagination, retries, and error recovery
- **🔧 Configurable**: JSON config files or command-line options
- **📊 Data Quality**: Automatic geometry validation and attribute normalization
- **🚀 Easy Deploy**: One-command deployment to GitHub
- **📦 Packaged**: Proper Python package with dependencies

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/jjkssf1/scrapington.git
cd scrapington
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Basic Usage - Just Paste a URL!
```bash
# Extract data from any ArcGIS service
python universal_scraper.py --url "https://services.arcgis.com/..." --output "my_data.geojson"

# Or use the packaged command
scrapington --url "https://services.arcgis.com/..." --output "my_data.geojson"
```

> **💡 Pro Tip**: You can now provide simplified URLs!
> - Works with: `https://services.arcgis.com/.../FeatureServer` or `.../MapServer` (auto-adds `/0/query`)
> - Works with: `https://services.arcgis.com/.../FeatureServer/0` or `.../MapServer/31` (auto-adds `/query`)
> - Works with: `https://services.arcgis.com/.../FeatureServer/0/query` (complete URL)
> - **New!** Supports both FeatureServer AND MapServer endpoints
> 
> **⚠️ Important**: Make sure your URL is valid! Check that:
> - The service actually exists (test the URL in your browser by adding `?f=json`)
> - Path capitalization is correct (some servers use `/ArcGIS/`, not `/arcgis/`)
> - For custom portals, use browser DevTools Network tab to find the actual REST service URL

### 3. Advanced Usage with Configuration
```bash
# Create a sample config
python universal_scraper.py --create-config my_config.json

# Edit the config file with your URL and settings
# Then run with config
python universal_scraper.py --config my_config.json
```

### 4. Deploy Your Changes
```bash
# Automatically commit and push to scrapington.git
python deploy.py
```

## 📁 What's Included

- **`universal_scraper.py`** - Main scraper script (production-ready)
- **`config.json`** - Sample configuration file
- **`deploy.py`** - One-command deployment script
- **`requirements.txt`** - All dependencies
- **`setup.py`** - Python package configuration
- **`geojson_export/`** - Output directory for scraped data
- **Legacy scripts** - `extract_*.py` for reference

## 🎯 Universal Scraper Usage

### Command Line Options
```bash
python universal_scraper.py --help
```

**Basic Options:**
- `--url` - ArcGIS Feature Service URL (required)
- `--output` - Output filename (default: scraped_data.geojson)
- `--config` - Use configuration file instead of command line

**Advanced Options:**
- `--where` - WHERE clause for filtering (default: 1=1)
- `--fields` - Fields to retrieve (default: *)
- `--max-records` - Maximum records to fetch
- `--batch-size` - Batch size for requests (default: 1000)
- `--timeout` - Request timeout in seconds (default: 60)
- `--no-validate` - Skip geometry validation
- `--no-normalize` - Skip attribute normalization
- `--quiet` - Suppress output messages

### Configuration File Format
```json
{
  "url": "https://services.arcgis.com/.../FeatureServer/0/query",
  "output_file": "my_data.geojson",
  "output_dir": "geojson_export",
  "where_clause": "1=1",
  "out_fields": "*",
  "spatial_reference": 4326,
  "max_records": 1000,
  "batch_size": 1000,
  "timeout": 60,
  "retry_attempts": 3,
  "retry_delay": 1.0,
  "validate_geometry": true,
  "normalize_attributes": true,
  "verbose": true
}
```

## 🔧 Advanced Features

### Data Quality & Validation
- **Geometry Validation**: Automatically validates and fixes invalid geometries
- **Attribute Normalization**: Converts field names to snake_case, handles special characters
- **Error Recovery**: Retries failed requests with exponential backoff
- **Progress Tracking**: Real-time progress updates for large datasets

### Performance Optimization
- **Intelligent Pagination**: Handles large datasets efficiently
- **Batch Processing**: Configurable batch sizes for optimal performance
- **Memory Management**: Streams data to avoid memory issues
- **Rate Limiting**: Respectful delays between requests

### Output Format
All outputs are valid GeoJSON FeatureCollection with metadata:
```json
{
  "type": "FeatureCollection",
  "features": [...],
  "metadata": {
    "source_url": "https://services.arcgis.com/...",
    "total_features": 1234,
    "processed_features": 1234,
    "scraped_at": "2024-01-15 14:30:00",
    "config": {...}
  }
}
```

## 🚀 Deployment & Production

### One-Command Deploy
```bash
# Automatically commit and push all changes
python deploy.py
```

### Manual Git Workflow
```bash
git add .
git commit -m "Add new scraper configuration"
git push origin main
```

### Package Installation
```bash
# Install as a Python package
pip install -e .

# Now you can use the 'scrapington' command anywhere
scrapington --url "https://services.arcgis.com/..." --output "data.geojson"
```

## 📊 Real-World Examples

### Example 1: School Enrollment Boundaries
```bash
python universal_scraper.py \
  --url "https://services.arcgis.com/P3ePLMYs2RVChkJx/ArcGIS/rest/services/ACS_School_Enrollment_Boundaries/FeatureServer/0" \
  --output "school_boundaries.geojson" \
  --max-records 100
```

### Example 2: Public Schools
```bash
python universal_scraper.py \
  --url "https://services.arcgis.com/P3ePLMYs2RVChkJx/ArcGIS/rest/services/HIFLD_Public_Schools_Placekey/FeatureServer" \
  --output "public_schools.geojson" \
  --max-records 1000
```

### Example 3: Custom ArcGIS Server (services6.arcgis.com)
```bash
# Works with any ArcGIS domain!
python universal_scraper.py \
  --url "https://services6.arcgis.com/aROFfSNHbmHPb6wX/arcgis/rest/services/County_Commission_HUB/FeatureServer" \
  --output "county_commission.geojson"
```

### Example 3.5: MapServer Endpoints (not just FeatureServer!)
```bash
# Works with MapServer too! (e.g., from custom GIS portals)
python universal_scraper.py \
  --url "https://web6.kcsgis.com/kcsgis/rest/services/Baldwin/Baldwin_Public_ISV/MapServer/31" \
  --output "baldwin_parcels.geojson" \
  --max-records 10000
```

> **💡 Discovery Tip**: Many custom mapping websites (like county parcel viewers) use ArcGIS services under the hood. 
> Open your browser's Network tab, look for requests to `/rest/services/`, and you can often find the direct MapServer or FeatureServer URLs!

### Example 4: Using Configuration
```bash
# Create config
python universal_scraper.py --create-config schools.json

# Edit schools.json with your URL and settings
# Then run
python universal_scraper.py --config schools.json
```

### Example 5: Large Dataset with Custom Settings
```bash
python universal_scraper.py \
  --url "https://services.arcgis.com/..." \
  --output "large_dataset.geojson" \
  --batch-size 500 \
  --max-records 50000 \
  --timeout 120
```

## 🛠️ Development & Customization

### Adding Custom Transformations
The universal scraper is designed to be extensible. You can modify the `_process_features` method to add custom data transformations.

### Error Handling
The scraper includes comprehensive error handling:
- Network timeouts and retries
- Invalid geometry detection and fixing
- Malformed data handling
- Progress tracking and recovery

### Recent Improvements
- **Fixed URL Encoding**: Special characters like `=` and `*` are now properly handled for ArcGIS compatibility
- **Windows Console Support**: Removed emoji characters that caused encoding errors on Windows
- **Better Error Messages**: Clearer indication when services don't exist or URLs are invalid
- **Smart URL Normalization**: Automatically adds `/0/query` to incomplete URLs
- **Multi-Domain Support**: Works with any ArcGIS domain (`services.arcgis.com`, `services6.arcgis.com`, etc.)
- **MapServer Support**: Now works with both FeatureServer and MapServer endpoints
- **Custom GIS Portals**: Can scrape from custom mapping portals that use ArcGIS REST APIs

### Technical Details
The scraper uses proper URL encoding for ArcGIS services:
- Characters like `=`, `*`, `<`, `>`, and `,` are kept unencoded
- This prevents the `where=1=1` from becoming `where=1%3D1`
- ArcGIS servers expect these characters in their raw form

**Smart URL Handling:**
- If you provide `https://.../FeatureServer` or `.../MapServer`, it automatically adds `/0/query`
- If you provide `https://.../FeatureServer/5` or `.../MapServer/31`, it automatically adds `/query`
- URLs ending with `/query` are used as-is
- Works with both FeatureServer and MapServer endpoints

### Testing
```bash
# Run tests
pytest

# Test with sample data
python universal_scraper.py --create-config test.json
python universal_scraper.py --config test.json
```

## 📋 Troubleshooting

### Common Issues

#### 1. **"400 Bad Request" Errors**
This usually means one of two things:

**A. Invalid Service URL** - The service doesn't exist
- Verify the service exists by visiting the base URL in your browser
- Check for typos in the service name
- Note that service names are case-sensitive

**B. Path Capitalization Matters**
- Some ArcGIS servers require `/ArcGIS/` (capital letters) not `/arcgis/`
- Example: `https://services.arcgis.com/.../ArcGIS/rest/services/...`

#### 2. **How to Find Valid Service URLs**
If you're unsure about a service name, query the server's service directory:

```bash
# List all services on a server
https://services.arcgis.com/YOUR_SERVER_ID/arcgis/rest/services?f=json

# Or use Python to search
python -c "import requests, json; \
  r = requests.get('https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services?f=json'); \
  services = [s['name'] for s in r.json().get('services', [])]; \
  print('\n'.join(services))"
```

#### 3. **"No features found"**
- Check your WHERE clause syntax
- Verify field names match the service schema
- Try with default `--where "1=1"` first

#### 4. **"Timeout errors"**
- Increase timeout: `--timeout 120`
- Reduce batch size: `--batch-size 500`
- Check your internet connection

#### 5. **"Memory issues"**
- Reduce batch size: `--batch-size 100`
- Limit max records: `--max-records 10000`
- Process data in smaller chunks

#### 6. **Unicode/Emoji Errors on Windows**
- These have been fixed in the latest version
- Update your `universal_scraper.py` if you see emoji-related errors

### Getting Help
- **Verify the service exists**: Check the URL in a browser first
- **Use verbose mode**: Add `--verbose` flag for detailed logging
- **Start small**: Test with `--max-records 5` before downloading large datasets
- **Check service capabilities**: Visit `SERVICE_URL?f=json` to see available fields and settings
- **Validate your query**: Test WHERE clauses with small limits first

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your scraper or improvements
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.


