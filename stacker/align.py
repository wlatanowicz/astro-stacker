import value_objects
import astroalign as aa
from sys import argv


if __name__ == "__main__":

    base_file_path = argv[1]
    target_file_path = argv[2]

    base_image = value_objects.ImageFile.load(base_file_path)
    target_image = value_objects.ImageFile.load(target_file_path)

    if not base_image.meta.stars:
        raise Exception("Base file not registered")

    if not target_image.meta.stars:
        raise Exception("Target file not registered")


    transformation, (s_list, t_list) = aa.find_transform(base_image.meta.stars_as_tuples, target_image.meta.stars_as_tuples)
    print(transformation)
    if target_image.meta.transformations is None:
        target_image.meta.transformations = {}

    target_image.meta.transformations[base_image.meta.uuid] = transformation.params
    target_image.save()
