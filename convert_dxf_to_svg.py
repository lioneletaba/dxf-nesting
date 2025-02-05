import os

import matplotlib.pyplot as plt
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.filemanagement import readfile

from ezdxf.addons.drawing.properties import RenderContext
from ezdxf.addons.drawing.frontend import Frontend


INPUT_PATH = "data/input"
OUTPUT_PATH = "data/output/svg"


def convert_dxf_to_svg(input_folder, output_folder):
    # Ensure the output directory exists
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".dxf"):
            dxf_path = os.path.join(input_folder, filename)
            svg_filename = f"{os.path.splitext(filename)[0]}.svg"
            svg_path = os.path.join(output_folder, svg_filename)

            try:
                # Load the DXF document
                doc = readfile(dxf_path)

                # Create a matplotlib figure
                fig = plt.figure()
                ax = fig.add_axes((0, 0, 1, 1))
                ctx = RenderContext(doc)
                backend = MatplotlibBackend(ax)
                frontend = Frontend(ctx, backend)

                # Draw the modelspace
                msp = doc.modelspace()
                frontend.draw_layout(msp, finalize=True)

                # Save the figure as an SVG file
                fig.savefig(svg_path)
                plt.close(fig)

                print(f"Successfully converted {filename} to {svg_filename}")

            except Exception as e:
                print(f"Failed to convert {filename}: {e}")


def main():
    convert_dxf_to_svg(INPUT_PATH, OUTPUT_PATH)


if __name__ == "__main__":
    main()
