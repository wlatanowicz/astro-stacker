import click
from . import value_objects
import logging


logger = logging.getLogger(__name__)


@click.group()
def cli():
    pass


@cli.command()
@click.option('-f', '--force', 'overwrite', is_flag=True)
@click.argument('file_path', nargs=-1)
def register(overwrite: bool, file_path):
    from .register import find_stars

    for fp in file_path:
        image = value_objects.ImageFile.load(fp)

        if not overwrite and image.meta.stars is not None:
            logger.warning("File %s already registred", fp)
        else:
            logger.info("Registering %s", fp)
            stars = find_stars(image.image)
            image.meta.stars = stars
            image.save()


@cli.command()
def align():
    ...


@cli.command()
def stack():
    ...


if __name__ == "__main__":
    cli()
