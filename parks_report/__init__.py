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
