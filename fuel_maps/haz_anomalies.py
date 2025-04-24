

import geopandas as gpd
from geospatial_tools import geotools as gt
import os
import numpy as np
import pandas as pd

Raster = gt.Raster()

# input files 
datapath = '/home/sadc/share/project/calabria/data'
haz_static_file = f'{datapath}/fuel_maps/static/FUEL_MAP.tif'
haz_monthly_folder = f'{datapath}/fuel_maps/v4'
ba_file = f'{datapath}/raw/burned_area/incendi_dpc_2007_2023_calabria_3857.shp'

# settings
years = list(range(2007, 2025))
months = list(range(1, 13))
yearmonths = [f'{year}_{month}' for year in years for month in months]

# initial data
static_fuel = Raster.read_1band(haz_static_file)
h3_static = np.where(static_fuel == 3, 1, 0).sum()
h6_static = np.where(static_fuel == 6, 1, 0).sum()
h9_static = np.where(static_fuel == 9, 1, 0).sum()
h12_static = np.where(static_fuel == 12, 1, 0).sum()
static_extents = [h3_static, h6_static, h9_static, h12_static]

ba = gpd.read_file(ba_file)
ba['date_iso'] = pd.to_datetime(ba['date_iso'])

# prepare out lists
areas = []
h3, h6, h9, h12 = [], [], [], []
lists = [h3, h6, h9, h12]

anomaly = lambda montly, static: ((montly / static) - 1) * 100

# eval monthly anomalies
cls = [3,6,9,12]
for month in yearmonths:
    print(month)
    fuel_map_filepath = f'{haz_monthly_folder}/fuel_calabria_{month}.tif'
    fuel = Raster.read_1band(fuel_map_filepath)
    y = int(month.split('_')[0])
    m = int(month.split('_')[1])
    ba_year = ba[ba['date_iso'].dt.year == y]
    ba_month = ba_year[ba_year['date_iso'].dt.month == m]
    area = ba_month.area_ha.sum()
    areas.append(area)
    # eval anomalies and appned in the class list
    for cl, proper_list, static_extent in zip(cls, lists, static_extents):
        h_month = np.where(fuel == cl, 1, 0).sum()
        perc_anomaly = anomaly(h_month, static_extent) # percentage of anomaly, ex: 100% means twice the value
        proper_list.append(perc_anomaly)
        
df = pd.DataFrame({
    'year_month': yearmonths,
    'area_ha': areas,
    'h3': h3,
    'h6': h6,
    'h9': h9,
    'h12': h12
})   


# save
outpath = f'{haz_monthly_folder}/anomalies/anomalies.csv'
os.makedirs(os.path.dirname(outpath), exist_ok=True)
df.to_csv(outpath, index=False)

#%% fancy plot 

import matplotlib.pyplot as plt

df['date'] = pd.to_datetime(df['year_month'].str.replace('_', '-'))

plt.figure(figsize=(30, 8), dpi = 200)

# Curve delle anomalie
plt.plot(df['date'], df['h3'], label='Anomalia Classe 3', linewidth=1.2, marker='o')
plt.plot(df['date'], df['h6'], label='Anomalia Classe 6', linewidth=1.2, marker='s')
plt.plot(df['date'], df['h9'], label='Anomalia Classe 9', linewidth=1.2, marker='^')
plt.plot(df['date'], df['h12'], label='Anomalia Classe 12', linewidth=1.2, marker='d')

# Secondo asse y per l'area bruciata
ax1 = plt.gca()
ax2 = ax1.twinx()
ax2.plot(df['date'], df['area_ha'], color='black', label='Area Bruciata (ha)', linewidth=2, linestyle='--')

# Stile e labels
ax1.set_title("Trend delle Anomalie di Copertura e Aree Bruciate", fontsize=16)
ax1.set_xlabel("Data", fontsize=12)
ax1.set_ylabel("Anomalia (%)", fontsize=12)
ax2.set_ylabel("Area Bruciata (ha)", fontsize=12)
ax1.set_xticks(df['date'])
ax1.set_xticklabels(df['date'].dt.strftime('%Y-%m'), rotation=90, fontsize=8)
ax1.set_xlim(xmax= df['date'].max())

# Legenda combinata
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
plt.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')

plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
#save
plt.savefig(f'{haz_monthly_folder}/anomalies/anomalies_plot.png', dpi=200)

