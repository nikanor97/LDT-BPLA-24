FROM pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime

# Downloads to user config dir
ADD https://ultralytics.com/assets/Arial.ttf https://ultralytics.com/assets/Arial.Unicode.ttf /root/.config/Ultralytics/

# Install linux packages
# g++ required to build 'tflite_support' package
RUN apt update \
    && apt install --no-install-recommends -y gcc git zip curl htop libgl1-mesa-glx libglib2.0-0 libpython3-dev gnupg g++
# RUN alias python=python3

# Security updates
# https://security.snyk.io/vuln/SNYK-UBUNTU1804-OPENSSL-3314796
RUN apt upgrade --no-install-recommends -y openssl tar

# Create working directory
#RUN mkdir -p /usr/src/ultralytics
#WORKDIR /usr/src/ultralytics

# Copy contents
# COPY . /usr/src/app  (issues as not a .git directory)
#RUN git clone https://github.com/ultralytics/ultralytics /usr/src/ultralytics
#ADD https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt /usr/src/ultralytics/

# Install pip packages
#RUN python3 -m pip install --upgrade pip wheel
#RUN pip install --no-cache -e . albumentations comet tensorboard

# Set environment variables
ENV OMP_NUM_THREADS=1


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_VERSION=1.7.1
ENV PYTHONPATH "${PYTHONPATH}:/app"

RUN pip install "poetry==$POETRY_VERSION"
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

WORKDIR /app
COPY . /app

RUN poetry config installer.max-workers 10
RUN poetry install # --without device
#RUN pip install -r requirements.txt
