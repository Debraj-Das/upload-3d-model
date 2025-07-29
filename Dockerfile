FROM continuumio/miniconda3

# Set working directory
WORKDIR /app

# Copy environment file and app code
COPY environment.yml .
COPY . .

# Create the conda environment
RUN conda env create -f environment.yml

# Install system packages required by Blender
RUN apt-get update && \
    apt-get install -y \
    wget \
    libgl1 \
    libx11-6 \
    libxi6 \
    libxxf86vm1 \
    libxrender1 \
    libxrandr2 \
    libxcursor1 \
    libxinerama1 \
    libglu1-mesa \
    libxkbcommon0 \
    libdbus-1-3 \
    libnss3 \
    libasound2 \
    libatk1.0-0 \
    libcups2 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libgtk-3-0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*


# Download and extract Blender (headless version)
ENV BLENDER_VERSION=3.6.5
ENV BLENDER_SUBVERSION=3.6

RUN wget https://download.blender.org/release/Blender${BLENDER_SUBVERSION}/blender-${BLENDER_VERSION}-linux-x64.tar.xz && \
    tar -xf blender-${BLENDER_VERSION}-linux-x64.tar.xz && \
    mv blender-${BLENDER_VERSION}-linux-x64 /opt/blender && \
    ln -s /opt/blender/blender /usr/local/bin/blender && \
    rm blender-${BLENDER_VERSION}-linux-x64.tar.xz

# Activate the environment
SHELL ["conda", "run", "-n", "upload", "/bin/bash", "-c"]

RUN conda run -n upload python manage.py migrate

RUN conda run -n upload pip install gunicorn

# Collect static files
RUN conda run -n upload python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Start the Django app
CMD ["conda", "run", "-n", "upload", "gunicorn", "admin.wsgi:application", "--bind", "0.0.0.0:8000"]
