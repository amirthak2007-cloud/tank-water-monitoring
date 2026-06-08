# Tank Water Spread & Storage Monitoring Dashboard

Prototype geospatial dashboard for automated seasonal water spread detection, storage estimation, and reporting using satellite imagery.

## Solution Overview

The system automatically:

1. Computes NDWI from multi-season satellite bands (Green + NIR)
2. Extracts water masks
3. Clips masks to tank boundary
4. Converts masks to polygons
5. Calculates seasonal area (sq km)
6. Estimates storage volume using bathymetric contours
7. Displays everything in an interactive Streamlit+Folium dashboard
8. Exports reports for management use

---

## Features

• Interactive map with layer toggles (May / Sept / boundary)
• Seasonal water spread comparison
• Area statistics
• Volume estimation from elevation contours
• One-click recompute pipeline
• CSV report export

---

## Project Structure

index.py  
- Streamlit dashboard (main app)

ndwi.py  
- NDWI computation and water mask generation

clip_water_mask.py  
- Clips rasters to tank boundary

analyze_ndwi.py  
- Calculates seasonal area statistics and saves ndwi_stats.csv

volume.py  
- Volume estimation using bathymetric contours

tank_boundary.geojson  
- Tank polygon

contours.geojson  
- Elevation contours for volume estimation

may2023/, sept2023/
- Satellite bands and water mask rasters

---

## Installation

### 1. Create environment
```
conda create -n geo python=3.10
conda activate geo
```

### 2. Install dependencies
```
pip install -r requirements.txt
```

---

## Run Dashboard

```
streamlit run index.py
```

Open the local browser link shown.

---

## Workflow

### First time
Place satellite imagery inside:
may2023/
sept2023/

### Then
Click:
Recompute NDWI (sidebar)

The system will automatically:
• clip rasters
• generate masks
• compute areas
• compute volumes
• refresh dashboard

---

## Inputs Required

• Green band (B03.jp2)  
• NIR band (B08.jp2)  
• Tank boundary GeoJSON  
• Contour elevation GeoJSON  

---

## Outputs

• water_season_1.geojson  
• water_season_2.geojson  
• ndwi_stats.csv  
• interactive dashboard  
• optional report export  

---

## Use Case for Water Managers

This tool helps:

• track seasonal storage trends
• estimate usable volume
• detect low storage early
• anticipate overflow risk
• create quick reports for planning

---

## Tech Stack

Python  
Rasterio  
GeoPandas  
Streamlit  
Folium  
NumPy / SciPy  

---

## Future Improvements

• multi-date batch processing  
• rainfall integration  
• time-series charts  
• automated PDF reports  
• cloud deployment  

---

## Authors - Ananya J, Benicia B, Amirtha K - Easwari Engineering College, Chennai

Tank Water Spread Analysis – Mapathon Prototype