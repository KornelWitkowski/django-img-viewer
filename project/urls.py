from django.contrib import admin
from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', views.home, name='home'),
    path('upload_img/', views.upload_img, name='upload_img'),
    path('logged_in/', views.logged_in, name='logged_in'),
    path('log_out/', views.logout_user, name='logout_user'),
    path('sign_up/', views.sign_up_user, name='sign_up_user'),
    path('sign_in/', views.sign_in_user, name='sign_in_user'),
    path('<int:image_id>', views.img_metadata, name='img_metadata')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
