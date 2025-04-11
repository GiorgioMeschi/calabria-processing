
import os
import rasterio as rio
import multiprocessing as mp
from geospatial_tools import geotools as gt
import numpy as np

ras = gt.Raster()

TILEPATH = '/home/sadc/share/project/calabria/data/ML'

tiles = os.listdir(TILEPATH)

aggrs = [1, 3, 6, 12]

# for aggr in aggrs:
#     for tile in tiles:
def compute_average_spi(tile, aggr):
    tile_path = os.path.join(TILEPATH, tile)
    idx = 0
    print(f'tile {tile} for SPI {aggr} months')
    for year in range(2007, 2025):
        for month in range(1, 13):
            path = os.path.join(tile_path, 'climate_1m_shift', f'{year}_{month}', f'spi_{aggr}m_bilinear_epsg3857.tif')
            #open and add 
            arr = rio.open(path).read(1)
            if idx == 0:
                arr_sum = arr
            else:
                arr_sum += arr
            idx += 1
    #divide by idx
    arr_sum /= idx
    #save the result
    folder = f'/home/sadc/share/project/calabria/data/spi_aggr/{tile}'
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, f'spi_{aggr}m_2007-2024_bilinear_epsg3857.tif')
    ras.save_raster_as(arr_sum, filepath, path, clip_extent=True)

with mp.Pool(20) as pool:
    pool.starmap(compute_average_spi, [(tile, aggr) for tile in tiles for aggr in aggrs])

#%% merge tiles

basep = '/home/sadc/share/project/calabria/data/spi_aggr'
for aggr in aggrs:
    spi_tiles = [f'{basep}/{tile}/spi_{aggr}m_2007-2024_bilinear_epsg3857.tif' for tile in tiles]
    # merge
    out_fp = f'{basep}/spi_{aggr}m_2007-2024_bilinear_epsg3857.tif'
    ras.merge_rasters(out_fp, np.nan, 'first', *spi_tiles)

#%%


