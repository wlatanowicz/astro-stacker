import logging
from logging import getLogger
from sys import argv

import astroalign as aa

from . import value_objects

logger = logging.getLogger(__name__)


if __name__ == "__main__":

    base_file_path = argv[1]
    target_file_paths = argv[2:]

    base_image = value_objects.ImageFile.load(base_file_path)
    if not base_image.meta.stars:
        raise Exception("Base file %s not registered", base_file_path)

    for target_file_path in target_file_paths:
        target_image = value_objects.ImageFile.load(target_file_path)

        if not target_image.meta.stars:
            logger.error("Target file %s not registered", target_file_path)

        else:
            logger.error("Aligning file %s", target_file_path)

            transformation, (s_list, t_list) = aa.find_transform(base_image.meta.stars_as_tuples, target_image.meta.stars_as_tuples)
            if target_image.meta.transformations is None:
                target_image.meta.transformations = {}

            target_image.meta.transformations[base_image.meta.uuid] = transformation.params
            target_image.save()
