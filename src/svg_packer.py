from datetime import datetime
import os

from rectpack import float2dec as _float2dec
from svgpathtools import svg2paths
from svgwrite import Drawing
from svgwrite.container import Group
from svgwrite.path import Path
from svgwrite.shapes import Rect

from rectpack import newPacker, PackingMode

# We can test other packing algorithms like MaxRectsBssf, MaxRectsBlsf, MaxRectsBl
from rectpack.maxrects import MaxRectsBaf


class SVGPacker:
    @staticmethod
    def nest(output, files, wbin, hbin, enclosing_rectangle=True):
        packer = newPacker(
            mode=PackingMode.Offline, pack_algo=MaxRectsBaf, rotation=True
        )

        def float2dec(x):
            return _float2dec(x, 4)

        def bbox_paths(paths):
            if not paths:
                return (0, 0, 0, 0)

            # Initialize bbox with the first path's bounds
            bbox = paths[0].bbox()

            # Expand bbox to include all other paths
            for p in paths[1:]:
                p_bbox = p.bbox()
                bbox = (
                    min(p_bbox[0], bbox[0]),  # xmin
                    max(p_bbox[1], bbox[1]),  # xmax
                    min(p_bbox[2], bbox[2]),  # ymin
                    max(p_bbox[3], bbox[3]),  # ymax
                )

            # Ensure we don't have any floating point precision issues
            return tuple(float2dec(x) for x in bbox)

        all_paths = {}
        # First pass: collect all paths and compute exact bounding boxes
        for svg in files:
            paths, attributes = svg2paths(svg)
            bbox = bbox_paths(paths)

            # Calculate actual dimensions without padding
            width = float2dec(bbox[1] - bbox[0])
            height = float2dec(bbox[3] - bbox[2])

            for i in range(files[svg]):
                rid = svg + str(i)
                all_paths[rid] = {
                    "paths": paths,
                    "bbox": bbox,
                    "width": width,
                    "height": height,
                }
                packer.add_rect(width, height, rid=rid)

        # Pack rectangles
        print("Rectangle packing...")
        while True:
            packer.add_bin(wbin, hbin)
            packer.pack()
            rectangles = {r[5]: r for r in packer.rect_list()}
            if len(rectangles) == len(all_paths):
                break
            print("Not enough space in the bin, adding another")

        combineds = {}

        print("Packing into SVGs...")
        for rid, obj in all_paths.items():
            paths = obj["paths"]
            bbox = obj["bbox"]
            width = obj["width"]
            height = obj["height"]

            bin, x, y, w, h, _ = rectangles[rid]

            # Create or get the SVG drawing
            if bin not in combineds:
                svg_file = output
                if bin != 0:
                    splitext = os.path.splitext(svg_file)
                    svg_file = splitext[0] + ".%s" % bin + splitext[1]
                dwg = Drawing(
                    svg_file,
                    profile="tiny",
                    size=("%smm" % wbin, "%smm" % hbin),
                    viewBox="0 0 %s %s" % (wbin, hbin),
                )
                combineds[bin] = dwg

            combined = combineds[bin]
            group = Group()

            # Determine if rotation is needed
            needs_rotation = (width > height and w < h) or (width < height and w > h)

            if needs_rotation:
                # Apply rotation transformation
                rotate = 90
                dx = -bbox[2]  # Use y-min as x-offset
                dy = -bbox[0]  # Use x-min as y-offset
                # Center the rotation
                group.translate(x + height / 2, y + width / 2)
                group.rotate(rotate, (0, 0))
                group.translate(-height / 2, -width / 2)
            else:
                # No rotation needed
                rotate = 0
                dx = -bbox[0]
                dy = -bbox[2]
                group.translate(x + dx, y + dy)

            # Add paths to group
            for p in paths:
                path = Path(d=p.d())
                path.stroke(color="red", width="1")
                path.fill(opacity=0)
                group.add(path)

            combined.add(group)

        # Save all SVGs
        for combined in combineds.values():
            if enclosing_rectangle:
                r = Rect(size=(wbin, hbin))
                r.fill(opacity=0)
                r.stroke(color="lightgray")
                combined.add(r)

            print("SVG saving...")
            combined.save(pretty=True)
