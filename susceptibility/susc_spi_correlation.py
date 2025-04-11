# 1) open every spi1 3 6 12 and calculate the mean value for each month
# 2) for that month compute the area at high susceptibility (>= lv2)
# 3) append to a dataframe

import os 
from rasterio.mask import mask as riomask
import rasterio as rio
import geopandas as gpd
import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt

# 1
years = list(range(2007, 2024))
months = list(range(1, 13))
yearmonths = [f"{year}_{month}" for year in years for month in months]
months_aggregation = [1, 3, 6, 12]
spi_path = '/home/sadc/share/project/calabria/data/raw/spi'
calabria_path = '/home/sadc/share/project/calabria/data/aoi/calabria.geojsonl.json'
calabria = gpd.read_file(calabria_path)
calabria = calabria.to_crs(epsg=4326)
calabria_geom = calabria.geometry.values[0]
vs_susc = 'v4'
susc_thresholds_file = f'/home/sadc/share/project/calabria/data/susceptibility/{vs_susc}/thresholds/thresholds.json'
high_threshold = json.load(open(susc_thresholds_file))['lv2']

corr_df = pd.DataFrame()
for year in years:
    for month in months:

        print(f"{year}-{month:02d}")

        # put susc 
        susc_file = f"/home/sadc/share/project/calabria/data/susceptibility/{vs_susc}/susc_calabria_{year}_{month}.tif"
        with rio.open(susc_file) as src:
            susc_arr = src.read(1)
        susc_arr = np.where(susc_arr >= high_threshold, 1, 0)
        high_susc_pixels = np.sum(susc_arr)
        del susc_arr
        
        corr_df.loc[f'{year}_{month}', f'pixels_high_susc'] = int(high_susc_pixels)

        for aggr in months_aggregation:

            base_folderpath = os.path.join(spi_path, str(aggr), str(year), f'{month:02}')
            day_of_interest = os.listdir(base_folderpath)[-1]
            folderpath = os.path.join(base_folderpath, day_of_interest)
            tile_file = os.path.join(folderpath, f'CHIRPS2-SPI{aggr}_{year}{month:02}{day_of_interest}_tile4.tif')
            
            with rio.open(tile_file) as src:
                out_image, _ = riomask(src, [calabria_geom], crop = True, nodata = -9999)
            # compute mean value excluding -9999
            out_image[out_image == -9999] = np.nan
            mean_spi = np.nanmean(out_image)
            corr_df.loc[f'{year}_{month}', f'spi{aggr}'] = round(mean_spi, 2)

#add fires
fires_file = '/home/sadc/share/project/calabria/data/raw/burned_area/incendi_dpc_2007_2023_calabria_3857.shp'
fires = gpd.read_file(fires_file)
fires['date_iso'] = pd.to_datetime(fires['date_iso'])
fires['year'] = fires['date_iso'].dt.year
fires['month'] = fires['date_iso'].dt.month
#eval area for each month of the year
for year in years:
    for month in months:
        print(f"{year}-{month:02d}")
        # get the area of the burned area
        month_fires = fires[(fires['year'] == year) & (fires['month'] == month)]
        if len(month_fires) > 0:
            month_area = month_fires.area.sum() / 10000
        else:
            month_area = 0
        corr_df.loc[f'{year}_{month}', 'burned_area'] = int(month_area)

# corr matrix
corr = corr_df.corr(method='pearson')
#plot
fig, ax = plt.subplots(figsize=(8, 6))
cax = ax.matshow(corr, cmap='coolwarm')

# Add colorbar
plt.colorbar(cax)

# Set ticks and labels
ax.set_xticks(range(len(corr.columns)))
ax.set_yticks(range(len(corr.columns)))
ax.set_xticklabels(corr.columns, rotation=45, ha='left')
ax.set_yticklabels(corr.columns)

# Optional: add values in each cell
for (i, j), val in np.ndenumerate(corr.values):
    ax.text(j, i, f'{val:.2f}', ha='center', va='center', color='black')

plt.tight_layout()

