import geopandas as gpd
import rasterio
import numpy as np

UTM = 32644


def compute_volume(water_tif):

    # load raster mask
    with rasterio.open(water_tif) as src:
        mask = src.read(1)
        pixel_area = abs(src.transform.a * src.transform.e)

    water_pixels = mask > 0
    water_area = water_pixels.sum() * pixel_area   # m²

    # load elevations
    contours = gpd.read_file("contours.geojson").to_crs(UTM)

    bottom = contours["CONTOUR_ELEVATION"].min()
    top    = contours["CONTOUR_ELEVATION"].max()

    avg_depth = (top - bottom) / 2

    volume = water_area * avg_depth

    return float(volume)


def compute_capacity():

    contours = gpd.read_file("contours.geojson").to_crs(UTM)

    bottom = contours["CONTOUR_ELEVATION"].min()
    top    = contours["CONTOUR_ELEVATION"].max()

    total_area = contours.union_all().area

    avg_depth = (top - bottom) / 2

    return float(total_area * avg_depth)