import logging
from math import ceil, floor
from os import path
from sys import argv

import astroalign as aa
import numpy as np
from scipy import optimize
from skimage.color import rgb2gray
from skimage.feature import blob_log
from skimage.transform import rescale

import value_objects

logger = logging.getLogger(__name__)


def to_gray(image_arr):
    if image_arr.shape == (2,):
        return rgb2gray(image_arr[0])
    if len(image_arr.shape) == 3 and image_arr.shape[2] == 3:
        return rgb2gray(image_arr)
    if len(image_arr.shape) == 2:
        return image_arr


def two_dimensional_gaussian_fit(data):
    def gaussian(height, center_x, center_y, width):
        """Returns a gaussian function with the given parameters"""
        return lambda x, y: height * np.exp(
            -(((center_x - x) / width) ** 2 + ((center_y - y) / width) ** 2) / 2
        )

    def moments(data):
        """Returns (height, x, y, width)
        the gaussian parameters of a 2D distribution by calculating its
        moments """
        total = data.sum()
        X, Y = np.indices(data.shape)
        x = (X * data).sum() / total
        y = (Y * data).sum() / total
        col = data[:, int(y)]
        width = np.sqrt(np.abs((np.arange(col.size) - y) ** 2 * col).sum() / col.sum())
        height = data.max()
        return height, x, y, width

    def fitgaussian(data):
        """Returns (height, x, y, width)
        the gaussian parameters of a 2D distribution found by a fit"""
        params = moments(data)

        def errorfunction(p):
            return np.ravel(gaussian(*p)(*np.indices(data.shape)) - data)

        p, success = optimize.leastsq(errorfunction, params)
        return p

    return fitgaussian(data)


def _find_stars_ballpark(
    gray_image, scale=0.2, min_sigma=3, max_sigma=10, num_sigma=10
):
    if scale != 1:
        gray_image = rescale(gray_image, scale)

    blobs = blob_log(
        gray_image,
        min_sigma=min_sigma * scale,
        max_sigma=max_sigma * scale,
        num_sigma=num_sigma,
    )

    return [
        value_objects.Star(
            position=value_objects.Point(x=b[0] / scale, y=b[1] / scale),
            radius=b[2] * 2 / scale,
        )
        for b in blobs
    ]


def _find_star_refine(
    gray_image,
    star: value_objects.Star,
    scale=5,
    min_sigma=3,
    max_sigma=10,
    num_sigma=10,
):
    logger.warning("Refining star %s", star)

    chunk_radius = star.radius * 2
    chunk_offset = value_objects.Point(
        x=floor(star.x - chunk_radius), y=floor(star.y - chunk_radius),
    )
    chunk_size = ceil(2 * chunk_radius)

    gray_image = gray_image[
        chunk_offset.x : chunk_offset.x + chunk_size,
        chunk_offset.y : chunk_offset.y + chunk_size,
    ]

    if scale != 1:
        gray_image = rescale(gray_image, scale)

    blobs = blob_log(
        gray_image,
        min_sigma=min_sigma * scale,
        max_sigma=max_sigma * scale,
        num_sigma=num_sigma,
    )

    if len(blobs) < 1:
        logger.warning("Refining star %s failed", star)
        return None

    blob = blobs[0]

    return value_objects.Star(
        position=value_objects.Point(
            x=chunk_offset.x + blob[0] / scale, y=chunk_offset.y + blob[1] / scale,
        ),
        radius=blob[2] * 2 / scale,
        fwhm=two_dimensional_gaussian_fit(gray_image)[3] / scale,
    )


def find_stars(img):
    gray_image = to_gray(img)

    return [
        _find_star_refine(gray_image, star)
        for star in _find_stars_ballpark(gray_image)
        if star is not None
    ]


def register_file(file_path):

    image = value_objects.ImageFile.load(file_path)
    stars = find_stars(image.image)
    image.meta.stars = stars
    image.save()

    print(stars)


if __name__ == "__main__":

    register_file(argv[1])

# target_stars = find_stars(target_image)

# print(source_stars)
# print(target_stars)

# transf, (s_list, t_list) = aa.find_transform(source_stars, target_stars)

# print(transf)
