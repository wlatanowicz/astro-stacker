from . import value_objects
import astroalign as aa
from sys import argv

from skimage import io, img_as_float64


if __name__ == "__main__":

    base_file_path = argv[1]

    base_image = value_objects.ImageFile.load(base_file_path)
    stack = img_as_float64(base_image.image)

    for n, i in enumerate(range(2, len(argv))):
        print(n, i)
        target_file_path = argv[i]
        target_image = value_objects.ImageFile.load(target_file_path)

        target_image = img_as_float64(target_image.image)

        stack += (target_image - stack) / (n+2)


    io.imshow(stack)
    io.show()
