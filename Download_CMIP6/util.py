import re
from typing import Iterable

CATALOG_URL = "https://storage.googleapis.com/cmip6/pangeo-cmip6.json"


def natural_sort(l: Iterable[str]) -> list[str]:
    """
    Sort names like r1i1p1f1, r1i2p1f1 in a natural (numeric) order.
    - r1: Realization (initial condition run),
    - i1: Initialization method,
    - p1: Physical parameters,
    - f1: External forcings.

    Numeric order means that r1i1p1f1 < r2i1p1f1 < r11i1p1f1.

    :param l: list of names to be sorted
    """

    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split("([0-9]+)", key)]
    return sorted(l, key=alphanum_key)
