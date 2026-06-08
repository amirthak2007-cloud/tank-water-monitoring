import rasterio
from rasterio.mask import mask
import geopandas as gpd
import numpy as np

# ----------------------------------
# INPUT FILES
# ----------------------------------
BOUNDARY_FILE = "tank_boundary.geojson"

FILES = {
    "may": {
        "in": "may2023/water_mask_may.tif",
        "out": "may2023/water_mask_may_clipped.tif"
    },
    "sept": {
        "in": "sept2023/water_mask_sept.tif",
        "out": "sept2023/water_mask_sept_clipped.tif"
    }
}
# ----------------------------------
# LOAD TANK BOUNDARY
# ----------------------------------
tank = gpd.read_file(BOUNDARY_FILE)

# ----------------------------------
# CLIP FUNCTION
# ----------------------------------
def clip_raster(input_raster, output_raster):
    with rasterio.open(input_raster) as src:

        # Reproject boundary if needed
        if tank.crs != src.crs:
            tank_proj = tank.to_crs(src.crs)
        else:
            tank_proj = tank

        geometries = tank_proj.geometry.values

        clipped, transform = mask(
            src,
            geometries,
            crop=True,
            nodata=0
        )

        meta = src.meta.copy()
        meta.update({
            "height": clipped.shape[1],
            "width": clipped.shape[2],
            "transform": transform,
            "driver": "GTiff"
        })

        with rasterio.open(output_raster, "w", **meta) as dst:
            dst.write(clipped)

# ----------------------------------
# RUN
# ----------------------------------
for season, paths in FILES.items():
    clip_raster(paths["in"], paths["out"])
    print(f"{season.upper()} clipping done.")
