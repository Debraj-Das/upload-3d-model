import os
from admin import settings
import subprocess

def render_project_images(project):
    model_file = os.path.join(settings.MEDIA_ROOT, str(project.model_file))
    textures_dir = os.path.join(settings.MEDIA_ROOT, 'uploads/textures', str(project.project_name))
    scripts_file = os.path.join(settings.MEDIA_ROOT, "scripts/blender_scripts.py")

    output_file = os.path.join(settings.MEDIA_ROOT, "output", str(project))

    command = [
        "blender", "-b", "-noaudio", model_file, "-P", scripts_file, output_file
    ]
    for part in project.texture_parts.all():
        part_name = part.object_name
        part_path = os.path.join(
            textures_dir,
            str(part_name)
        )

        if os.path.isdir(part_path):
            command.append(part_name)
            command.append(part_path)

    logs = os.path.join(settings.MEDIA_ROOT, "logs")
    if not logs.exists():
        logs.mkdir(parents=True)

    errs = os.path.join(settings.MEDIA_ROOT, "errs")
    if not errs.exists():
        errs.mkdir(parent=True)

    logfile = open(os.path.join(settings.MEDIA_ROOT, "logs", str(project) + '.log',), 'a')
    errfile = open(os.path.join(settings.MEDIA_ROOT, "errs", str(project) + '.err'), 'a')
    subprocess.Popen(command, stdout=logfile, stderr=errfile)

    return True
