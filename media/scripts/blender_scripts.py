import bpy
import os
import math
import sys

# Constants

# === RENDER SETTINGS ===
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'GPU'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.cycles.samples = 100
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'JPEG'
# scene.render.film_transparent = True


model_file = str(sys.argv[3])
model_file_basename_without_ext = os.path.splitext(os.path.basename(model_file))[0]

output_dir = str(sys.argv[6])
os.makedirs(output_dir, exist_ok=True)

N = int(sys.argv[7])
rotation_step = 360 / N
body = bpy.data.objects.get("body")

target_names = []
target_paths = []

for i in range(8, len(sys.argv), 2):
    target_names.append(sys.argv[i])
    target_paths.append(sys.argv[i+1])


def assign_material(name, texture_path):
    # Try to get the object
    obj = bpy.data.objects.get(name)
    mat = bpy.data.materials.get(name)

    # If we got an object
    if obj:
        print(f"🎯 Assigning material to object: {name}")
        # Create or reuse material
        if obj.active_material:
            mat = obj.active_material
            print(f"ℹ️ Reusing existing material: {mat.name}")
        else:
            mat = bpy.data.materials.new(name=f"{obj.name}_Mat")
            obj.data.materials.append(mat)

    # If we got a material
    elif mat:
        print(f"🎯 Updating existing material: {name}")

    # Neither found
    else:
        print(f"⚠️ '{name}' is neither an object nor a material!")
        return

    # Ensure material uses nodes
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Get or create Principled BSDF
    bsdf = nodes.get("Principled BSDF")
    if not bsdf:
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")

    # Add texture node
    tex_image = nodes.new("ShaderNodeTexImage")
    tex_image.image = bpy.data.images.load(texture_path)

    # Link texture to Base Color
    links.new(bsdf.inputs["Base Color"], tex_image.outputs["Color"])




def render(textures_files):
    output_file_parts = [model_file_basename_without_ext]
    for obj_name, texture_path in zip(target_names, textures_files):
        assign_material(obj_name, texture_path)
        output_file_parts.append(os.path.splitext(os.path.basename(texture_path))[0])

    output = '_'.join(output_file_parts)

    for i in range(N):
        angle = math.radians(i * rotation_step)
        body.rotation_euler[2] = angle
        scene.render.filepath = os.path.join(output_dir, f"{output}_{i+1:02d}.jpg")
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
