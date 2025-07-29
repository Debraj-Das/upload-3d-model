import bpy
import os
import math
import sys
import bmesh

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


def create_normal_map_from_base(base_image):
    """Generate normal map using Blender nodes"""
    # Create a new image for the normal map
    width, height = base_image.size
    normal_image = bpy.data.images.new(
        name=f"{base_image.name}_normal",
        width=width,
        height=height,
        alpha=False
    )
    
    # Create a temporary material to generate the normal map
    temp_mat = bpy.data.materials.new(name="temp_normal_gen")
    temp_mat.use_nodes = True
    nodes = temp_mat.node_tree.nodes
    links = temp_mat.node_tree.links
    
    # Clear default nodes
    nodes.clear()
    
    # Create nodes for normal map generation
    base_tex = nodes.new("ShaderNodeTexImage")
    base_tex.image = base_image
    
    # Use ColorRamp to convert to grayscale
    color_ramp = nodes.new("ShaderNodeValToRGB")
    color_ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
    color_ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
    
    # Use Bump node to create normal effect
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.5
    bump.inputs["Distance"].default_value = 1.0
    
    # Connect nodes
    links.new(base_tex.outputs["Color"], color_ramp.inputs["Fac"])
    links.new(color_ramp.outputs["Color"], bump.inputs["Height"])
    
    # This is a simplified approach - in practice, you'd need to bake this
    # For now, we'll create a procedural normal map effect
    
    # Clean up temporary material
    bpy.data.materials.remove(temp_mat)
    
    return normal_image


def create_roughness_map_from_base(base_image):
    """Create roughness map by inverting and adjusting base image"""
    width, height = base_image.size
    roughness_image = bpy.data.images.new(
        name=f"{base_image.name}_roughness",
        width=width,
        height=height,
        alpha=False
    )
    
    # Copy and modify pixel data (simplified approach)
    # In a real scenario, you'd process the pixel data
    # For now, we'll use the base image with different settings
    
    return roughness_image


def create_metallic_map_from_base(base_image):
    """Create metallic map from base image using threshold"""
    width, height = base_image.size
    metallic_image = bpy.data.images.new(
        name=f"{base_image.name}_metallic",
        width=width,
        height=height,
        alpha=False
    )
    
    return metallic_image


def assign_material(obj_name, texture_path):
    obj = bpy.data.objects.get(obj_name)
    if not obj:
        print(f"⚠️ Warning: '{obj_name}' not found!")
        return

    # Load base texture
    base_image = bpy.data.images.load(texture_path)
    base_name = os.path.splitext(os.path.basename(texture_path))[0]

    # Create material
    mat = bpy.data.materials.new(name=f"{obj_name}_Mat")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear default nodes
    nodes.clear()
    
    # Create main nodes
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    output = nodes.new("ShaderNodeOutputMaterial")
    
    # Position nodes
    bsdf.location = (0, 0)
    output.location = (400, 0)
    
    # Connect BSDF to output
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    
    # === BASE COLOR TEXTURE ===
    base_tex = nodes.new("ShaderNodeTexImage")
    base_tex.location = (-600, 300)
    base_tex.image = base_image
    base_tex.label = "Base Color"
    links.new(base_tex.outputs["Color"], bsdf.inputs["Base Color"])
    
    print(f"📸 Creating enhanced material for {base_name}...")
    
    # === PROCEDURAL NORMAL MAP ===
    # Create a normal map effect using nodes
    base_tex_normal = nodes.new("ShaderNodeTexImage")
    base_tex_normal.location = (-600, 0)
    base_tex_normal.image = base_image
    base_tex_normal.label = "Normal Source"
    
    # Convert to grayscale for height
    rgb_to_bw = nodes.new("ShaderNodeRGBToBW")
    rgb_to_bw.location = (-400, 0)
    
    # Create bump/displacement effect
    bump = nodes.new("ShaderNodeBump")
    bump.location = (-200, 0)
    bump.inputs["Strength"].default_value = 0.3
    bump.inputs["Distance"].default_value = 0.1
    
    # Connect normal map chain
    links.new(base_tex_normal.outputs["Color"], rgb_to_bw.inputs["Color"])
    links.new(rgb_to_bw.outputs["Val"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    
    print(f"✅ Procedural normal map created")
    
    # === PROCEDURAL ROUGHNESS MAP ===
    base_tex_rough = nodes.new("ShaderNodeTexImage")
    base_tex_rough.location = (-600, -300)
    base_tex_rough.image = base_image
    base_tex_rough.label = "Roughness Source"
    
    # Convert to BW and invert for roughness
    rgb_to_bw_rough = nodes.new("ShaderNodeRGBToBW")
    rgb_to_bw_rough.location = (-400, -300)
    
    # Invert the values (dark = rough, bright = smooth)
    invert = nodes.new("ShaderNodeInvert")
    invert.location = (-200, -300)
    
    # Adjust contrast
    color_ramp_rough = nodes.new("ShaderNodeValToRGB")
    color_ramp_rough.location = (-100, -300)
    # Adjust the color ramp for better contrast
    color_ramp_rough.color_ramp.elements[0].position = 0.3
    color_ramp_rough.color_ramp.elements[1].position = 0.8
    
    # Connect roughness chain
    links.new(base_tex_rough.outputs["Color"], rgb_to_bw_rough.inputs["Color"])
    links.new(rgb_to_bw_rough.outputs["Val"], invert.inputs["Color"])
    links.new(invert.outputs["Color"], color_ramp_rough.inputs["Fac"])
    links.new(color_ramp_rough.outputs["Color"], bsdf.inputs["Roughness"])
    
    print(f"✅ Procedural roughness map created")
    
    # === PROCEDURAL METALLIC MAP ===
    base_tex_metal = nodes.new("ShaderNodeTexImage")
    base_tex_metal.location = (-600, -600)
    base_tex_metal.image = base_image
    base_tex_metal.label = "Metallic Source"
    
    # Convert to BW for metallic
    rgb_to_bw_metal = nodes.new("ShaderNodeRGBToBW")
    rgb_to_bw_metal.location = (-400, -600)
    
    # Use ColorRamp to create metallic threshold
    color_ramp_metal = nodes.new("ShaderNodeValToRGB")
    color_ramp_metal.location = (-200, -600)
    color_ramp_metal.color_ramp.interpolation = 'CONSTANT'
    # Create a sharp threshold at 0.6
    color_ramp_metal.color_ramp.elements[0].position = 0.6
    color_ramp_metal.color_ramp.elements[0].color = (0, 0, 0, 1)  # Non-metallic
    color_ramp_metal.color_ramp.elements[1].position = 0.6
    color_ramp_metal.color_ramp.elements[1].color = (1, 1, 1, 1)  # Metallic
    
    # Connect metallic chain
    links.new(base_tex_metal.outputs["Color"], rgb_to_bw_metal.inputs["Color"])
    links.new(rgb_to_bw_metal.outputs["Val"], color_ramp_metal.inputs["Fac"])
    links.new(color_ramp_metal.outputs["Color"], bsdf.inputs["Metallic"])
    
    print(f"✅ Procedural metallic map created")
    
    # === ADDITIONAL ENHANCEMENTS FOR BLENDER 4.4 ===
    # Set material properties using Blender 4.4 input names
    try:
        # Blender 4.x uses "Subsurface Weight"
        if "Subsurface Weight" in bsdf.inputs:
            bsdf.inputs["Subsurface Weight"].default_value = 0.05
        
        # Adjust IOR for more realistic materials
        if "IOR" in bsdf.inputs:
            bsdf.inputs["IOR"].default_value = 1.45
        
        # Set specular value
        if "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = 0.5
        elif "Specular" in bsdf.inputs:
            bsdf.inputs["Specular"].default_value = 0.8
        
        # Add slight transmission for more interesting materials
        if "Transmission Weight" in bsdf.inputs:
            bsdf.inputs["Transmission Weight"].default_value = 0.02
        
        # Adjust sheen for fabric-like materials
        if "Sheen Weight" in bsdf.inputs:
            bsdf.inputs["Sheen Weight"].default_value = 0.1
        
    except KeyError as e:
        print(f"⚠️ Warning: Could not set material property: {e}")
        pass
    
    # Assign material to object
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    
    print(f"✅ Enhanced PBR material assigned to {obj_name}")


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
print("🎨 Enhanced PBR materials created using procedural techniques!")