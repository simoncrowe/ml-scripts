import click
import os
import dlib
import shutil

COMMON_IMAGE_FILE_EXTENSIONS = (
    "jpg",
    "jpeg",
    "png",
    "gif",
    "tif",
    "tiff",
    "tga",
    "bmp",
)
CNN_FACE_DETECTOR_FILENAME = "mmod_human_face_detector.dat"


def wrong_num_faces_generator(image_paths, min_faces, max_faces):
    cnn_face_detector = dlib.cnn_face_detection_model_v1(CNN_FACE_DETECTOR_FILENAME)

    for i, image_path in enumerate(image_paths, 1):
        print("Running face detection on image {image_num} of {image_count}".format(image_num=i, image_count=len(image_paths)))
        img = dlib.load_rgb_image(image_path)
        # Run face detection
        faces_detected = len(cnn_face_detector(img, 1))
        
        if min_faces <= faces_detected <= max_faces:
            print("{face_count} faces found. GOOD.".format(face_count=faces_detected))
        else:   
            print("{face_count} faces found. BAD.".format(face_count=faces_detected))
            yield image_path


@click.command()
@click.argument("images_dir")
@click.option(
    "-d", 
    "--wrong-num-faces-dir", 
    required=True,
    help="Directory to move images with too many or too few faces.",
)
@click.option(
    "--min-num-faces",
    default=1,
    help="The minimum number of faces allowed in an image for it to be kept.",
)
@click.option(
    "--max-num-faces",
    default=16,
    help="The maximum number of faces allowed in an image for it to be kept.",
)
@click.option("--dry-run", is_flag=True)
def move_images(images_dir, wrong_num_faces_dir, min_num_faces, max_num_faces, dry_run):
    image_paths = tuple(
        os.path.join(root, f) for root, _, files in os.walk(images_dir) for f in files 
        #if os.path.splitext(f)[1].lower() in COMMON_IMAGE_FILE_EXTENSIONS
    )
    print("{image_count} images found in {image_path}".format(image_count=len(image_paths), image_path=images_dir))

    images_to_move = tuple(wrong_num_faces_generator(image_paths, min_num_faces, max_num_faces))
    if images_to_move and not os.path.exists(wrong_num_faces_dir):
        os.makedirs(wrong_num_faces_dir)

    for image_path in images_to_move:
        image_name = image_path.split("/")[-1]
        destination_path = os.path.join(wrong_num_faces_dir, image_name)
        if not dry_run:
            print("Moving {source} to {destination}".format(source=image_path, destination=destination_path))
            shutil.move(image_path, destination_path)
   
    if dry_run:
        print("{image_count} images processed; {moved_count} would have been moved.".format(image_count = len(image_paths), moved_count=len(images_to_move)))
    else:
        print("{image_count} images processed; {moved_count} moved.".format(image_count = len(image_paths), moved_count=len(images_to_move)))


if __name__ == "__main__":
    move_images()

