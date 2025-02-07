import os

import matplotlib.pyplot as plt
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.filemanagement import readfile, new

from ezdxf.addons.drawing.properties import RenderContext
from ezdxf.addons.drawing.frontend import Frontend
from svg.path import parse_path
from xml.dom import minidom

DXF_PATH = "data/input/dxf"
SVG_PATH = "data/input/svg"


class FormatConverter:
    @classmethod
    def _convert_paths(cls, svg_doc, msp):
        paths = svg_doc.getElementsByTagName("path")
        for path in paths:
            d = path.getAttribute("d")
            if d:
                # Parse the path data
                path_data = parse_path(d)
                points = []

                # Sample points along the path
                for i in range(100):
                    point = path_data.point(i / 99)
                    points.append((point.real, point.imag))

                if len(points) > 1:
                    # Create a polyline from the points
                    msp.add_polyline2d(points)

    @classmethod
    def _convert_circles(cls, svg_doc, msp):
        circles = svg_doc.getElementsByTagName("circle")
        for circle in circles:
            cx = float(circle.getAttribute("cx") or 0)
            cy = float(circle.getAttribute("cy") or 0)
            r = float(circle.getAttribute("r") or 0)

            # Add circle to DXF
            msp.add_circle((cx, cy), r)

    @classmethod
    def _convert_rectangles(cls, svg_doc, msp):
        rects = svg_doc.getElementsByTagName("rect")
        for rect in rects:
            x = float(rect.getAttribute("x") or 0)
            y = float(rect.getAttribute("y") or 0)
            width = float(rect.getAttribute("width") or 0)
            height = float(rect.getAttribute("height") or 0)

            # Create rectangle as a closed polyline
            points = [
                (x, y),
                (x + width, y),
                (x + width, y + height),
                (x, y + height),
                (x, y),
            ]
            msp.add_polyline2d(points)

    @classmethod
    def _convert_lines(cls, svg_doc, msp):
        lines = svg_doc.getElementsByTagName("line")
        for line in lines:
            x1 = float(line.getAttribute("x1") or 0)
            y1 = float(line.getAttribute("y1") or 0)
            x2 = float(line.getAttribute("x2") or 0)
            y2 = float(line.getAttribute("y2") or 0)

            # Add line to DXF
            msp.add_line((x1, y1), (x2, y2))

    @classmethod
    def dxf_to_svg(cls, input_path=DXF_PATH, output_path=SVG_PATH):
        # Ensure the output directory exists
        os.makedirs(output_path, exist_ok=True)

        for filename in os.listdir(input_path):
            if filename.lower().endswith(".dxf"):
                dxf_path = os.path.join(input_path, filename)
                svg_filename = f"{os.path.splitext(filename)[0]}.svg"
                svg_path = os.path.join(output_path, svg_filename)

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

    @classmethod
    def svg_to_dxf(cls, input_path=SVG_PATH, output_path=DXF_PATH):
        # Ensure the output directory exists
        os.makedirs(output_path, exist_ok=True)

        for filename in os.listdir(input_path):
            if filename.lower().endswith(".svg"):
                svg_path = os.path.join(input_path, filename)
                dxf_filename = f"{os.path.splitext(filename)[0]}.dxf"
                dxf_path = os.path.join(output_path, dxf_filename)

                try:
                    # Create a new DXF document
                    doc = new("R2010")
                    msp = doc.modelspace()

                    # Parse SVG file
                    svg_doc = minidom.parse(svg_path)

                    # Convert SVG elements to DXF entities
                    cls._convert_paths(svg_doc, msp)
                    cls._convert_circles(svg_doc, msp)
                    cls._convert_rectangles(svg_doc, msp)
                    cls._convert_lines(svg_doc, msp)

                    # Save the DXF file
                    doc.saveas(dxf_path)
                    print(f"Successfully converted {filename} to {dxf_filename}")

                    # Clean up
                    svg_doc.unlink()

                except Exception as e:
                    print(f"Failed to convert {filename}: {e}")
