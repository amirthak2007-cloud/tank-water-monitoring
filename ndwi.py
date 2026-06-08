import rasterio
from rasterio.features import shapes
from shapely.geometry import shape
from scipy.ndimage import binary_opening, binary_closing
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt

def mask_to_geojson(mask, meta, outfile, season_name, threshold):

    tank = gpd.read_file("tank_boundary.geojson").to_crs(meta["crs"])

    results = []

    for geom, val in shapes(mask.astype("uint8"), transform=meta["transform"]):
        if val:
            results.append(shape(geom))

    # ---------- EMPTY GUARD ----------
    if len(results) == 0:
        print(f"{season_name}: No water detected")
        gpd.GeoDataFrame(geometry=[], crs=meta["crs"]).to_file(outfile, driver="GeoJSON")
        return

    # ---------- BUILD GDF ----------
    gdf = gpd.GeoDataFrame(geometry=results, crs=meta["crs"])

    # ---------- CLIP TO TANK ----------
    gdf = gpd.overlay(gdf, tank, how="intersection")

    # ---------- PROJECT TO METERS ----------
    gdf = gdf.to_crs(3857)

    # ---------- COMPUTE AREA PER POLYGON ----------
    gdf["area_sqkm"] = gdf.geometry.area / 1e6
    gdf["season"] = season_name
    gdf["ndwi_thr"] = threshold

    # ---------- REMOVE NOISE ----------
    gdf = gdf[gdf["area_sqkm"] > 0.01]

    # ---------- MERGE ----------
    gdf = gdf.dissolve(by="season")

    gdf.to_file(outfile, driver="GeoJSON")

def load_bands(folder):
   
    green_path = f"{folder}/B03.jp2"
    nir_path   = f"{folder}/B08.jp2"
    with rasterio.open(green_path) as g:
        green = g.read(1).astype("float32")
        meta = g.meta
    with rasterio.open(nir_path) as n:
        nir = n.read(1).astype("float32")
    return green, nir, meta

def compute_ndwi(green, nir):
    np.seterr(divide='ignore', invalid='ignore')
    ndwi = (green - nir) / (green + nir)
    return ndwi

may_green, may_nir, meta = load_bands("may2023")
sept_green, sept_nir, _ = load_bands("sept2023")

ndwi_may = compute_ndwi(may_green, may_nir)
ndwi_sept = compute_ndwi(sept_green, sept_nir)

print("May NDWI stats:", np.nanmin(ndwi_may), np.nanmax(ndwi_may))
print("Sept NDWI stats:", np.nanmin(ndwi_sept), np.nanmax(ndwi_sept))

water_may = ndwi_may > 0.25
water_sept = ndwi_sept > 0.0

water_may = binary_opening(water_may, np.ones((3,3)))
water_may = binary_closing(water_may, np.ones((5,5)))

water_sept = binary_opening(water_sept, np.ones((3,3)))
water_sept = binary_closing(water_sept, np.ones((5,5)))

water_pixels_may = np.sum(water_may)
water_pixels_sept = np.sum(water_sept)

print("May water pixels:", water_pixels_may)
print("Sept water pixels:", water_pixels_sept)

PIXEL_AREA =100

area_may = water_pixels_may * PIXEL_AREA
area_sept = water_pixels_sept * PIXEL_AREA

print("May water area (sq.km):", area_may / 1e6)
print("Sept water area (sq.km):", area_sept / 1e6)

change_area = area_sept - area_may

print("Water area change (sq.m):", change_area)
print("Water area change (sq.km):", change_area / 1e6)

mask_to_geojson(water_may, meta, "water_season_1.geojson", "May 2023", 0.25)
mask_to_geojson(water_sept, meta, "water_season_2.geojson", "Sept 2023", 0.0)

print("GeoJSONs saved.")
plt.imshow(ndwi_sept, vmin=-0.5, vmax=0.5, cmap='Blues')