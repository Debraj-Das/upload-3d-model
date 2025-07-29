from django.contrib import admin
from .models import Project, TexturePart, TextureFile

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['project_name', 'user', 'created_at', 'updated_at']
    list_filter = ['created_at', 'user']
    search_fields = ['project_name', 'user__username']
    readonly_fields = ['created_at', 'updated_at']

class TextureFileInline(admin.TabularInline):
    model = TextureFile
    extra = 0
    readonly_fields = ['original_filename', 'file_size', 'uploaded_at']

@admin.register(TexturePart)
class TexturePartAdmin(admin.ModelAdmin):
    list_display = ['object_name', 'project', 'created_at']
    list_filter = ['created_at', 'project']
    search_fields = ['object_name', 'project__project_name']
    inlines = [TextureFileInline]

@admin.register(TextureFile)
class TextureFileAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'texture_part', 'file_size', 'uploaded_at']
    list_filter = ['uploaded_at', 'texture_part__project']
    search_fields = ['original_filename', 'texture_part__object_name']
    readonly_fields = ['original_filename', 'file_size', 'uploaded_at']