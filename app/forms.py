from django.forms import ModelForm
from app.models import UserCatalog, UserImage


class UploadImgForm(ModelForm):
    class Meta:
        model = UserImage
        fields = ["name", "image", "description"]


class NewCatalogForm(ModelForm):
    class Meta:
        model = UserCatalog
        fields = ["catalog_name"]
