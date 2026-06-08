import folium
import geopandas as gpd
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
from volume import compute_volume
import subprocess

if st.sidebar.button("Recompute NDWI"):
    subprocess.run(["python", "ndwi.py"])
    subprocess.run(["python", "analyze_ndwi.py"])
st.title("Tank Water Spread Analysis")

mapObj = folium.Map(location = [13.0, 80.06], zoom_start = 14, tiles = "CartoDB positron",control_scale = True)
tank = gpd.read_file("tank_boundary.geojson")
s1 = gpd.read_file("water_season_1.geojson")
s2 = gpd.read_file("water_season_2.geojson")
contours = gpd.read_file("contours.geojson")

#conversions
metric_crs = s1.crs   # EPSG:32644 (meters)

tank = tank.to_crs(metric_crs)
s2 = s2.to_crs(metric_crs)
contours = contours.to_crs(metric_crs)

#to compute area attributes for the seasonal geojsons for the tooltips
for gdf, name in [(s1, "May"), (s2, "Sept")]:
    gdf["season"] = name
    gdf["area_sqkm"] = gdf.area / 1e6


tank["Area_sqkm"] = tank.area / 1e6

tank = tank.to_crs(4326)
s1 = s1.to_crs(4326)
s2 = s2.to_crs(4326)

folium.GeoJson(
    tank,
    name="Tank Boundary",
    style_function=lambda x: {
        "color": "green",
        "weight": 3,
        "fillOpacity": 0.0
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["dscr1", "dscr2", "Area_sqkm"],
        aliases=["Category:", "Type:", "Area (sq km):"],
        localize=True,
        sticky=True
    )
).add_to(mapObj)

bounds = tank.total_bounds  # [minx, miny, maxx, maxy]
mapObj.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])

#adding seasonal geojsons to streamlit
# -----------------------
# May layer
# -----------------------
fg_may = folium.FeatureGroup(name="Water - May", show=True)

folium.GeoJson(
    s1,
    style_function=lambda x: {
        "color": "cyan",
        "fillColor": "cyan",
        "fillOpacity": 0.6
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["season", "area_sqkm"],
        aliases=["Season:", "Water Area (sq km):"]
    )
).add_to(fg_may)

fg_may.add_to(mapObj)


# -----------------------
# Sept layer
# -----------------------
fg_sept = folium.FeatureGroup(name="Water - Sept", show=True)

folium.GeoJson(
    s2,
    style_function=lambda x: {
        "color": "darkblue",
        "fillColor": "darkblue",
        "fillOpacity": 0.6
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["season", "area_sqkm"],
        aliases=["Season:", "Water Area (sq km):"]
    )
).add_to(fg_sept)

fg_sept.add_to(mapObj)

#stats panel
stats = pd.read_csv("ndwi_stats.csv")
st.sidebar.subheader("Area Stats (sq km)")
st.sidebar.dataframe(stats, width = 'stretch')

#legend
legend_html = """
<div style="
position: fixed;
bottom: 40px;
left: 40px;
background: white;
border-radius: 8px;
padding: 10px;
box-shadow: 0 0 6px rgba(0,0,0,0.3);
font-size: 13px;
color: #545454;
z-index:9999;
">
<b>Legend</b><br>
<span style="color:darkgreen;">■</span> Tank Boundary<br>
<span style="color:cyan;">■</span> Water – May<br>
<span style="color:darkblue;">■</span> Water – Sept<br>
</div>
"""
mapObj.get_root().html.add_child(folium.Element(legend_html))

#volume, capacity, percent of tank filled
vol_may  = compute_volume("may2023/water_mask_may_clipped.tif")
vol_sept = compute_volume("sept2023/water_mask_sept_clipped.tif")

st.sidebar.metric("May Volume (m³)", f"{vol_may:,.0f}")
st.sidebar.metric("Sept Volume (m³)", f"{vol_sept:,.0f}")
st.sidebar.metric("Change (m³)", f"{vol_sept - vol_may:,.0f}")

folium.LayerControl(collapsed = False).add_to(mapObj)

st_folium(mapObj, height=750, width = 'stretch')