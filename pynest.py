import ezdxf
import os
from pynest2d import run_nest, Item, Box  # Import from pynest2d


# Read DXF files and extract shapes
def read_dxf(file_path):
    doc = ezdxf.readfile(file_path)
    msp = doc.modelspace()
    shapes = []
    for entity in msp:
        if (
            entity.dxftype() == "LINE"
            or entity.dxftype() == "CIRCLE"
            or entity.dxftype() == "LWPOLYLINE"
        ):
            # Extract vertices or properties of the shape
            if entity.dxftype() == "LWPOLYLINE":
                vertices = [(v[0], v[1]) for v in entity.get_points("xy")]
                shapes.append(vertices)
            elif entity.dxftype() == "CIRCLE":
                center = (entity.dxf.center.x, entity.dxf.center.y)
                radius = entity.dxf.radius
                shapes.append((center, radius))
            elif entity.dxftype() == "LINE":
                start = (entity.dxf.start.x, entity.dxf.start.y)
                end = (entity.dxf.end.x, entity.dxf.end.y)
                shapes.append((start, end))
    return shapes


# Convert shapes into pynest2d Items
def create_items(shapes):
    items = []
    for shape in shapes:
        if isinstance(shape[0], tuple) and len(shape) > 2:  # Polygon
            item = Item.from_polyline(shape)
        elif isinstance(shape[0], tuple) and len(shape) == 2:  # Circle approximation
            center, radius = shape
            item = Item.from_circle(center, radius)
        else:
            continue  # Unsupported shape
        items.append(item)
    return items


# Perform nesting using pynest2d
def nest_shapes(items, panel_width, panel_height):
    container = Box(panel_width, panel_height)
    nested_items = run_nest(items, container)
    return nested_items


# Create output DXF file
def create_output_dxf(nested_items, output_path):
    doc = ezdxf.new()
    msp = doc.modelspace()

    for item in nested_items:
        if item.is_polygon():
            vertices = item.as_polygon()
            msp.add_lwpolyline(vertices, close=True)
        elif item.is_circle():
            center, radius = item.as_circle()
            msp.add_circle(center, radius)

    doc.saveas(output_path)


def main():
    input_dir = "data/input"
    output_dir = "data/output"

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Read all DXF files from input directory
    all_shapes = []
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".dxf"):
            file_path = os.path.join(input_dir, filename)
            shapes = read_dxf(file_path)
            all_shapes.extend(shapes)

    # Process all shapes together
    items = create_items(all_shapes)
    nested_items = nest_shapes(items, 2800, 2000)

    # Save output
    output_path = os.path.join(output_dir, "output.dxf")
    create_output_dxf(nested_items, output_path)


if __name__ == "__main__":
    main()
