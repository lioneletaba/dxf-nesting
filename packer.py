from datetime import datetime

from ezdxf.filemanagement import readfile, new
from rectpack import newPacker, PackingMode
import os

from rectpack.maxrects import MaxRectsBaf, MaxRectsBssf, MaxRectsBlsf, MaxRectsBl

INPUT_PATH = "data/input"
OUTPUT_PATH = "data/output"
SUPPORTED_ENTITIES = ["LINE", "CIRCLE", "LWPOLYLINE"]


# Read DXF files
def read_dxf(file_path):
    doc = readfile(file_path)
    msp = doc.modelspace()
    shapes = []
    for entity in msp:
        if entity.dxftype() in SUPPORTED_ENTITIES:
            shapes.append(entity)
    return shapes


def get_shape_bounds(shape):
    x_coords = []
    y_coords = []
    shape_type = shape.dxftype()
    if shape_type == "LINE":
        x_coords = [shape.dxf.start[0], shape.dxf.end[0]]
        y_coords = [shape.dxf.start[1], shape.dxf.end[1]]
    elif shape_type == "CIRCLE":
        radius = shape.dxf.radius
        center = shape.dxf.center
        x_coords = [center[0] - radius, center[0] + radius]
        y_coords = [center[1] - radius, center[1] + radius]
    elif shape_type == "LWPOLYLINE":
        points = list(shape.get_points())
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]

    max_x = max(x_coords)
    min_x = min(x_coords)
    max_y = max(y_coords)
    min_y = min(y_coords)
    width = max_x - min_x
    height = max_y - min_y
    if width <= 0 or height <= 0:
        print(
            f"Unused Shape (invalid width or height) bounds: {width}, {height}, minx{min_x}, miny{min_y}, maxx{max_x}, maxy{max_y}"
        )
    return (width, height)


def pack_shapes(shapes, panel_width, panel_height):
    packer = newPacker(mode=PackingMode.Online, rotation=True)

    # Add the container (panel)
    packer.add_bin(panel_width, panel_height)

    # Add shapes to pack
    for i, shape in enumerate(shapes):
        width, heigth = get_shape_bounds(shape)
        print(f"Adding shape {i} with bounds {width}, {heigth}")
        if width > 0 and heigth > 0:
            packer.add_rect(width, heigth, rid=i)

    # Pack rectangles if necessary, when using the Offline PackingMode
    # packer.pack()

    return packer


def create_output_dxf(packer, shapes, output_path):
    doc = new()
    msp = doc.modelspace()

    # Get the first bin's rectangles (assuming single bin)
    packed_rects = packer.rect_list()

    for rect in packed_rects:
        # rect format: (x, y, width, height, rid)
        print(f"Placing shape {rect[4]} at {rect[0]}, {rect[1]}, {rect}")
        shape_index = rect[-1]  # rid
        original_shape = shapes[shape_index]

        # Transform the original shape and add it to the modelspace
        transform_shape(msp, original_shape, rect)
    doc.saveas(output_path)


def transform_shape(modelspace, shape, rect):
    """
    Transform and add a shape to the modelspace at the specified position

    Args:
        modelspace: The DXF modelspace to add the transformed shape to
        shape: The original shape to transform
        rect: Tuple containing (x, y, width, height, rid) of the new position
    """
    shape_type = shape.dxftype()
    if shape_type == "LINE":
        # Get original line coordinates
        start = shape.dxf.start
        end = shape.dxf.end

        # Calculate translation
        dx = rect[0] - min(start[0], end[0])
        dy = rect[1] - min(start[1], end[1])

        # Create new translated line
        return modelspace.add_line(
            (start[0] + dx, start[1] + dy), (end[0] + dx, end[1] + dy)
        )

    elif shape_type == "CIRCLE":
        # Get original circle properties
        center = shape.dxf.center
        radius = shape.dxf.radius

        # Calculate new center position

        new_center = (
            center.x + radius,  # x position + radius
            center.y + radius,  # y position + radius
        )
        # Create new translated circle
        return modelspace.add_circle(new_center, radius)

    elif shape_type == "LWPOLYLINE":
        # Get original points
        points = list(shape.get_points())
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]

        # Calculate translation
        dx = rect[0] - min(x_coords)
        dy = rect[1] - min(y_coords)

        # Create new translated polyline
        new_points = [(p[0] + dx, p[1] + dy) for p in points]
        return modelspace.add_lwpolyline(new_points)
        # msp.add_entity(original_shape.copy())


def main():
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_PATH, exist_ok=True)

    # Read all DXF files from input directory
    all_shapes = []
    for filename in os.listdir(INPUT_PATH):
        if filename.lower().endswith(".dxf"):
            file_path = os.path.join(INPUT_PATH, filename)
            shapes = read_dxf(file_path)
            all_shapes.extend(shapes)

    # Pack all shapes together
    packer = pack_shapes(all_shapes, 2800, 2000)

    # Save output
    output_path = os.path.join(OUTPUT_PATH, f"{datetime.now().timestamp()}output.dxf")
    create_output_dxf(packer, all_shapes, output_path)


if __name__ == "__main__":
    main()
