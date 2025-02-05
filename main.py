import ezdxf
from nest2D import Nest2D, Box, Item
import os


# Lecture des fichiers DXF
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
            shapes.append(entity)
    return shapes


# Création des items pour le nesting
def create_items(shapes):
    items = []
    for shape in shapes:
        # Convertir la forme en un objet Item de nest2d
        # (cette partie dépend de la complexité des formes)
        item = Item(shape)
        items.append(item)
    return items


# Nesting
def nest_shapes(items, panel_width, panel_height):
    nest = Nest2D(items, Box(panel_width, panel_height))
    nest.execute()
    return nest


# Création des fichiers DXF de sortie
def create_output_dxf(nest, output_path):
    doc = ezdxf.new()
    msp = doc.modelspace()
    for item in nest.get_items():
        # Ajouter chaque item au fichier DXF
        # (cette partie dépend de la manière dont vous avez converti les formes)
        pass
    doc.saveas(output_path)


def main():
    input_dir = "data/input"
    output_dir = "data/output"
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Read all DXF files from input directory
    all_shapes = []
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.dxf'):
            file_path = os.path.join(input_dir, filename)
            shapes = read_dxf(file_path)
            all_shapes.extend(shapes)
    
    # Process all shapes together
    items = create_items(all_shapes)
    nest = nest_shapes(items, 2800, 2000)
    
    # Save output
    output_path = os.path.join(output_dir, "output.dxf")
    create_output_dxf(nest, output_path)


if __name__ == "__main__":
    main()
