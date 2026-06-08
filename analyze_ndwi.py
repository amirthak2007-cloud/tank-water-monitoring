import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

# ----------------------
# 1. Load GeoJSONs
# ----------------------
may = gpd.read_file("water_season_1.geojson")
sept = gpd.read_file("water_season_2.geojson")

# ----------------------
# 2. Merge tiny squares
if not may.empty:
    may = may.dissolve()

if not sept.empty:
    sept = sept.dissolve()
# ----------------------
# 3. Area statistics
# ----------------------
may_area = may.to_crs(3857).area.sum() / 1e6
sept_area = sept.to_crs(3857).area.sum() / 1e6

stats = pd.DataFrame({
    "season": ["May", "Sept"],
    "area_sqkm": [may_area, sept_area]
})

stats.to_csv("ndwi_stats.csv", index=False)

print(stats)

# ----------------------
# 4. Plot comparison
# ----------------------
fig, ax = plt.subplots()

may.plot(ax=ax, alpha=0.4, label="May")
sept.plot(ax=ax, alpha=0.4, label="Sept")

plt.legend()
plt.title("Water Change (NDWI)")
plt.show()
