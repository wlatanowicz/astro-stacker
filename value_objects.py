from typing import List, Optional

from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Point:
    x: float
    y: float

@dataclass_json
@dataclass
class Star:
    position: Point
    radius: float
    fwhm: Optional[float]

@dataclass_json
@dataclass
class FileMetaData:
    file_name: str
    stars: List[Star]
