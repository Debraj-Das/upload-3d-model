#!/usr/bin/env bash

# Set -euo pipefail:  Exit immediately if a command exits with a non-zero status.
# -e: Exit if a command exits with a non-zero status.
# -u: Treat unset variables as an error.
# -o pipefail:  If a command in a pipeline fails, the whole pipeline fails.
set -euo pipefail

# order of the textures
# seat
# pillow
# Leg

./blender/blender -q -b ./1.blend -P ./rds.py

./blender/blender -q -b ./1.blend -P ./rds.py "./textures/sofa/1.jpg" "./textures/pillow/1.jpg" "./textures/leg/1.jpg"

# textures = {
#     "Seat": "/home/raj/3d-rendering/texture/Fabric_007.jpg",
#     "Pillow": "/home/raj/3d-rendering/texture/file90.jpg",
#     "Leg": "/home/raj/3d-rendering/texture/Leg_Basecolor.jpg",
# }

exit 0
