FROM python:3.11-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

RUN apt-get update && apt-get install -y cmake build-essential
# Install system dependencies and uv
RUN apt-get update && apt-get install -y \
  gcc \
  python3-dev \
  libboost-all-dev \
  libclipper-dev \
  git \
  && rm -rf /var/lib/apt/lists/*

# Install Clipper library
RUN git clone https://github.com/AngusJohnson/Clipper2.git /tmp/clipper && \
  cd /tmp/clipper/CPP && \
  mkdir build && \
  cd build && \
  cmake .. && \
  make && \
  make install && \
  ldconfig && \
  rm -rf /tmp/clipper


# Set CLIPPER_PATH environment variable
ENV CLIPPER_PATH=/usr/local

# Copy project files
COPY pyproject.toml .

RUN echo ${CLIPPER_PATH}

# Configure CMake manually
# RUN mkdir -p /app/build && \
#   cd /app/build && \
#   cmake .. \
#   -DCMAKE_LIBRARY_OUTPUT_DIRECTORY=/app/build \
#   -DPYTHON_EXECUTABLE=$(which python) \
#   -DCLIPPER_INCLUDE_DIRS=${CLIPPER_PATH}/include \
#   -DCLIPPER_LIBRARIES=${CLIPPER_PATH}/lib/libclipper.a && \
#   make


# Install dependencies using uv
RUN pip install . \
  --global-option=build_ext \
  --global-option="-DCLIPPER_INCLUDE_DIRS=${CLIPPER_PATH}/include" \
  --global-option="-DCLIPPER_LIBRARIES=${CLIPPER_PATH}/lib/libclipper.a"

COPY . .

# Create data directory
RUN mkdir /app/data

RUN python main.py
# Set the entrypoint
# ENTRYPOINT ["python", "main.py"]