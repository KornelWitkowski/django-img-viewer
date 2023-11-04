from app.models import UserImage, UserCatalog
from PIL import Image
from PIL.ExifTags import TAGS

METADATA_TAGS = [
    "DateTime",
    "Model",
    "ExposureTime",
    "FNumber",
    "ISOSpeedRatings",
    "LensModel",
]

NO_METADATA_COMMUNICATE = "The file does not contain any metadata."


class ImageMetadata:
    def __init__(
        self,
        date_time_original,
        model,
        exposure_time,
        f_number,
        iso_speed_ratings,
        lens_model,
        view,
    ):
        self.date_time_original = date_time_original
        self.model = model
        self.exposure_time = exposure_time
        self.f_number = f_number
        self.iso_speed_ratings = iso_speed_ratings
        self.lens_model = lens_model
        self.view = view

    @classmethod
    def from_image_path(cls, image_path):
        image_file = Image.open(image_path)
        exif_data = image_file._getexif()

        metadata = {tag: None for tag in METADATA_TAGS}

        if exif_data is not None:
            for tag_id in exif_data:
                tag = TAGS.get(tag_id, tag_id)
                data = exif_data.get(tag_id)
                if tag in METADATA_TAGS:
                    metadata[tag] = data

        return cls(*metadata.values(), True)


def get_image_names(user, catalog_name):
    if catalog_name == "All":
        return UserImage.get_all_image_names(user)
    images = UserCatalog.get_images_from_catalog(user, catalog_name)
    return [image.name for image in images]


def create_img_list_from_catalog(request, catalog_name="All"):
    images = []
    user = request.user
    images_names = get_image_names(user, catalog_name)
    for img_name in images_names:
        image = UserImage.objects.get(name=img_name, user=user)
        metadata = ImageMetadata.from_image_path(image.image)
        images.append([image, metadata])
        if request.method == "POST" and not request.POST.get("Select"):
            images_to_show = list(request.POST.getlist("show_checkbox"))
            for image, metadata in images:
                metadata.view = True if image.name in images_to_show else False

    return images


def get_metadata_from_img(image_path):
    image = Image.open(image_path)
    exif_data = image._getexif()

    metadata = []

    if exif_data is None:
        return NO_METADATA_COMMUNICATE

    for tag_id in exif_data:
        tag = TAGS.get(tag_id, tag_id)
        data = exif_data.get(tag_id)
        metadata.append(f"{tag} : {data}")

    if not metadata:
        metadata = NO_METADATA_COMMUNICATE

    return metadata
