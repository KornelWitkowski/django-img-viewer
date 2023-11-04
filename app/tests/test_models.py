from django.test import TestCase
from app.models import UserCatalog, UserImage
from django.contrib.auth.models import User
import os

IMAGE1_PATH = os.path.join(os.getcwd(), "app", "tests",
                           "images", "img_without_metadata.png")
IMAGE2_PATH = os.path.join(os.getcwd(), "app", "tests",
                           "images", "img_with_metadata.jpg")


class TestUserCatalog(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user('user1')
        self.user2 = User.objects.create_user('user2')
        self.catalog11 = UserCatalog.objects.create(user=self.user1, catalog_name="name11")
        UserCatalog.objects.create(user=self.user1, catalog_name="name12")

        UserCatalog.objects.create(user=self.user2, catalog_name="name11")
        UserCatalog.objects.create(user=self.user2, catalog_name="name21")

    def test_user_catalog(self):
        actual1 = UserCatalog.get_catalog_names(user=self.user1)
        excepted1 = ["name11", "name12"]
        self.assertEqual(actual1, excepted1)

        actual2 = UserCatalog.get_catalog_names(user=self.user2)
        excepted2 = ["name11", "name21"]
        self.assertEqual(actual2, excepted2)

    def test_user_catalog_delete(self):
        UserCatalog.delete_catalog(user=self.user1, catalog_name="name11")

        actual1 = UserCatalog.get_catalog_names(user=self.user1)
        excepted1 = ["name12"]
        self.assertEqual(actual1, excepted1)

        actual2 = UserCatalog.get_catalog_names(user=self.user2)
        excepted2 = ["name11", "name21"]
        self.assertEqual(actual2, excepted2)

    def test_get_images_from_catalog(self):
        image1 = UserImage.objects.create(name="name11",
                                          user=self.user1,
                                          catalog=self.catalog11,
                                          image=IMAGE1_PATH,
                                          description="")
        image2 = UserImage.objects.create(name="name12",
                                          user=self.user1,
                                          catalog=self.catalog11,
                                          image=IMAGE2_PATH,
                                          description="")
        images_name = UserCatalog.get_images_from_catalog(user=self.user1,
                                                          catalog_name="name11")
        self.assertEqual(images_name, [image1, image2])


class TestUserImage(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user('user1')
        self.user2 = User.objects.create_user('user2')
        self.catalog1 = UserCatalog.objects.create(user=self.user1, catalog_name="name1")
        self.catalog2 = UserCatalog.objects.create(user=self.user2, catalog_name="name2")

        UserImage.objects.create(name="name11",
                                 user=self.user1,
                                 catalog=self.catalog1,
                                 image=IMAGE1_PATH,
                                 description="")
        UserImage.objects.create(name="name12",
                                 user=self.user1,
                                 catalog=self.catalog1,
                                 image=IMAGE2_PATH,
                                 description="")
        UserImage.objects.create(name="name21",
                                 user=self.user2,
                                 catalog=self.catalog2,
                                 image=IMAGE1_PATH,
                                 description="")

    def test_get_all_image_names(self):
        actual = UserImage.get_all_image_names(self.user1)
        expected = ["name11", "name12"]
        self.assertEqual(actual, expected)

        actual = UserImage.get_all_image_names(self.user2)
        expected = ["name21"]
        self.assertEqual(actual, expected)
