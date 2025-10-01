import json, math, os, re, time
import urllib.parse, urllib.request

APP_ID = "dc701db95ad540e6b79f5e7a7d984cd1"
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

# 1) App config -> get webmap id
print(f"Getting app config for {APP_ID}...")
app_data = get_json(f"https://www.arcgis.com/sharing/rest/content/items/{APP_ID}/data?f=pjson")
webmap_id = app_data.get("webmap") or app_data.get("values", {}).get("webmap")
if not webmap_id:
    raise SystemExit("Could not find webmap id in app data.")

print(f"Found webmap ID: {webmap_id}")

# 2) WebMap data -> get layer URLs and titles
print("Getting webmap data...")
wm_data = get_json(f"https://www.arcgis.com/sharing/rest/content/items/{webmap_id}/data?f=pjson")
layers = []
for lyr in wm_data.get("operationalLayers", []):
    url = lyr.get("url")
    title = lyr.get("title") or lyr.get("id") or "layer"
    if url:
        layers.append({"title": title, "url": url})
        print(f"Found layer: {title} -> {url}")

if not layers:
    raise SystemExit("No operational layer URLs found in the webmap.")

print(f"\nFound {len(layers)} layers total")

# 3) For each layer, detect maxRecordCount and page to GeoJSON
for L in layers:
    base = L["url"].rstrip("/")
    print(f"\nProcessing layer: {L['title']}")
    
    try:
        info = get_json(f"{base}?f=pjson")
        max_count = info.get("maxRecordCount", 2000)
        title_sanitized = re.sub(r"[^A-Za-z0-9_-]+", "_", L["title"]).strip("_") or "layer"

        # Count records (optional but nice)
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
            print(f"  Saved page {i+1}/{pages} to {part_path}")
            time.sleep(0.2)  # be polite

    except Exception as e:
        print(f"Error processing layer {L['title']}: {e}")
        continue

print(f"\nDone. Files in: {os.path.abspath(OUT_DIR)}")

