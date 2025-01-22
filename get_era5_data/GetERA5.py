# following https://dreambooker.site/2019/10/03/initializing-the-wrf-model-with-era5-pressure-level/

import os
from typing import Literal

import cdsapi
import fire
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# fmt: off
PRESSURE_LEVELS = [
    "1", "2", "3", "5", "7", "10", "20", "30", "50", "70", "100", "125",
    "150", "175", "200", "225", "250", "300", "350", "400", "450", "500",
    "550", "600", "650", "700", "750", "775", "800", "825", "850", "875",
    "900", "925", "950", "975", "1000",
]
# fmt: on

SINGLE_LEVEL_PARAMS = {
    "product_type": ["reanalysis"],
    "data_format": "grib",
    "variable": [
        "10m_u_component_of_wind",
        "10m_v_component_of_wind",
        "2m_dewpoint_temperature",
        "2m_temperature",
        "land_sea_mask",
        "mean_sea_level_pressure",
        "sea_ice_cover",
        "sea_surface_temperature",
        "skin_temperature",
        "snow_depth",
        "soil_temperature_level_1",
        "soil_temperature_level_2",
        "soil_temperature_level_3",
        "soil_temperature_level_4",
        "surface_pressure",
        "volumetric_soil_water_layer_1",
        "volumetric_soil_water_layer_2",
        "volumetric_soil_water_layer_3",
        "volumetric_soil_water_layer_4",
    ],
    "time": "00/to/23/by/1",
}

PRESSURE_LEVELS_PARAMS = {
    "product_type": ["reanalysis"],
    "data_format": "grib",
    "pressure_level": PRESSURE_LEVELS,
    "time": "00/to/23/by/1",
    "variable": [
        "geopotential",
        "relative_humidity",
        "specific_humidity",
        "temperature",
        "u_component_of_wind",
        "v_component_of_wind",
    ],
}


def download_file(url, local_filename, expected_size=None):
    # Set up a session with retry strategy
    session = requests.Session()
    retry = Retry(
        total=5,  # Total number of retries
        backoff_factor=0.3,  # A backoff factor to apply between attempts
        status_forcelist=[500, 502, 503, 504],  # Retry on these HTTP status codes
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # Stream the download to avoid loading the entire file into memory
    with session.get(url, stream=True) as response:
        response.raise_for_status()  # Raise an exception for HTTP errors
        with open(local_filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)

    # Verify the file size if expected_size is provided
    if expected_size is not None:
        actual_size = os.path.getsize(local_filename)
        if actual_size != expected_size:
            raise ValueError(
                f"Downloaded file size ({actual_size}) does not match expected size ({expected_size})"
            )

    print(f"File downloaded successfully: {local_filename}")


def download(
    level: Literal["pl", "sl"],
    date1: str,
    date2: str | None = None,
    area: tuple[float, float, float, float] | None = None,
    output_file: str | None = None,
    dry_run: bool = False,
):
    """Download ERA5 single-level or pressure-level data.

    Args:
        level: Data level to download. Either "pl" for pressure levels or "sl" for single level.
        date1: Start date in the format "YYYYMMDD".
        date2: End date in the format "YYYYMMDD".
        area: Bounding box of the area of interest (north, west, south, east). Defaults to None.
        output_file: Output file name. Defaults to ERA5-{date1}-{date2}-{level}.grib.
    """

    if date2 is None:
        date2 = date1

    if level == "pl":
        params = PRESSURE_LEVELS_PARAMS.copy()
        product = "reanalysis-era5-pressure-levels"
    else:
        params = SINGLE_LEVEL_PARAMS.copy()
        product = "reanalysis-era5-single-levels"

    params["date"] = f"{date1}/{date2}"
    if area is not None:
        params["area"] = list(area)

    if output_file is None:
        output_file = f"ERA5-{date1}-{date2}-{level}.grib"

    if dry_run:
        print(level, date1, date2, area, output_file)
        return

    c = cdsapi.Client()

    # This should work, but some how it's very unstable recently
    # c.retrieve(product, params, output_file)

    res = c.retrieve(product, params)
    download_file(res.location, output_file, res.content_length)


if __name__ == "__main__":
    fire.Fire(download)
