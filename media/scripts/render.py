import bpy
import sys
import os
import math


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



# Remove previous empty
if "SofaEmpty" in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects["SofaEmpty"], do_unlink=True)

# Add empty for rotation
bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
empty = bpy.context.active_object
empty.name = "SofaEmpty"


model = str(sys.argv[3])
output_dir = str(sys.argv[6])
os.makedirs(output_dir, exist_ok=True)

# textures = {}
for i in range(7, len(sys.argv), 2):
    part_name = sys.argv[i]
    texture_path = sys.argv[i + 1]
    # textures[part_name] = texture_path
    obj = bpy.data.objects.get(part_name)
    if obj:
        assign_material(part_name, texture_path)
        obj.parent = empty

X_resolution = 2048
Y_resolution = 2048
SAMPLES = 32
N = 36

scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.device = "GPU"
scene.cycles.samples = SAMPLES
scene.render.resolution_x = X_resolution
scene.render.resolution_y = Y_resolution
scene.render.film_transparent = False  # KEY: disable transparency!
scene.render.image_settings.file_format = "PNG"

# ─── SET WHITE WORLD BACKGROUND ───
world = scene.world
world.use_nodes = True
nodes = world.node_tree.nodes
nodes.clear()

bg = nodes.new(type="ShaderNodeBackground")
bg.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)  # white
bg.inputs[1].default_value = 1.0

out = nodes.new(type="ShaderNodeOutputWorld")
world.node_tree.links.new(bg.outputs[0], out.inputs[0])

for i in range(N):
    angle = math.radians(i * (360 / N))
    empty.rotation_euler[2] = angle
    scene.render.filepath = os.path.join(output_dir, f"{i+1}.png")
    bpy.ops.render.render(write_still=True)
