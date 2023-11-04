from django.db import models
from django.contrib.auth.models import User


class UserCatalog(models.Model):
    catalog_name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default='1')

    def __str__(self):
        return self.catalog_name

    @staticmethod
    def get_images_from_catalog(user, catalog_name):
        return list(UserCatalog.objects.get(
            user=user, catalog_name=catalog_name
        ).userimage_set.all())

    @staticmethod
    def get_catalog_names(user):
        return list(UserCatalog.objects.filter(user=user).values_list(
            "catalog_name", flat=True))

    @staticmethod
    def delete_catalog(user, catalog_name):
        UserCatalog.objects.get(user=user, catalog_name=catalog_name).delete()


class UserImage(models.Model):
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to="app/images")
    user = models.ForeignKey(User, on_delete=models.CASCADE, default='1')
    catalog = models.ForeignKey(UserCatalog, on_delete=models.CASCADE,
                                default='1')
    description = models.TextField(blank=True, max_length='1000')

    def __str__(self):
        return self.name

    @staticmethod
    def get_all_image_names(user):
        return list(UserImage.objects.filter(user=user).values_list("name", flat=True))
