import os
from datetime import datetime

from src.converter import FormatConverter
from src.svgpack import SVGPacker

INPUT_DIR = "examples/input"
OUTPUT_DIR = "examples/output"


def main():
    # Convert all the input dxf files into svg files
    input_dxf_path = f"{INPUT_DIR}/dxf"
    input_svg_path = f"{INPUT_DIR}/svg"

    output_dxf_path = f"{OUTPUT_DIR}/dxf"
    output_svg_path = f"{OUTPUT_DIR}/svg"
    FormatConverter.dxf_to_svg(input_dxf_path, input_svg_path)

    # Perform the nesting using the SVGPacker on the SVG files

    DEFAULT_NUMBER_OF_INSTANCES = 1
    files = {
        # 'part1.svg': 1,
        # 'part2.svg': 2
    }

    output_file_name = f"nested_svg_{datetime.now().timestamp()}.svg"
    for filename in os.listdir(input_svg_path):
        if filename.lower().endswith(".svg"):
            file_path = os.path.join(input_svg_path, filename)
            files[file_path] = DEFAULT_NUMBER_OF_INSTANCES

    # nest in a 2800 x 2000 mm plate, saving to combined.svg
    SVGPacker.nest(
        os.path.join(output_svg_path, output_file_name), files, 2800, 2000, False
    )
    print("SVG Nesting sucessful")

    # Convert the nested SVG result into dxf

    FormatConverter.svg_to_dxf(output_svg_path, output_dxf_path)
    print("SVG output successfully converted to DXF")


if __name__ == "__main__":
    main()
