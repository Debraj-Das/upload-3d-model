from django import forms
from .models import Project, TexturePart, TextureFile

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['project_name', 'model_file', 'low_quality_model_file']
        widgets = {
            'project_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter project name'
            }),
            'model_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.blend'
            }),
            'low_quality_model_file': forms.FileInput(attrs={
                'class': "form-control",
                'accept': '.glb',
            })
        }

    def clean_model_file(self):
        file = self.cleaned_data.get('model_file')
        if file and not file.name.endswith('.blend'):
            raise forms.ValidationError("Only .blend files are allowed.")
        return file
    
    def clean_low_quality_model_file(self):
        file = self.cleaned_data.get('low_quality_model_file')
        if file and not file.name.endswith('.glb'):
            raise forms.ValidationError("Only .glb files are allowed.")
        return file        

class TexturePartForm(forms.ModelForm):
    class Meta:
        model = TexturePart
        fields = ['object_name']
        widgets = {
            'object_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter object name'
            })
        }