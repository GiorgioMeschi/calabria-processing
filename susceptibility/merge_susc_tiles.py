
import os
from geospatial_tools import geotools as gt
import numpy as np
import rasterio as rio


basep = '/home/sadc/share/project/calabria/data/ML'
vs = 'v4'
tiles = os.listdir(basep)
tiles = [tile for tile in tiles if os.path.isdir(os.path.join(basep, tile))]

years = list(range(2024, 2025))
months = list(range(1, 13))

# check existance
# for tile in tiles:
#     for year in years:
#         for month in months:
#             filepath = f"{basep}/{tile}/susceptibility/annual_maps/Annual_susc_{year}_{month}.tif"
            
#             # check existance
#             if not os.path.exists(filepath):
#                 print(f"Missing: {filepath}")
#                 continue

ras = gt.Raster()

for year in years:
    for month in months:
        print(f"{year}-{month:02d}...")
        outfile = f'/home/sadc/share/project/calabria/data/susceptibility/{vs}/susc_calabria_{year}_{month}.tif'
        if not os.path.exists(outfile):
            # merge tiles
            files_to_merge = [f"{basep}/{tile}/susceptibility/{vs}/{year}_{month}/susceptibility/annual_maps/Annual_susc_{year}_{month}.tif"
                            for tile in tiles]


            out = ras.merge_rasters(outfile, np.nan, 'first', *files_to_merge)

            # with rio.open(outfile) as src:
            #     ras.plot_raster(src)
#%%  corrent nan to -1

files = os.listdir('/home/sadc/share/project/calabria/data/susceptibility/v4')
files = [f for f in files if f.endswith('.tif')]

for file in files:
    filepath = os.path.join('/home/sadc/share/project/calabria/data/susceptibility/v4', file)
    with rio.open(filepath) as src:
        arr = src.read(1)
        arr[np.isnan(arr)] = -1
        out_meta = src.meta.copy()
        out_meta.update({
            'compress': 'lzw',
            'tiled': True,
            'blockxsize': 256,
            'blockysize': 256,
        })
        with rio.open(filepath, 'w', **out_meta) as dst:
            dst.write(arr, 1)
        




