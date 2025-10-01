import json, math, os, re, time
import urllib.parse, urllib.request

# Direct webmap ID from the URL you provided
WEBMAP_ID = "20b3b4b3e0a74d3e8596c980f39c7aae"
OUT_DIR = "geojson_export"
TOKEN = None  # if needed, set a valid ArcGIS Online token string here

os.makedirs(OUT_DIR, exist_ok=True)

def get_json(url):
    if TOKEN:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}token={urllib.parse.quote(TOKEN)}"
    with urllib.request.urlopen(url) as r:
        return json.loads(r.read().decode("utf-8"))

def save_geojson(url, outfile):
    with urllib.request.urlopen(url) as r:
        with open(outfile, "wb") as f:
            f.write(r.read())

def q(params):
    return urllib.parse.urlencode(params, doseq=True, safe="=><,*")

print(f"Processing webmap ID: {WEBMAP_ID}")

# Get WebMap data -> find all layers
print("Getting webmap data...")
wm_data = get_json(f"https://www.arcgis.com/sharing/rest/content/items/{WEBMAP_ID}/data?f=pjson")

# Collect all layers
all_layers = []

for lyr in wm_data.get("operationalLayers", []):
    url = lyr.get("url")
    title = lyr.get("title") or lyr.get("id") or "layer"
    if url:
        all_layers.append({"title": title, "url": url})
        print(f"Found layer: {title}")
        print(f"  URL: {url}")

print(f"\nFound {len(all_layers)} layers total")

if not all_layers:
    print("No operational layer URLs found in the webmap.")
    exit()

# Process all layers
for L in all_layers:
    base = L["url"].rstrip("/")
    print(f"\n{'='*80}")
    print(f"Processing layer: {L['title']}")
    print(f"{'='*80}")
    
    try:
        info = get_json(f"{base}?f=pjson")
        max_count = info.get("maxRecordCount", 2000)
        title_sanitized = re.sub(r"[^A-Za-z0-9_-]+", "_", L["title"]).strip("_") or "layer"

        # Count records
        count_params = {
            "where": "1=1",
            "returnCountOnly": "true",
            "f": "json"
        }
        count_url = f"{base}/query?{q(count_params)}"
        total = get_json(count_url).get("count", 0)
        pages = max(1, math.ceil(total / max_count)) if total else 1

        print(f"Exporting {title_sanitized} ({total} features, ~{pages} page(s))")

        features_paths = []
        for i in range(pages):
            params = {
                "where": "1=1",
                "outFields": "*",
                "returnGeometry": "true",
                "outSR": "4326",
                "f": "geojson",
                "resultRecordCount": str(max_count),
                "resultOffset": str(i * max_count),
            }
            url = f"{base}/query?{q(params)}"
            part_path = os.path.join(OUT_DIR, f"{title_sanitized}_{i+1:03d}.geojson" if pages > 1 else f"{title_sanitized}.geojson")
            save_geojson(url, part_path)
            features_paths.append(part_path)
            print(f"  ✓ Saved page {i+1}/{pages} to {part_path}")
            time.sleep(0.2)  # be polite

    except Exception as e:
        print(f"  ✗ Error processing layer {L['title']}: {e}")
        continue

print(f"\n{'='*80}")
print(f"Done. Files in: {os.path.abspath(OUT_DIR)}")
print(f"{'='*80}")

