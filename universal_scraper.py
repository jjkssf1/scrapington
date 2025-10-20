#!/usr/bin/env python3
"""
Universal GeoJSON Scraper for ArcGIS Feature Services

A production-ready script that can extract GeoJSON data from any ArcGIS Feature Service
by simply configuring the URL and parameters. Handles pagination, error recovery,
and data validation automatically.

Usage:
    python universal_scraper.py --url "https://services.arcgis.com/..." --output "my_data.geojson"
    python universal_scraper.py --config config.json
"""

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse, parse_qs

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


@dataclass
class ScraperConfig:
    """Configuration for the universal scraper."""
    url: str
    output_file: str = "scraped_data.geojson"
    output_dir: str = "geojson_export"
    where_clause: str = "1=1"
    out_fields: str = "*"
    spatial_reference: int = 4326
    max_records: int = 1000
    batch_size: int = 1000
    timeout: int = 60
    retry_attempts: int = 3
    retry_delay: float = 1.0
    validate_geometry: bool = True
    normalize_attributes: bool = True
    verbose: bool = True

    @property
    def output_path(self) -> str:
        """Get the full output path."""
        os.makedirs(self.output_dir, exist_ok=True)
        return os.path.join(self.output_dir, self.output_file)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScraperConfig':
        """Create from dictionary."""
        return cls(**data)

    @classmethod
    def from_json(cls, filepath: str) -> 'ScraperConfig':
        """Load configuration from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)

    def save_json(self, filepath: str) -> None:
        """Save configuration to JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)


class UniversalScraper:
    """Universal scraper for ArcGIS Feature Services."""

    def __init__(self, config: ScraperConfig):
        self.config = config
        self.session = self._create_session()
        self.total_features = 0
        self.processed_features = 0

    def _create_session(self) -> requests.Session:
        """Create a requests session with retry strategy."""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=self.config.retry_attempts,
            backoff_factor=self.config.retry_delay,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session

    def _log(self, message: str) -> None:
        """Log message if verbose mode is enabled."""
        if self.config.verbose:
            print(f"[{time.strftime('%H:%M:%S')}] {message}")

    def _validate_url(self, url: str) -> bool:
        """Validate that the URL is a proper ArcGIS Feature Service endpoint."""
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Check if it looks like an ArcGIS service
            if 'arcgis.com' not in parsed.netloc and 'arcgis' not in parsed.netloc:
                self._log("Warning: URL doesn't appear to be an ArcGIS service")
            
            return True
        except Exception:
            return False

    def _get_service_info(self) -> Dict[str, Any]:
        """Get basic information about the service."""
        try:
            # Remove query parameters and add service info endpoint
            base_url = self.config.url.split('?')[0]
            if base_url.endswith('/query'):
                base_url = base_url.replace('/query', '')
            
            info_url = f"{base_url}?f=json"
            response = self.session.get(info_url, timeout=self.config.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self._log(f"Warning: Could not fetch service info: {e}")
            return {}

    def _fetch_batch(self, offset: int = 0) -> Dict[str, Any]:
        """Fetch a batch of features from the service."""
        params = {
            'where': self.config.where_clause,
            'outFields': self.config.out_fields,
            'f': 'geojson',
            'outSR': self.config.spatial_reference,
            'resultOffset': offset,
            'resultRecordCount': self.config.batch_size,
        }

        self._log(f"Fetching batch: offset={offset}, batch_size={self.config.batch_size}")
        
        try:
            response = self.session.get(
                self.config.url,
                params=params,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self._log(f"Error fetching batch at offset {offset}: {e}")
            raise

    def _normalize_attributes(self, feature: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize feature attributes to consistent format."""
        if not self.config.normalize_attributes:
            return feature

        if 'properties' not in feature:
            return feature

        normalized_props = {}
        for key, value in feature['properties'].items():
            # Convert to lowercase, snake_case
            normalized_key = key.lower().replace(' ', '_').replace('-', '_')
            # Clean up the key
            normalized_key = ''.join(c for c in normalized_key if c.isalnum() or c == '_')
            if normalized_key and not normalized_key[0].isdigit():
                normalized_props[normalized_key] = value

        feature['properties'] = normalized_props
        return feature

    def _validate_geometry(self, feature: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and fix geometry if needed."""
        if not self.config.validate_geometry:
            return feature

        try:
            # Basic geometry validation
            if 'geometry' not in feature:
                self._log(f"Warning: Feature missing geometry: {feature.get('id', 'unknown')}")
                return feature

            geom = feature['geometry']
            if not geom or geom.get('type') not in ['Point', 'LineString', 'Polygon', 'MultiPoint', 'MultiLineString', 'MultiPolygon']:
                self._log(f"Warning: Invalid geometry type: {geom.get('type', 'none')}")
                return feature

            # Check for required coordinates
            if 'coordinates' not in geom or not geom['coordinates']:
                self._log(f"Warning: Feature missing coordinates: {feature.get('id', 'unknown')}")
                return feature

            return feature
        except Exception as e:
            self._log(f"Warning: Geometry validation error: {e}")
            return feature

    def _process_features(self, features: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and validate a list of features."""
        processed = []
        for feature in features:
            try:
                # Normalize attributes
                feature = self._normalize_attributes(feature)
                
                # Validate geometry
                feature = self._validate_geometry(feature)
                
                processed.append(feature)
                self.processed_features += 1
                
            except Exception as e:
                self._log(f"Error processing feature: {e}")
                continue

        return processed

    def scrape(self) -> Dict[str, Any]:
        """Main scraping method that handles pagination and data collection."""
        if not self._validate_url(self.config.url):
            raise ValueError(f"Invalid URL: {self.config.url}")

        self._log(f"Starting scrape of: {self.config.url}")
        
        # Get service info
        service_info = self._get_service_info()
        if service_info:
            self._log(f"Service: {service_info.get('serviceName', 'Unknown')}")
            self._log(f"Description: {service_info.get('serviceDescription', 'No description')}")

        all_features = []
        offset = 0
        batch_count = 0

        while True:
            try:
                # Fetch batch
                batch_data = self._fetch_batch(offset)
                
                # Check if we got valid GeoJSON
                if batch_data.get('type') == 'FeatureCollection':
                    features = batch_data.get('features', [])
                elif 'features' in batch_data:
                    features = batch_data['features']
                else:
                    self._log("Warning: Unexpected response format")
                    break

                if not features:
                    self._log("No more features found")
                    break

                # Process features
                processed_features = self._process_features(features)
                all_features.extend(processed_features)
                
                batch_count += 1
                self._log(f"Batch {batch_count}: {len(processed_features)} features processed")
                
                # Check if we should continue
                if len(features) < self.config.batch_size:
                    self._log("Reached end of data")
                    break
                
                if self.config.max_records and len(all_features) >= self.config.max_records:
                    self._log(f"Reached max records limit: {self.config.max_records}")
                    all_features = all_features[:self.config.max_records]
                    break

                offset += len(features)
                
                # Small delay to be respectful to the server
                time.sleep(0.1)

            except Exception as e:
                self._log(f"Error in batch {batch_count + 1}: {e}")
                if batch_count == 0:
                    raise
                break

        self.total_features = len(all_features)
        self._log(f"Scraping complete: {self.total_features} features collected")

        return {
            'type': 'FeatureCollection',
            'features': all_features,
            'metadata': {
                'source_url': self.config.url,
                'total_features': self.total_features,
                'processed_features': self.processed_features,
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'config': self.config.to_dict()
            }
        }

    def save(self, data: Dict[str, Any]) -> str:
        """Save the scraped data to file."""
        output_path = self.config.output_path
        
        self._log(f"Saving {self.total_features} features to: {output_path}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        file_size = os.path.getsize(output_path)
        self._log(f"File saved: {file_size:,} bytes")
        
        return output_path


def create_sample_config(output_file: str = "sample_config.json") -> None:
    """Create a sample configuration file."""
    sample_config = ScraperConfig(
        url="https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Counties_Generalized/FeatureServer/0/query",
        output_file="usa_counties.geojson",
        where_clause="1=1",
        out_fields="*",
        max_records=1000,
        batch_size=1000
    )
    
    sample_config.save_json(output_file)
    print(f"Sample configuration created: {output_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Universal GeoJSON Scraper for ArcGIS Feature Services",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with URL
  python universal_scraper.py --url "https://services.arcgis.com/..." --output "data.geojson"
  
  # Use configuration file
  python universal_scraper.py --config config.json
  
  # Create sample configuration
  python universal_scraper.py --create-config sample.json
  
  # Advanced usage
  python universal_scraper.py --url "https://services.arcgis.com/..." \\
    --output "schools.geojson" \\
    --where "NAME LIKE '%School%'" \\
    --max-records 5000 \\
    --batch-size 1000
        """
    )

    parser.add_argument('--url', help='ArcGIS Feature Service URL')
    parser.add_argument('--output', help='Output filename (default: scraped_data.geojson)')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--create-config', help='Create sample configuration file')
    parser.add_argument('--where', help='WHERE clause for filtering (default: 1=1)')
    parser.add_argument('--fields', help='Fields to retrieve (default: *)')
    parser.add_argument('--max-records', type=int, help='Maximum records to fetch')
    parser.add_argument('--batch-size', type=int, help='Batch size for requests')
    parser.add_argument('--timeout', type=int, help='Request timeout in seconds')
    parser.add_argument('--no-validate', action='store_true', help='Skip geometry validation')
    parser.add_argument('--no-normalize', action='store_true', help='Skip attribute normalization')
    parser.add_argument('--quiet', action='store_true', help='Suppress output messages')

    args = parser.parse_args()

    # Handle config creation
    if args.create_config:
        create_sample_config(args.create_config)
        return

    # Load configuration
    if args.config:
        try:
            config = ScraperConfig.from_json(args.config)
        except Exception as e:
            print(f"Error loading config file: {e}")
            sys.exit(1)
    else:
        if not args.url:
            print("Error: --url is required when not using --config")
            sys.exit(1)
        
        config = ScraperConfig(url=args.url)
        
        # Apply command line overrides
        if args.output:
            config.output_file = args.output
        if args.where:
            config.where_clause = args.where
        if args.fields:
            config.out_fields = args.fields
        if args.max_records:
            config.max_records = args.max_records
        if args.batch_size:
            config.batch_size = args.batch_size
        if args.timeout:
            config.timeout = args.timeout
        if args.no_validate:
            config.validate_geometry = False
        if args.no_normalize:
            config.normalize_attributes = False
        if args.quiet:
            config.verbose = False

    try:
        # Create scraper and run
        scraper = UniversalScraper(config)
        data = scraper.scrape()
        output_path = scraper.save(data)
        
        print(f"\n✅ Success! Scraped {scraper.total_features} features")
        print(f"📁 Output: {output_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
