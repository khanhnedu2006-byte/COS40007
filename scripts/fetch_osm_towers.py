"""Download telecom masts/towers in Hanoi from OpenStreetMap (Overpass API).

OpenCelliD positions are estimated from phone measurements and cluster along main roads;
OSM masts can fill gaps in the suburbs. Run on a machine with normal internet access:
    python scripts/fetch_osm_towers.py
Output: data/raw/osm_comm_towers.csv (osm_id, latitude, longitude, operator, tags)
"""
import json
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

# Thử lần lượt các server Overpass, server nào trả lời trước thì dùng
OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]
# Dùng khung bao Hà Nội (không dùng area theo mã ISO vì có thể không khớp tag trên OSM)
BBOX = "20.54,105.35,21.41,106.08"  # nam, tây, bắc, đông
QUERY = f"""
[out:json][timeout:60];
(
  nwr["man_made"~"^(mast|tower|communications_tower)$"]({BBOX});
  nwr["tower:type"~"communication"]({BBOX});
  nwr["communication:mobile_phone"]({BBOX});
  nwr["telecom"]({BBOX});
);
out center tags;
"""
OUT = Path(__file__).resolve().parents[1] / "data" / "raw" / "osm_comm_towers.csv"


def main() -> None:
    data = urllib.parse.urlencode({"data": QUERY}).encode()
    elements = None
    for url in OVERPASS_URLS:
        print(f"Trying {url} ...", flush=True)
        req = urllib.request.Request(url, data=data, headers={"User-Agent": "COS40007-Group5-speedmap/0.1"})
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                elements = json.load(resp)["elements"]
            break
        except Exception as exc:  # server bận hoặc quá thời gian: thử server khác
            print(f"  failed: {exc}")
    if elements is None:
        raise SystemExit("All Overpass servers failed; try again later.")
    rows = []
    for el in elements:
        # node có lat/lon; way/relation dùng toạ độ tâm
        lat = el.get("lat", el.get("center", {}).get("lat"))
        lon = el.get("lon", el.get("center", {}).get("lon"))
        tags = el.get("tags", {})
        rows.append({"osm_id": f"{el['type']}/{el['id']}", "latitude": lat, "longitude": lon,
                     "operator": tags.get("operator", ""), "tags": json.dumps(tags, ensure_ascii=False)})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows, columns=["osm_id", "latitude", "longitude", "operator", "tags"])
    df.to_csv(OUT, index=False)
    print(f"{len(df)} OSM objects -> {OUT}")
    if len(df):
        # Thống kê nhanh loại đối tượng để biết cái nào thật sự là trạm viễn thông
        tags = df["tags"].map(json.loads)
        kinds = tags.map(lambda t: f"man_made={t.get('man_made', '-')}, tower:type={t.get('tower:type', '-')}")
        print(kinds.value_counts().to_string())


if __name__ == "__main__":
    main()
