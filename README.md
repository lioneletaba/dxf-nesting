# DXF Nesting Application

This application processes DXF files for nesting shapes efficiently.
It reads DXF files from an input directory, converts those files to SVG format,
then performs nesting operations, and outputs the result to a DXF file.

# Project Structure

## Data Directory Structure

The application uses a `examples` directory that must be organized as follows:

### Input Directory (`examples/input/dxf`)

- Place all your DXF files that need to be nested in this directory
- Supported file types: `.dxf`
- All files in this directory will be processed together

### Output Directory (`examples/output/{file_type}`)

_file_type_ can be svg or dxf

- The nested result will be saved here as `output.dxf`
- Created automatically if it doesn't exist
- Previous results will be overwritten

## Running

There are multiple implementations of the nesting algorithm at the root of the Project
To run one of them, just use python followed by the name of the file containing the implementation you want to run

```bash
python main.py
```

````

## Running with Docker

1. First-time setup:
   Create the "data/input" folder and copy your DXF files into it.

```bash
# Create required directories
mkdir -p examples/input examples/output

# Copy your DXF files
cp your-files/*.dxf examples/input/e
````

2. Run the container:

```bash
docker run -v "$(pwd)/examples:/app/examples" nesting-app:latest
```

### The result of the nesting will be a dxf file in the examples/output/dxf folder
