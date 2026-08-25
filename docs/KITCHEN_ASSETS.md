# Kitchen assets and licensing

`kitchen.world` is self-contained: it has no Fuel or other remote runtime
references. New material maps are 1K JPG files deliberately kept small for a
source repository and are used locally through `model://KitchenMaterials`.

## Existing repository assets

No existing visual model is instantiated by `kitchen.world`. The contribution
uses the repository's established `models/<ModelName>` and `model://ModelName`
layout for its new material bundle, without copying existing assets.

## New CC0 assets

All entries below are Poly Haven assets distributed under [CC0 1.0](https://polyhaven.com/license).
The files are unmodified downloads; they are paired as diffuse, normal, and
roughness maps and used in the Gazebo PBR material declarations.

| Local files | Asset / author | Source | Use |
|---|---|---|---|
| `models/KitchenMaterials/textures/brown_floor_tiles_{Diffuse,nor_gl,Rough}_1k.jpg` | Brown Floor Tilles — Rob Tuytel | https://polyhaven.com/a/brown_floor_tiles | Kitchen floor |
| `models/KitchenMaterials/textures/oak_wood_planks_{Diffuse,nor_gl,Rough}_1k.jpg` | Oak Wood Planks — Dimitrios Savva | https://polyhaven.com/a/oak_wood_planks | Cabinet fronts and dining table/chairs |
| `models/KitchenMaterials/textures/granite_tile_03_{Diffuse,nor_gl,Rough}_1k.jpg` | Granite Tile 03 — Charlotte Baglioni | https://polyhaven.com/a/granite_tile_03 | Countertops and island top |
| `models/KitchenMaterials/textures/denim_fabric_{Diffuse,nor_gl,Rough}_1k.jpg` | Denim Fabric — Rob Tuytel | https://polyhaven.com/a/denim_fabric | Sink mat |

No screenshots, logos, remote model references, or unclear-license content are
included.
