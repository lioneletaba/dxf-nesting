# DXF Nesting Application

This application processes DXF files for nesting shapes efficiently. It reads DXF files from an input directory, performs nesting operations, and outputs the result to a DXF file.

## Project Structure

## Data Directory Structure

The application uses a `data` directory that must be organized as follows:

### Input Directory (`data/input/`)

- Place all your DXF files that need to be nested in this directory
- Supported file types: `.dxf`
- All files in this directory will be processed together

### Output Directory (`data/output/`)

- The nested result will be saved here as `output.dxf`
- Created automatically if it doesn't exist
- Previous results will be overwritten

## Running

There are multiple implementations of the nesting algorithm at the root of the Project
To run one of them, just use python followed by the name of the file containing the implementation you want to run

```bash
python packer.py
```

````

## Running with Docker

1. First-time setup:
   Create the "data/input" folder and copy your DXF files into it.

```bash
# Create required directories
mkdir -p data/input data/output

# Copy your DXF files
cp your-files/*.dxf data/input/e
````

2. Run the container:

```bash
docker run -v "$(pwd)/data:/app/data" nesting-app:latest
```

### The result of the nesting will be a dxf file in the data/output folder
