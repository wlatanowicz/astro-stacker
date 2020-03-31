import numpy

import astroalign as aa
import imageio
import numpy as np
from skimage.feature import blob_log
from scipy import optimize
from math import ceil, floor
from skimage.color import rgb2gray

import value_objects

#source_image = imageio.imread("x.arw", format="RAW-FI")
source_image = imageio.imread("2.jpg")

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
        return lambda x, y: height * np.exp(-(((center_x - x) / width) ** 2 + ((center_y - y) / width) ** 2) / 2)

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

def find_stars(img):
    gray_img = to_gray(img)

    def star_arr(x, y, radius):
        return gray_img[
                floor(x - radius):ceil(x + radius),
                floor(y - radius):ceil(y + radius),
            ]
            
    blobs = blob_log(gray_img, min_sigma=3)
    return [
        value_objects.Star(
            position=value_objects.Point(x=b[0], y=b[1]),
            radius=b[2]*2,
            fwhm=two_dimensional_gaussian_fit(star_arr(x=b[0], y=b[1], radius=b[2]))[3],
        )
        for b in blobs
    ]

image = value_objects.FileMetaData(
    file_name="",
    stars=find_stars(source_image)
)

print(image.to_json(indent=4))

#target_stars = find_stars(target_image)

#print(source_stars)
#print(target_stars)

#transf, (s_list, t_list) = aa.find_transform(source_stars, target_stars)

#print(transf)
