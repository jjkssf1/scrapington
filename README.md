## Scrapington

A tiny, script-first workspace for extracting geospatial layers (GeoJSON) from public map sources.

### What’s here
- **Scripts**: Small Python scripts like `extract_arcgis_geojson.py`, `extract_nlcog_map.py`, `extract_school_districts.py`.
- **Exports**: GeoJSON files under `geojson_export/`.

### Quick start
1. **Install Python 3.10+**
2. **Create a virtual environment**
   - macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```
   - Windows (PowerShell):
```bash
py -m venv .venv
.venv\Scripts\Activate.ps1
```
3. **Install common dependencies** (if your script needs them):
```bash
pip install requests shapely pyproj pandas tqdm
```
4. **Run a script**:
```bash
python extract_school_districts.py
```
5. **Find outputs** in `geojson_export/`.

### Conventions for new scraper scripts
- **One job per file**: Each script should do one clear extraction task end-to-end.
- **Deterministic outputs**: Write results to `geojson_export/` using stable filenames.
- **Log plainly**: Print high-signal messages; avoid noisy logs.
- **Fail clearly**: Raise with context (HTTP code, layer ids, URLs) so issues are debuggable.
- **Small, pure helpers**: Separate network fetch, transform, and write steps into small functions.
- **No secrets in code**: Read tokens/keys from environment variables when needed.

### Recommended file layout
- `extract_<source>_<layer>.py` — single-purpose scraper
- `geojson_export/` — final GeoJSON outputs

### Minimal script template
Use this as a starting point for new scrapers.
```python
#!/usr/bin/env python3
import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List

import requests


@dataclass
class ExportConfig:
    output_dir: str = "geojson_export"
    output_file: str = "example.geojson"

    @property
    def output_path(self) -> str:
        os.makedirs(self.output_dir, exist_ok=True)
        return os.path.join(self.output_dir, self.output_file)


def fetch_json(url: str, params: Dict[str, Any] | None = None, headers: Dict[str, str] | None = None) -> Dict[str, Any]:
    response = requests.get(url, params=params, headers=headers, timeout=60)
    response.raise_for_status()
    return response.json()


def to_feature_collection(features: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {"type": "FeatureCollection", "features": features}


def write_geojson(path: str, data: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main() -> None:
    cfg = ExportConfig()

    # Example: ArcGIS FeatureServer query endpoint (replace with your own)
    url = "https://services.arcgis.com/<org>/arcgis/rest/services/<layer>/FeatureServer/0/query"
    params = {
        "where": "1=1",
        "outFields": "*",
        "f": "geojson",
        "outSR": 4326,
    }

    print("Fetching features…")
    data = fetch_json(url, params=params)

    # If your endpoint already returns valid GeoJSON FeatureCollection, you can write directly.
    # Otherwise, transform to GeoJSON here.
    if data.get("type") != "FeatureCollection":
        data = to_feature_collection(data.get("features", []))

    print(f"Writing {cfg.output_path}")
    write_geojson(cfg.output_path, data)
    print("Done.")


if __name__ == "__main__":
    main()
```

### ArcGIS/FeatureServer tips
- **Prefer `f=geojson`** when available. If only `f=json` is supported, you’ll need to map Esri JSON to GeoJSON.
- **Paginate** large layers using `resultOffset`/`resultRecordCount`, or `where` filtering.
- **Spatial reference**: Request `outSR=4326` for WGS84 when possible.
- **Attributes**: Use `outFields=*` or specify exactly what you need for smaller payloads.

### Data quality and transforms
- Validate geometry types and fix invalid polygons if needed (e.g., via Shapely `buffer(0)`).
- Normalize attribute names and values — keep them lowercase, snake_case, and consistent.
- Keep CRS as WGS84 (EPSG:4326) for GeoJSON outputs.

### Testing locally
```bash
python -m pip install pytest
pytest -q
```

### Adding a new script: checklist
- Script name is clear and specific
- Prints concise progress messages
- Handles HTTP failures and empty results
- Writes to `geojson_export/<your_file>.geojson`
- Leaves no temp files in the repo

### Contributing
Open a PR adding your new script and exported GeoJSON file(s). Keep diffs small and focused.


