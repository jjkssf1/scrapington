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

### Example 1: School Districts
```bash
python universal_scraper.py \
  --url "https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_School_Districts/FeatureServer/0/query" \
  --output "school_districts.geojson" \
  --where "STATE_NAME = 'California'" \
  --max-records 5000
```

### Example 2: Using Configuration
```bash
# Create config
python universal_scraper.py --create-config schools.json

# Edit schools.json with your URL and settings
# Then run
python universal_scraper.py --config schools.json
```

### Example 3: Large Dataset with Custom Settings
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
1. **"Invalid URL"** - Ensure the URL ends with `/query` and is a valid ArcGIS service
2. **"No features found"** - Check your WHERE clause and field names
3. **"Timeout errors"** - Increase timeout or reduce batch size
4. **"Memory issues"** - Reduce batch size or max records

### Getting Help
- Check the service URL in a browser first
- Use `--verbose` flag for detailed logging
- Test with small datasets first (`--max-records 100`)
- Check the service's field names and capabilities

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your scraper or improvements
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.


