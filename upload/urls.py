"""
URL configuration for admin project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from admin import settings

from . import views

urlpatterns = [
    path('', views.ProjectListView.as_view(), name='project_list'),
    path('upload/', views.upload_model, name='upload_model'),
    path('project/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('project/<int:pk>/delete/', views.delete_project, name='delete_project'),
    path('generate-images/', views.generate_images, name='generate_images'),
    path('generate-test-images/', views.generate_test_images, name='generate_test_images'),
    path('api/<str:product_id>/model', views.get_model_path, name='api_get_model'),
    path('api/<str:product_id>/textures', views.get_textures, name='api_get_textures'),
    path('api/<str:product_id>/images', views.get_rendered_images, name='api_get_images'),
   path('project/<int:project_id>/download-output-zip/', views.download_output_zip, name='download_output_zip'),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
