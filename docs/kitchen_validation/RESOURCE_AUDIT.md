# Local-resource audit

Commands run against `worlds/kitchen.world`:

```bash
python3 -c "import xml.etree.ElementTree as E; r=E.parse('worlds/kitchen.world').getroot(); print(len(r.findall('.//model')))"
rg -n 'https?://|fuel\.gazebosim|<uri>|<mesh>' worlds/kitchen.world models/KitchenMaterials
```

Result: XML parsed successfully with 23 world models. The reference search
returned no remote URI, Fuel URL, mesh, or model URI. Texture references use
only `model://KitchenMaterials/textures/...`; the twelve referenced 1K JPG maps
are included under that directory. The no-manual-resource launch log confirms
Gazebo resolves the bundle when launched from the installed package.
