import json
from urllib.request import urlopen
import pandas as pd
from urllib.parse import quote

regions = [
    "E12000001",
    "E12000002",
    "E12000003",
    "E12000004",
    "E12000005",
    "E12000006",
    "E12000007",
    "E12000008",
    "E12000009",
    "W10000001",
    "W10000006",
    "W10000007",
    "W10000008",
    "W10000009",
    ]


def list_authorities(region_code):
    if region_code not in regions:
        raise ValueError(f"Unknown region code: {region_code}")

    url = (
        f"https://raw.githubusercontent.com/Safer-Parks/"
        f"{region_code}/refs/heads/main/{region_code}_lut.geojson"
    )

    with urlopen(url) as response:
        lut = json.load(response)

    authorities = [
        {
            "region_code": feature["properties"]["region_id"],
            "region_name": feature["properties"]["reg_name_e"],
            "authority_code": feature["properties"]["authority_id"],
            "authority_name": feature["properties"]["auth_name_e"],
        }
        for feature in lut["features"]
    ]
    authorities.sort(key=lambda row: row["authority_name"])

    for row in authorities:
        print(
            f"{row['region_code']} ({row['region_name']}) | "
            f"{row['authority_code']} | {row['authority_name']}"
        )

    return authorities

def clean_type(value):
    """Treat missing, empty, and literal 'null' values as missing."""
    if value is None:
        return None

    value = value.strip()
    if not value or value.casefold() == "null":
        return None

    return value


def combine_types(type_os, type_osm):
    """Put OS first, adding OSM only when it is different."""
    type_os = clean_type(type_os)
    type_osm = clean_type(type_osm)

    if type_os and type_osm:
        if type_os.casefold() == type_osm.casefold():
            return type_os
        return f"{type_os}, {type_osm}"

    return type_os or type_osm


def load_authority_parks(authority):
    region_code = authority["region_code"]
    authority_code = authority["authority_code"]
    authority_name = authority["authority_name"]

    filename = quote(f"{authority_name}_parks.geojson", safe="")
    url = (
        f"https://raw.githubusercontent.com/Safer-Parks/"
        f"{region_code}/refs/heads/main/{authority_code}/{filename}"
    )

    with urlopen(url, timeout=60) as response:
        geojson = json.load(response)

    records = []
    for feature in geojson["features"]:
        props = feature["properties"]
        type_os = clean_type(props.get("Type (OS)"))
        type_osm = clean_type(props.get("Type (OSM)"))

        records.append({
            **authority,
            "park_id": props.get("new_park_id"),
            "park_name": props.get("Park Name"),
            "area_m2": props["Total Area (m²)"],
            "type_os": type_os,
            "type_osm": type_osm,
            "park_type": combine_types(type_os, type_osm),
        })

    print(f"{authority_name}: loaded {len(records)} parks")
    return records

def load_parks(authorities):
    columns = [
        "region_code", "region_name",
        "authority_code", "authority_name",
        "park_id", "park_name", "area_m2",
        "type_os", "type_osm", "park_type",
    ]

    park_records = []
    for authority in authorities:
        park_records.extend(load_authority_parks(authority))

    parks = pd.DataFrame.from_records(park_records, columns=columns)
    parks["area_m2"] = pd.to_numeric(parks["area_m2"], errors="raise")

    print(f"Total parks: {len(parks)}")
    print(f"Missing areas: {parks['area_m2'].isna().sum()}")
    print(f"Missing types: {parks['park_type'].isna().sum()}")

    parks.head()
    return parks

def summarise_authorities(parks):
    pass
    
def summarise_regions(parks):
    pass