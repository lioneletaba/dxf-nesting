import ezdxf
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import os


# Read DXF and extract shapes
def read_dxf(file_path):
    doc = ezdxf.readfile(file_path)
    msp = doc.modelspace()
    shapes = []
    for entity in msp:
        if entity.dxftype() == "LWPOLYLINE":
            vertices = [(v[0], v[1]) for v in entity.get_points()]
            if vertices:  # Ensure the shape is not empty
                shapes.append(vertices)
    return shapes


# Define the nesting problem using OR-Tools
def nest_shapes(shapes, panel_width, panel_height):
    solver = pywrapcp.Solver("Nesting Problem")

    # Variables
    x = []
    y = []
    for shape in shapes:
        # Calculate bounds for each shape
        width = max(v[0] for v in shape) - min(v[0] for v in shape)
        height = max(v[1] for v in shape) - min(v[1] for v in shape)

        # Ensure bounds are within the panel dimensions
        x.append(solver.IntVar(0, panel_width - width, f"x_{len(x)}"))
        y.append(solver.IntVar(0, panel_height - height, f"y_{len(y)}"))

    # Constraints: No overlap between shapes
    for i in range(len(shapes)):
        for j in range(i + 1, len(shapes)):
            solver.Add(
                solver.Max(
                    x[i] + max(v[0] for v in shapes[i]) - x[j],
                    x[j] + max(v[0] for v in shapes[j]) - x[i],
                    y[i] + max(v[1] for v in shapes[i]) - y[j],
                    y[j] + max(v[1] for v in shapes[j]) - y[i],
                )
                >= 0
            )

    # Objective: Minimize material waste (placeholder)
    objective = solver.Sum([x[i] + y[i] for i in range(len(shapes))])
    solver.Minimize(objective)

    # Solve
    db = solver.Phase(x + y, solver.CHOOSE_FIRST_UNBOUND, solver.ASSIGN_MIN_VALUE)
    solver.NewSearch(db)
    solution = []
    while solver.NextSolution():
        solution = [(x[i].Value(), y[i].Value()) for i in range(len(shapes))]
    solver.EndSearch()

    return solution


# Create output DXF
def create_output_dxf(shapes, positions, panel_width, panel_height, output_path):
    doc = ezdxf.new()
    msp = doc.modelspace()

    for i, (shape, (x_pos, y_pos)) in enumerate(zip(shapes, positions)):
        translated_shape = [(x_pos + pt[0], y_pos + pt[1]) for pt in shape]
        msp.add_lwpolyline(translated_shape)

    # Add bounding box for the panel
    msp.add_lwpolyline(
        [
            (0, 0),
            (panel_width, 0),
            (panel_width, panel_height),
            (0, panel_height),
            (0, 0),
        ]
    )

    doc.saveas(output_path)


# Main Function
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

    if not all_shapes:
        print("No valid shapes found in the input files.")
        return

    # Perform nesting
    panel_width, panel_height = 2800, 2000
    positions = nest_shapes(all_shapes, panel_width, panel_height)

    # Save output
    output_path = os.path.join(output_dir, "output.dxf")
    create_output_dxf(all_shapes, positions, panel_width, panel_height, output_path)


if __name__ == "__main__":
    main()
