

#%%

import os
import numpy as np
from geospatial_tools import geotools as gt
import rasterio as rio
import geopandas as gpd 
import pandas as pd
import multiprocessing as mp
from rasterio.mask import mask as riomask

#%% create tif file of vegetation

#extract the codes used in ML

veg_file = '/home/sadc/share/project/calabria/data/raw/vegetation/carta natura.shp'
ml_codes_mapping_file = '/home/sadc/share/project/calabria/data/raw/vegetation/stats_v3.csv'
out_file = '/home/sadc/share/project/calabria/data/raw/vegetation/vegetation_ml.tif'
reference_file = '/home/sadc/share/project/calabria/data/raw/dem/dem_calabria_20m_3857.tif'


veg = gpd.read_file(veg_file)
ml_codes = pd.read_csv(ml_codes_mapping_file)
ml_mapping = dict(zip(ml_codes['class'].astype(str), ml_codes['veg_code_ML'].astype(int)))
# mapping
veg['veg_code_ML'] = veg['COD_ISPRA'].map(ml_mapping)
# crs
veg = veg.to_crs('EPSG:3857')
#rasterizing
Raster = gt.Raster()
veg_arr = Raster.rasterize_gdf_as(veg, reference_file, column = 'veg_code_ML', all_touched = False)
# all not burnable as no data
veg_arr[veg_arr == 0] = 1

# save
Raster.save_raster_as(veg_arr, out_file, reference_file, nodata = 1, dtype = np.int8())

#%% clip over tiles

tiles_file = '/home/sadc/share/project/calabria/data/aoi/grid_clean.geojsonl.json'
out_folder = f'/home/sadc/share/project/calabria/data/ML'

# clip veg per tile 
with rio.open(out_file) as veg:
    tiles = gpd.read_file(tiles_file, driver='GeoJSONseq')
    for i, tile in tiles.iterrows():
        print(f'Processing tile {tile["id_sorted"]}')
        # buffer tile of 5 km 
        tile['geometry'] = tile['geometry'].buffer(5000)
        # clip usin rasterio
        tile_geom = tile['geometry']
        _tile, transform = riomask(veg, [tile_geom], crop=True)
        # save clipped dem
        path = f'{out_folder}/tile_{tile["id_sorted"]}/veg'
        os.makedirs(path, exist_ok=True)
        veg_file = f'{path}/veg_20m_3857.tif'
        meta_updated = veg.meta.copy()
        meta_updated.update({
            'transform': transform,
            'height': _tile.shape[1],
            'width': _tile.shape[2],
            # compression
            'compress': 'lzw',
            'tiled': True,
        })
        with rio.open(veg_file, 'w', **meta_updated) as dst:
            dst.write(_tile)


#%% create a unique veg map of calabria with the fuel types already in the shapefile

import json

veg_file = '/home/sadc/share/project/calabria/data/raw/vegetation/carta natura.shp'
ml_codes_mapping_file = '/home/sadc/share/project/calabria/data/raw/vegetation/veg_to_ft_v2.json'
out_file = '/home/sadc/share/project/calabria/data/raw/vegetation/fuel_type.tif'
reference_file = '/home/sadc/share/project/calabria/data/raw/dem/dem_calabria_20m_3857.tif'


veg = gpd.read_file(veg_file)
mapping = json.load(open(ml_codes_mapping_file))
# mapping
veg['ft'] = veg['COD_ISPRA'].map(mapping)
# crs
veg = veg.to_crs('EPSG:3857')
#rasterizing
Raster = gt.Raster()
veg_arr = Raster.rasterize_gdf_as(veg, reference_file, column = 'ft', all_touched = False)
# all not burnable as no data
# veg_arr[veg_arr == 0] = 1

# save
Raster.save_raster_as(veg_arr, out_file, reference_file, nodata = 0, dtype = np.int8())












