import os

import FreeCAD
import Import
import Mesh


input_path = r"D:\Projects\WALL-E\doc\三维建模资料\source\可编辑瓦力\Wall-e_Assembly_NotForPrinting.STEP"
output_path = r"D:\Projects\WALL-E\Software-web\public\models\robot-full.obj"

doc = FreeCAD.newDocument("RobotStep")
Import.insert(input_path, doc.Name)
doc.recompute()

meshes = []
for obj in doc.Objects:
    shape = getattr(obj, "Shape", None)
    if shape is None or shape.isNull() or getattr(shape, "Volume", 0.0) <= 0:
        continue

    placed_shape = shape.copy()
    placement = getattr(obj, "getGlobalPlacement", None)
    if callable(placement):
        placed_shape.Placement = obj.getGlobalPlacement()
    else:
        placed_shape.Placement = getattr(obj, "Placement", FreeCAD.Placement())

    mesh = Mesh.Mesh()
    mesh.addFacets(placed_shape.tessellate(14.0))
    if mesh.CountFacets:
        meshes.append(mesh)

if not meshes:
    raise RuntimeError("No meshable shapes found in STEP file")

combined = Mesh.Mesh()
for mesh in meshes:
    combined.addMesh(mesh)

os.makedirs(os.path.dirname(output_path), exist_ok=True)
combined.write(output_path)
print(f"Converted {len(meshes)} shapes")
print(f"Wrote {output_path}")
