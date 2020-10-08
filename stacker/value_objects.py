import json
import hashlib
import uuid
from dacite import from_dict
from typing import Any, Dict, List, Optional
from uuid import uuid5

import imageio
from dataclasses import dataclass, asdict
from matplotlib import image
from numpy.core.numeric import ndarray
from skimage.transform import SimilarityTransform

META_VERSION = "1.0"


class BaseDataClass:
    def to_json(self, *args, **kwargs):
        d = asdict(self)
        return json.dumps(d, *args, **kwargs)

    @classmethod
    def from_json(cls, j):
        d = json.loads(j)
        return from_dict(data_class=cls, data=d)


@dataclass
class Point(BaseDataClass):
    x: float
    y: float


@dataclass
class Star(BaseDataClass):
    position: Point
    radius: float
    fwhm: Optional[float] = None

    @property
    def x(self):
        return self.position.x

    @property
    def y(self):
        return self.position.y

    def __str__(self):
        if self.fwhm is None:
            return f"Star(x={self.x} y={self.y} r={self.radius})"
        else:
            return f"Star(x={self.x} y={self.y} fwhm={self.fwhm})"


@dataclass
class FileMetaData(BaseDataClass):
    md5: str
    uuid: str
    stars: Optional[List[Star]] = None
    transformations: Optional[Dict[str, Any]] = None
    version: str = META_VERSION

    @property
    def stars_as_tuples(self):
        return [
            (s.position.x, s.position.y)
            for s in self.stars
        ]


class ImageFile:
    FILE_TYPE_MAPPING = {
        "arw": "RAW-FI",
    }

    def __init__(self, file_name: str, image: ndarray, meta: FileMetaData):
        self.file_name = file_name
        self.image = image
        self.meta = meta

    @classmethod
    def load(cls, file_name):
        image = cls._load_image(file_name)
        meta = cls._load_meta(file_name) or cls._create_meta(file_name)
        return cls(file_name=file_name, image=image, meta=meta,)

    def save(self):
        self._save_meta()

    @staticmethod
    def _md5(file_name):
        hash_md5 = hashlib.md5()
        with open(file_name, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    @classmethod
    def _load_image(cls, file_name: str):
        format = None
        extension = None
        try:
            extension = file_name.split(".")[-1].lower()
            format = cls.FILE_TYPE_MAPPING[extension]
        except:
            pass

        return imageio.imread(file_name, format=format)

    @classmethod
    def _load_meta(cls, file_name: str):
        try:
            meta_file_name = cls._meta_file_name(file_name)
            with open(meta_file_name, "r") as f:
                meta = FileMetaData.from_json(f.read())

            md5 = cls._md5(file_name)

            if md5 != meta.md5:
                raise ValueError("Meta data checksum doesn't match")

            return meta
        except OSError as e:
            return None

    @staticmethod
    def _meta_file_name(file_name: str) -> str:
        return file_name + ".meta.json"

    def _save_meta(self):
        meta_file_name = self._meta_file_name(self.file_name)
        meta_json = self.meta.to_json(indent=4)
        with open(meta_file_name, "w") as f:
            f.write(meta_json)

    @classmethod
    def _create_meta(cls, file_name):
        md5 = cls._md5(file_name)
        return FileMetaData(md5=md5, uuid=str(uuid.uuid1()),)
