import json
import os
import random
import shutil
import uuid

from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import DetailView, ListView

from admin import settings

from .forms import ProjectForm, TexturePartForm
from .models import Project, TextureFile, TexturePart
from .render_project_images import render_project_images

from django.contrib.auth.decorators import login_required
from io import BytesIO
import zipfile
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
import urllib.request


def upload_model(request):
    if request.method == 'POST':
        view_name = request.POST.get('project_name')
        model_file = request.FILES.get('model_file')
        low_quality_model_file = request.FILES.get('low_quality_model_file')
        object_names = request.POST.getlist('object_names[]')
        
        
        # add the 16 digit timestamp to the project name
        ext = os.path.splitext(view_name)[1]
        project_name = f"{uuid.uuid4().hex}{ext}"

        if not project_name or not model_file:
            messages.error(request, 'Project name and model file are required.')
            return render(request, 'upload_model.html')

        if Project.objects.filter(project_name=project_name).exists():
            return render(request, 'upload_model.html', {'project_name': 'previous present project name'})
        
        # Create the project
        project = Project.objects.create(
            project_name=project_name,
            view_name = view_name,
            model_file=model_file,
            low_quality_model_file=low_quality_model_file,
            user=request.user if request.user.is_authenticated else None
        )
        
        # Process texture parts
        for i, object_name in enumerate(object_names):
            if object_name.strip():  # Only process non-empty object names
                # Create texture part
                texture_part = TexturePart.objects.create(
                    project=project,
                    object_name=object_name.strip()
                )
                
                # Process texture files for this part
                texture_files_key = f'textures_{i+1}[]'
                texture_files = request.FILES.getlist(texture_files_key)
                
                for texture_file in texture_files:
                    TextureFile.objects.create(
                        texture_part=texture_part,
                        file=texture_file,
                        original_filename=texture_file.name
                    )
        
        messages.success(request, f'Project "{view_name}" uploaded successfully!')

        return redirect('project_detail', pk=project.pk)
    
    return render(request, 'upload_model.html')

class ProjectListView(ListView):
    model = Project
    template_name = 'project_list.html'
    context_object_name = 'projects'
    paginate_by = 10

    def get_queryset(self):
        queryset = Project.objects.all()
        if self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)
        return queryset

class ProjectDetailView(DetailView):
    model = Project
    template_name = 'project_detail.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['texture_parts'] = self.object.texture_parts.all()
        output_dir = os.path.join(settings.MEDIA_ROOT, 'output', str(self.object.project_name))
        output_files = []
        if os.path.exists(output_dir):
            for file in sorted(os.listdir(output_dir)):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    output_files.append(os.path.join(settings.MEDIA_URL, 'output', str(self.object.project_name), file))
        context['output_files'] = output_files
        return context

def delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if not project.user or request.user.is_authenticated and project.user == request.user:
        model_dir = os.path.join(settings.MEDIA_ROOT,'uploads/models', str(project.project_name))
        try:
            if os.path.exists(model_dir):
                shutil.rmtree(model_dir)

            low_quality_model_file_dir = os.path.join(settings.MEDIA_ROOT, 'uploads/LQ_models', str(project.project_name))
            if os.path.exists(low_quality_model_file_dir):
                shutil.rmtree(low_quality_model_file_dir)

            textures = os.path.join(settings.MEDIA_ROOT, 'uploads/textures', str(project.project_name))
            if os.path.exists(textures):
                shutil.rmtree(textures)

            output_dir = os.path.join(settings.MEDIA_ROOT, 'output', str(project.project_name) )
            if os.path.exists(output_dir):
                shutil.rmtree(output_dir)

            err_file = os.path.join(settings.MEDIA_ROOT,'errs', str(project.project_name) + '.err')
            if os.path.isfile(err_file):
                os.remove(err_file)

            log_file = os.path.join(settings.MEDIA_ROOT, 'logs', str(project.project_name) + 'log')
            if os.path.isfile(log_file):
                os.remove(log_file)

            project.delete()
            messages.success(request, 'Project deleted successfully!')
        except OSError as e:
            messages.error(request, f'Error deleting project: {e}')
            print(f'Error deleting project {project.view_name}: {e}')
            return HttpResponse(status=500)
    else:
        messages.error(request, 'You do not have permission to delete this project.')
    return redirect('project_list')


@csrf_exempt
def generate_images(request):
    if request.method == 'POST':
        project_id = request.POST.get('project_id')
        project = get_object_or_404(Project, id=project_id)
        if request.user.is_authenticated and project.user == request.user:
            render_project_images(project, 72)
            messages.success(request, f"Started image generation for {project.view_name}")
            return redirect('project_detail', pk=project.pk)

    return redirect('project_list')


@csrf_exempt
def generate_test_images(request):
    if request.method == 'POST':
        project_id = request.POST.get('project_id')
        project = get_object_or_404(Project, id=project_id)
        if request.user.is_authenticated and project.user == request.user:
            render_project_images(project,1)
            messages.success(request, f"Started image generation for {project.view_name}")
            return redirect('project_detail', pk=project.pk)

    return redirect('project_list')


def get_model_path(request, product_id):
    project = get_object_or_404(Project, view_name=product_id)
    model_url = project.low_quality_model_file.url if project.low_quality_model_file else None
    return JsonResponse({'model_file': model_url})

def get_textures(request, product_id):
    project = get_object_or_404(Project, view_name=product_id)
    texture_parts = []
    for part in project.texture_parts.all():
        files = [tf.file.url for tf in part.texture_files.all()]
        texture_parts.append({
            'object_name': part.object_name,
            'files': files
        })
    return JsonResponse({'texture_parts': texture_parts})




def get_rendered_images(request, product_id):
    try:
        project = get_object_or_404(Project, view_name=product_id)

        output_dir = os.path.join(settings.MEDIA_ROOT, 'output', str(project.project_name))
        if not os.path.exists(output_dir):
            return JsonResponse({'error': 'No images found for this project.'}, status=404)
        
        texture_ids = []
        for part in project.texture_parts.all():
            texture_ids.append(request.GET.get(str(part.object_name), ""))

        images = []
        for file in sorted(os.listdir(output_dir)):
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')) and product_id in file:
                check = True
                for texture_id in texture_ids:
                    if texture_id == "" or texture_id not in file:
                        check = False
                        break
                if check:
                    images.append(os.path.join(settings.MEDIA_URL, 'output', str(project.project_name), file))

        return JsonResponse({'images': images})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)



@login_required
def download_output_zip(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Check if user has permission to download
    if project.user != request.user:
        raise Http404("You don't have permission to download this project's files")
    
    # Get the output directory
    output_dir = os.path.join(settings.MEDIA_ROOT, 'output', str(project.project_name))

    print(output_dir)
    
    if not os.path.exists(output_dir):
        return HttpResponse("No output images found for this project", status=404)
    
    # Create a BytesIO object to store the ZIP file in memory
    zip_buffer = BytesIO()
    
    try:
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Get all image files from the output directory
            image_files = []
            
            for file in sorted(os.listdir(output_dir)):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    # Check if the file contains the project view_name (similar to your get_rendered_images logic)
                    if project.project_name in file:
                        image_files.append(file)
            
            if not image_files:
                print("why this comming")
                return HttpResponse("No output images found for this project", status=404)
            
            # Add each image file to the ZIP
            for filename in image_files:
                file_path = os.path.join(output_dir, filename)
                try:
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                    
                    # Add file to ZIP with original filename
                    zip_file.writestr(filename, file_data)
                except Exception as e:
                    print(f"Error adding file {filename} to ZIP: {e}")
                    continue
        
        zip_buffer.seek(0)
        
        # Create HTTP response with ZIP file
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{project.view_name}_output_images.zip"'
        
        return response
        
    except Exception as e:
        print(f"Error creating ZIP file: {e}")
        return HttpResponse("Error creating ZIP file", status=500)
