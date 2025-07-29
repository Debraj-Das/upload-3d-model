import bpy
import os
import math
import sys

# Constants
N = 6
rotation_step = 360 / N
body = bpy.data.objects.get("body")

# === RENDER SETTINGS ===
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.render.resolution_x = 600
scene.render.resolution_y = 364
scene.render.image_settings.file_format = 'JPEG'


model_file = str(sys.argv[3])
model_file_basename_without_ext = os.path.splitext(os.path.basename(model_file))[0]

output_dir = str(sys.argv[6])
os.makedirs(output_dir, exist_ok=True)

target_names = []
target_paths = []

for i in range(7, len(sys.argv), 2):
    target_names.append(sys.argv[i])
    target_paths.append(sys.argv[i+1])


def assign_material(obj_name, texture_path):
    obj = bpy.data.objects.get(obj_name)
    if not obj:
        print(f"⚠️ Warning: '{obj_name}' not found!")
        return

    mat = bpy.data.materials.new(name=f"{obj_name}_Mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    tex_image = mat.node_tree.nodes.new("ShaderNodeTexImage")
    tex_image.image = bpy.data.images.load(texture_path)
    mat.node_tree.links.new(bsdf.inputs["Base Color"], tex_image.outputs["Color"])

    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)



def render(textures_files):
    output_file_parts = [model_file_basename_without_ext]
    for obj_name, texture_path in zip(target_names, textures_files):
        assign_material(obj_name, texture_path)
        output_file_parts.append(os.path.splitext(os.path.basename(texture_path))[0])

    output = '_'.join(output_file_parts)

    for i in range(N):
        angle = math.radians(i * rotation_step)
        body.rotation_euler[2] = angle
        scene.render.filepath = os.path.join(output_dir, f"{output}_{i+1}.jpg")
        bpy.ops.render.render(write_still=True)
        print(f"Rendered image {i+1}/{N}")




def recursive(index, textures_files):
    if(index == len(target_names)):
        render(textures_files)
        return
    
    current_dir = target_paths[index]
    if not os.path.isdir(current_dir):
        print(f"⚠️ Warning: {current_dir} is not a directory.")
        return

    for file in os.listdir(current_dir):
        file_path = os.path.join(current_dir, file)
        if os.path.isfile(file_path):
            textures_files.append(file_path)
            recursive(index+1, textures_files)
            textures_files.pop()

recursive(0, [])

print("✅ All renders complete.")
