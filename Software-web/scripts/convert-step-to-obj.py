import os
import sys

import FreeCAD
import Import
import Mesh


def main():
    if len(sys.argv) < 3:
        raise SystemExit("Usage: convert-step-to-obj.py input.step output.obj")

    input_path = os.path.abspath(sys.argv[-2])
    output_path = os.path.abspath(sys.argv[-1])

    doc = FreeCAD.newDocument("RobotStep")
    Import.insert(input_path, doc.Name)
    doc.recompute()

    meshes = []
    for obj in doc.Objects:
        shape = getattr(obj, "Shape", None)
        if shape is None or shape.isNull():
            continue
        mesh = Mesh.Mesh()
        mesh.addFacets(shape.tessellate(0.55))
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


if __name__ == "__main__":
    main()
