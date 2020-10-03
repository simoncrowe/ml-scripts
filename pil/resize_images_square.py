from datetime import datetime
import json

import click
from os import path, walk
from PIL import Image, ImageOps



def paths_and_names(directory: str):
    for dirpath, _, filenames in walk(directory):
        print(f'Found {len(filenames)} files in {dirpath}')
        
        for filename in filenames:
            filepath = path.join(dirpath, filename)
            yield filepath, filename

        # Not looking in subdirectories
        break


def resize_and_save(output_directory: str,
                    image_path: str,
                    filename: str,
                    image_index: int,
                    resolution: int):
    print(f"{image_index}: Loading image {image_path}")
    image = Image.open(image_path)

    if image.mode == "L":
        image = image.convert("RGB")

    resized_image = ImageOps.fit(image, (resolution, resolution), Image.BICUBIC)
    
    output_path = path.join(output_directory, filename)
    print(f"{image_index}: Saving to {output_path}")
    resized_image.save(output_path)


@click.command()
@click.argument("input_dir")
@click.argument("output_dir")
@click.option("-r", "--resolution", default=1024, help="Output resolution of (square) images.")
@click.option("--dry-run", is_flag=True)
def resize_square(input_dir, output_dir, resolution, dry_run):
    """Resizes all images in a direcory to fit square dimentions e.g. 1024x1024.
    """
    
    total_images = 0

    for i, (image_path, filename) in enumerate(paths_and_names(input_dir), 1):
        total_images += 1

        if not dry_run:
            resize_and_save(output_dir, image_path, filename, i, resolution)



if __name__ == "__main__":
    resize_square()

