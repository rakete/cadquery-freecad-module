# This example is meant to be used from within the CadQuery module of FreeCAD.
import cadquery
from Helpers import show

# The dimensions of the box. These can be modified rather than changing the
# object's code directly.
length = 80.0
height = 60.0
thickness = 10.0
center_hole_dia = 22.0
cbore_hole_diameter = 2.4
cbore_diameter = 4.4
cbore_depth = 2.1

# Create a 3D box based on the dimensions above and add 4 counterbored holes
result = cadquery.Workplane("XY").box(length, height, thickness) \
    .faces(">Z").workplane().hole(center_hole_dia) \
    .faces(">Z").workplane() \
    .rect(length - 8.0, height - 8.0, forConstruction=True) \
    .vertices().cboreHole(cbore_hole_diameter, cbore_diameter, cbore_depth)

# Render the solid
show(result)
