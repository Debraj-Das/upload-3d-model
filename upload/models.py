from django.db import models
from django.contrib.auth.models import User
import os
import uuid

def upload_model_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    return f'uploads/models/{instance.project_name}/{unique_filename}'

def upload_LQ_model_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    return f'uploads/LQ_models/{instance.project_name}/{unique_filename}'

def upload_texture_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    return f'uploads/textures/{instance.texture_part.project.project_name}/{instance.texture_part.object_name}/{unique_filename}'


class Project(models.Model):
    project_name = models.CharField(max_length=300, unique=True)
    view_name = models.CharField(max_length=200)
    model_file = models.FileField(upload_to=upload_model_path, null=True, blank=True)
    low_quality_model_file = models.FileField(upload_to=upload_LQ_model_path, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.project_name

    class Meta:
        ordering = ['-created_at']

class TexturePart(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='texture_parts')
    object_name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project.project_name} - {self.object_name}"

    class Meta:
        ordering = ['created_at']

class TextureFile(models.Model):
    texture_part = models.ForeignKey(TexturePart, on_delete=models.CASCADE, related_name='texture_files')
    file = models.ImageField(upload_to=upload_texture_path)
    original_filename = models.CharField(max_length=255)
    file_size = models.IntegerField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.texture_part.object_name} - {self.original_filename}"

    def save(self, *args, **kwargs):
        if self.file:
            self.original_filename = self.file.name
            self.file_size = self.file.size
        super().save(*args, **kwargs)
