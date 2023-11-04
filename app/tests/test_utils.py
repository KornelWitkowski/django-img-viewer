from app.utils import (get_metadata_from_img, ImageMetadata,
                       get_image_names, create_img_list_from_catalog)
from django.test import TestCase
from unittest.mock import MagicMock
from app.models import UserCatalog, UserImage
from django.contrib.auth.models import User
import os


IMAGE_WITHOUT_METADATA_PATH = os.path.join(os.getcwd(), "app",
                                           "tests", "images", "img_without_metadata.png")
IMAGE_WITH_METADATA_PATH = os.path.join(os.getcwd(), "app", "tests",
                                        "images", "img_with_metadata.jpg")


class TestGetMetadataFromImg(TestCase):
    def test_get_metadata_from_img_with_no_metadata(self):
        actual = get_metadata_from_img(IMAGE_WITHOUT_METADATA_PATH)
        expected = "The file does not contain any metadata."
        self.assertEqual(actual, expected)

    def test_get_metadata_from_img_with_metadata(self):
        actual = get_metadata_from_img(IMAGE_WITH_METADATA_PATH)
        self.assertEqual(actual[0], 'ResolutionUnit : 2')
        self.assertEqual(actual[1], 'ExifOffset : 216')
        self.assertEqual(actual[2], 'Make : Canon')
        self.assertEqual(actual[3], 'Model : Canon EOS 77D')
        self.assertEqual(actual[-1], 'LensSerialNumber : 0000280404')


class TestImageMetadata(TestCase):
    def test_from_image_path_without_metadata(self):
        image_metadata = ImageMetadata.from_image_path(IMAGE_WITHOUT_METADATA_PATH)
        self.assertIsNone(image_metadata.date_time_original)
        self.assertIsNone(image_metadata.model)
        self.assertIsNone(image_metadata.exposure_time)
        self.assertIsNone(image_metadata.f_number)
        self.assertIsNone(image_metadata.iso_speed_ratings)
        self.assertIsNone(image_metadata.lens_model)

    def test_from_image_path_with_metadata(self):
        image_metadata = ImageMetadata.from_image_path(IMAGE_WITH_METADATA_PATH)
        self.assertEqual(image_metadata.date_time_original, '2020:08:12 10:32:48')
        self.assertEqual(image_metadata.model, 'Canon EOS 77D')
        self.assertEqual(image_metadata.exposure_time, 0.0025)
        self.assertEqual(image_metadata.f_number, 3.5)
        self.assertEqual(image_metadata.iso_speed_ratings, 100)
        self.assertEqual(image_metadata.lens_model, 'EF50mm f/1.8 STM')


class TestGetImageNames(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('user')
        UserCatalog.objects.create(user=self.user,
                                   catalog_name="name0")
        catalog1 = UserCatalog.objects.create(user=self.user,
                                              catalog_name="name1")
        catalog2 = UserCatalog.objects.create(user=self.user,
                                              catalog_name="name2")

        UserImage.objects.create(name="name11",
                                 user=self.user,
                                 catalog=catalog1,
                                 image=IMAGE_WITHOUT_METADATA_PATH,
                                 description="")
        UserImage.objects.create(name="name12",
                                 user=self.user,
                                 catalog=catalog1,
                                 image=IMAGE_WITH_METADATA_PATH,
                                 description="")
        UserImage.objects.create(name="name21",
                                 user=self.user,
                                 catalog=catalog2,
                                 image=IMAGE_WITH_METADATA_PATH,
                                 description="")

    def test_get_image_names_empty_catalog(self):
        actual = get_image_names(self.user, "name0")
        expected = []
        self.assertEqual(actual, expected)

    def test_get_image_names_not_empty_catalog(self):
        actual = get_image_names(self.user, "name1")
        expected = ["name11", "name12"]
        self.assertEqual(actual, expected)

    def test_get_image_names_all_catalogs(self):
        actual = get_image_names(self.user, "All")
        expected = ["name11", "name12", "name21"]
        self.assertEqual(actual, expected)


class TestCreateImgListFromCatalog(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('user')
        _ = UserCatalog.objects.create(user=self.user, catalog_name="name0")
        catalog1 = UserCatalog.objects.create(user=self.user,
                                              catalog_name="name1")
        catalog2 = UserCatalog.objects.create(user=self.user,
                                              catalog_name="name2")

        UserImage.objects.create(name="name11",
                                 user=self.user,
                                 catalog=catalog1,
                                 image=IMAGE_WITHOUT_METADATA_PATH,
                                 description="")
        UserImage.objects.create(name="name12",
                                 user=self.user,
                                 catalog=catalog1,
                                 image=IMAGE_WITH_METADATA_PATH,
                                 description="")
        UserImage.objects.create(name="name21",
                                 user=self.user,
                                 catalog=catalog2,
                                 image=IMAGE_WITHOUT_METADATA_PATH,
                                 description="")

    def test_create_img_list_from_catalog_empty(self):
        attrs = {'user': self.user,
                 'method': "POST",
                 'POST.get.return_value': False,
                 'POST.getlist.return_value': []}
        request = MagicMock(**attrs)

        expected = []
        actual = create_img_list_from_catalog(request, catalog_name="name0")
        self.assertEqual(actual, expected)

    def test_create_img_list_from_catalog_one_catalog(self):
        attrs = {'user': self.user,
                 'method': "POST",
                 'POST.get.return_value': False,
                 'POST.getlist.return_value': ["name11", "name12"]}
        request = MagicMock(**attrs)

        actual = create_img_list_from_catalog(request, catalog_name="name1")

        self.assertEqual(len(actual), 2)
        self.assertIsInstance(actual[0][0], UserImage)
        self.assertIsInstance(actual[0][1], ImageMetadata)
        self.assertEqual(actual[0][0].name, "name11")
        self.assertEqual(actual[0][1].model, None)
        self.assertEqual(actual[0][1].view, True)
        self.assertEqual(actual[1][0].name, "name12")
        self.assertEqual(actual[1][1].model, 'Canon EOS 77D')
        self.assertEqual(actual[1][1].view, True)

    def test_create_img_list_from_catalog_all_catalogs(self):
        attrs = {'user': self.user,
                 'method': "POST",
                 'POST.get.return_value': False,
                 'POST.getlist.return_value': ["name11", "name12"]
                 }
        request = MagicMock(**attrs)

        actual = create_img_list_from_catalog(request, catalog_name="All")

        self.assertEqual(actual[0][0].name, "name11")
        self.assertEqual(actual[0][1].model, None)
        self.assertEqual(actual[0][1].view, True)
        self.assertEqual(actual[1][0].name, "name12")
        self.assertEqual(actual[1][1].model, 'Canon EOS 77D')
        self.assertEqual(actual[1][1].view, True)
        self.assertEqual(actual[2][0].name, "name21")
        self.assertEqual(actual[2][1].model, None)
        self.assertEqual(actual[2][1].view, False)
