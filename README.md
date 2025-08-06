# Django Project Documentation

This document describes the functionality and usage of a Django application for uploading 3D model projects, managing texture parts, rendering images, and providing REST API endpoints to access project resources.

---

## Table of Contents

1. [Overview](#overview)
2. [Uploading a Model](#uploading-a-model)
3. [Rendering 360 Images](#rendering-360-images)
4. [Deleting a Project](#deleting-a-project)
5. [API Endpoints](#api-endpoints)

    - [Model File](#model-file-api)
    - [Texture Files](#texture-files-api)
    - [Rendered Images](#rendered-images-api)

6. [Project Structure](#project-structure)
7. [Use Cases](#use-cases)

---

## Overview

The application allows users to:

- Upload a 3D model along with texture parts.
- Automatically assign a unique project name.
- Render 360-degree views using a Blender-based backend.
- Access model files, textures, and rendered outputs through RESTful APIs.

---

## Uploading a Model

### Form Fields:

- **project_name**: A readable name entered by the user.
- **model_file**: The uploaded .blend or .obj file.
- **object_names\[]**: A list of object part names (e.g., "seat", "pillow").
- **textures\_{i}\[]**: Multiple files per texture part (indexed).

### Backend:

- Validates input fields.
- Generates a unique project name using UUID.
- Stores uploaded files in appropriate directories.

---

## Rendering 360 Images

### Button:

A button labeled `Generate 360 images` triggers rendering.

### Backend:

- `POST /generate_images/` with `project_id`.
- Calls Blender rendering script: `render_project_images(project)`.
- Stores output images under `MEDIA_ROOT/output/{project_name}/`.

---

## Deleting a Project

### Backend:

- Endpoint: `/delete_project/<pk>/`
- Deletes:

    - Model files
    - Texture files
    - Rendered output
    - Logs and error files

---

## API Endpoints

### 1. Model File API

- **Endpoint:** `/api/<project_name>/model`
- **Method:** `GET`
- **Response:**

```json
{
    "model_file": "/media/uploads/models/uuid_name.blend"
}
```

### 2. Texture Files API

- **Endpoint:** `/api/<project_name>/textures`
- **Method:** `GET`
- **Response:**

```json
{
  "textures": [
    {
      "object_name": "seat",
      "files": ["/media/uploads/textures/.../seat_diffuse.png"]
    },
    ...
  ]
}
```

### 3. Rendered Images API

- **Endpoint:** `/api/<project_name>/images?object_name=<texture_id>`
- **Method:** `GET`
- **Supports:** Multiple `object_name` queries
- **Response:**

```json
{
  "images": [
    "/media/output/uuid_name/seat_001.png",
    ...
  ]
}
```

### Notes:

- `object_name=<texture_id>` filters images by object.
- If omitted, all images for the project are returned.

---

## Project Structure

```
/media/
├── uploads/
│   ├── models/{project_name}/...
│   └── textures/{project_name}/...
├── output/{project_name}/...
├── logs/{project_name}.log
├── errs/{project_name}.err
```

---

## Use Cases

### 1. Upload a Sofa Model with Textures

- Fill form with: `project_name = "My Sofa"`, upload `sofa.blend`, provide textures.
- Submit → Project created and visible in `/projects/`.

### 2. Generate Images

- Open project detail page.
- Click `Generate 360 images`.
- Blender runs in the background; images appear in project view.

### 3. Access via API

- Model: `GET /api/{project_name}/model`
- Textures: `GET /api/{project_name}/textures`
- Renders: `GET /api/{project_name}/images?object_name=seat&object_name=pillow`

---

## Future Improvements

- Add authentication for API access.
- Implement progress tracking for rendering.
- Support more formats for upload/rendering.
