from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from app.models import UserImage, UserCatalog
from app.forms import UploadImgForm, NewCatalogForm
from django.contrib import messages
from app.utils import create_img_list_from_catalog, get_metadata_from_img

HOME_NAME = "home"
HOME_HTML = "home.html"
UPLOAD_IMG_NAME = "upload_img"
UPLOAD_IMG_HTML = "upload_img.html"
LOGGED_IN_NAME = "logged_in"
LOGGED_IN_HTML = "logged_in.html"
SIGN_UP_USER_NAME = "sign_up_user"
SING_UP_USER_HTML = "sign_up_user.html"
SIGN_IN_USER_NAME = "sign_in_user"
SING_IN_USER_HTML = "sign_in_user.html"

METADATA_SORT_TAG_NAME = "Metadata-sort"

METADATA_TAGS_DICT = {
    "Name": "Name",
    "DateTimeOriginal": "date_time_original",
    "Model": "model",
    "ExposureTime": "exposure_time",
    "FNumber": "f_number",
    "ISOSpeedRatings": "iso_speed_ratings",
    "LensModel": "lens_model",
}


def home(request):
    return render(request, HOME_HTML)


def check_invalid_img_upload_form(request, form):
    info = "Unknown error"
    if not form.cleaned_data.get("name"):
        info = "Name field can not be empty."
    if not form.cleaned_data.get("image"):
        info = "Image field can not be empty."
    if not request.POST.get("catalog"):
        info = "Choose catalog"
    messages.info(request, info)


def save_new_img(request, form, catalog_name):
    new_img = form.save(commit=False)
    new_img.user = request.user
    new_img.catalog = UserCatalog.objects.get(catalog_name=catalog_name, user=request.user)
    new_img.save()
    messages.success(request, "Your picture has been uploaded successfully!")


def check_if_catalog_form_is_valid(request, catalogs, catalog_form):
    catalog_name = request.POST.get("catalog_name")

    if not catalog_name:
        messages.info(request, "Catalog name field cannot be empty!")
        return False
    if catalog_name in catalogs:
        messages.info(request, "Catalog name must be unique!")
        return False
    if not catalog_form.is_valid():
        messages.info(request, catalog_form.errors)
        return False

    return True


def save_new_catalog(request, catalog_form):
    new_catalog = catalog_form.save(commit=False)
    new_catalog.user = request.user
    new_catalog.save()
    messages.info(request, "Catalog added")


def upload_img(request):
    catalogs = UserCatalog.get_catalog_names(request.user)

    if request.method == "GET":
        return render(
            request, UPLOAD_IMG_HTML, {"form": UploadImgForm(), "catalogs": catalogs}
        )
    if request.method == "POST":
        upload_img_form = UploadImgForm(request.POST, request.FILES)
        catalog_form = NewCatalogForm(request.POST)

        if request.POST.get("Upload"):
            if not upload_img_form.is_valid():
                check_invalid_img_upload_form(request, upload_img_form)
                return redirect(UPLOAD_IMG_NAME)
            catalog_name = request.POST.get("catalog")
            save_new_img(request, upload_img_form, catalog_name)

            return render(
                request,
                UPLOAD_IMG_HTML,
                {
                    "form": UploadImgForm(),
                    "catalogs": catalogs,
                    "catalog_name": catalog_name,
                },
            )

        if request.POST.get("AddCatalog"):
            if check_if_catalog_form_is_valid(request, catalogs, catalog_form):
                save_new_catalog(request, catalog_form)

        return redirect(UPLOAD_IMG_NAME)


def logged_in(request):
    user = request.user
    catalogs = UserCatalog.get_catalog_names(user)
    images = create_img_list_from_catalog(request)

    if request.method == "GET":
        return render(request, LOGGED_IN_HTML,
                      {"images": images, "catalogs": catalogs})

    if request.method == "POST":
        catalog_name = request.POST.get("Catalogs")
        images = create_img_list_from_catalog(request, catalog_name)

        if "Delete" in request.POST.values():
            delete_image(request)
            images = create_img_list_from_catalog(request, catalog_name)

        if request.POST.get("DeleteCatalog"):
            if catalog_name == "All":
                messages.info(request, "Catalog " "All" " can not be deleted")
            else:
                UserCatalog.delete_catalog(user=user, catalog_name=catalog_name)
                messages.info(request, "Catalog " "" + catalog_name + " " "have been deleted")
                images = create_img_list_from_catalog(request, "All")
                catalog_name = "All"

        if sort_parameter_tag := request.POST.get(METADATA_SORT_TAG_NAME):
            images = create_img_list_from_catalog(request, catalog_name)
            images = sort_images(images, sort_parameter_tag)

    return render(
        request,
        LOGGED_IN_HTML,
        {"images": images, "catalogs": catalogs, "selected": catalog_name},
    )


def sort_images(images, sort_parameter_tag):
    sort_parameter = METADATA_TAGS_DICT[sort_parameter_tag]
    if sort_parameter == "Name":
        images = sorted(images, key=lambda x: x[0].name)
    else:
        images = sorted(images, key=lambda x: getattr(x[1], sort_parameter))
    return images


def delete_image(request):
    for image_id, value in request.POST.items():
        if value == "Delete":
            UserImage.objects.get(id=image_id).delete()
            break


def logout_user(request):
    logout(request)
    return redirect(HOME_NAME)


def sign_up_user(request):
    if request.method == "GET":
        return render(request, SING_UP_USER_HTML, {"form": UserCreationForm()})
    if request.POST:
        if request.POST["password1"] == request.POST["password2"]:
            try:
                user = User.objects.create_user(
                    request.POST["username"],
                    email=request.POST["email"],
                    password=request.POST["password1"],
                )
                login(request, user)
                return redirect("logged_in")
            except IntegrityError:
                return render(
                    request,
                    SING_UP_USER_HTML,
                    {
                        "form": UserCreationForm(),
                        "error": "That username has already taken",
                    },
                )
        if not request.POST["password1"] == request.POST["password2"]:
            return render(
                request,
                SING_UP_USER_HTML,
                {"form": UserCreationForm(), "error": "Passwords did not match"},
            )


def sign_in_user(request):
    if request.method == "GET":
        return render(request, SING_IN_USER_HTML, {"form": AuthenticationForm()})
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST["username"],
            password=request.POST["password"],
        )
        if user:
            login(request, user)
            return redirect(LOGGED_IN_NAME)

        return render(
            request,
            SING_IN_USER_HTML,
            {
                "form": AuthenticationForm(),
                "error": "Username or password did not match",
            },
        )
    return redirect(HOME_NAME)


def img_metadata(request, image_id):
    img = UserImage.objects.get(id=image_id)
    exif_data = get_metadata_from_img(img.image)
    return render(request, "img_metadata.html", {"image": img, "exif_data": exif_data})
