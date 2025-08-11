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
