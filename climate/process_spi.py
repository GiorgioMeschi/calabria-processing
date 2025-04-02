

#%% imports

import os
import numpy as np
from geospatial_tools import geotools as gt
import rasterio as rio
from rasterio.merge import merge
import geopandas as gpd 
from rasterio.mask import mask as riomask
import multiprocessing as mp
import time

#%% inputs

DATAPATH = '/home/sadc/share/project/calabria/data/raw/spi'
TILES_DIR = '/home/sadc/share/project/calabria/data/ML'
CORES = 30

months_aggregation = [1, 3, 6, 12]
years = list(range(2006, 2025))
months = list(range(1, 13))
clim_tile_num = 4 # include italy
# tiles to clip the data on 
tiles = os.listdir(TILES_DIR)

Raster = gt.Raster()

# I see that tile 4 cover Italy    

#%% clip the raw spi and save it in the proper month folder


def clip_to_tiles(aggr, year, month, tile: str, tile_df: gpd.GeoDataFrame):

    base_folderpath = os.path.join(DATAPATH, str(aggr), str(year), f'{month:02}')
    day_of_interest = os.listdir(base_folderpath)[-1]
    folderpath = os.path.join(base_folderpath, day_of_interest)
    tile_file = os.path.join(folderpath, f'CHIRPS2-SPI{aggr}_{year}{month:02}{day_of_interest}_tile4.tif')
    out_folder = os.path.join(TILES_DIR, tile, 'climate', f'{year}_{month}')
    os.makedirs(out_folder, exist_ok=True)
    wgs_file = os.path.join(out_folder, f'spi_{aggr}m_wgs.tif')
    reproj_out_file = os.path.join(out_folder, f'spi_{aggr}m_bilinear_epsg3857.tif') # out filename

    if not os.path.exists(reproj_out_file):
    # if reproj_out_file == '/home/sadc/share/project/calabria/data/ML/tile_2/climate/2012_6/spi_1m_bilinear_epsg3857.tif':


        # clip and reproject
        tile_geom = tile_df[tile_df['id_sorted'] == int(tile[5:])].geometry.values[0]
        # buffer 5 km in degrees
        tile_geom = tile_geom.buffer(0.05)
        
        with rio.open(tile_file) as src:
            out_image, out_transform = riomask(src, [tile_geom], crop = True)
            out_meta = src.meta.copy()
            out_meta.update({
                'height': out_image.shape[1],
                'width': out_image.shape[2],
                'transform': out_transform
            })
            with rio.open(wgs_file, 'w', **out_meta) as dst:
                dst.write(out_image)
        
        # reference_file_wgs = os.path.join(TILES_DIR, tile, 'dem', 'dem_wgs.tif')
        reference_file = os.path.join(TILES_DIR, tile, 'dem', 'dem_20m_3857.tif')
        with rio.open(reference_file) as ref:
            bounds = ref.bounds  # Extract bounds (left, bottom, right, top)
            xres = ref.transform[0]  # Pixel width
            yres = ref.transform[4]  # Pixel height
            working_crs = 'EPSG:3857'  # Target CRS

        # Use gdalwarp to reproject and match the bounds and resolution of the reference file
        interpolation = 'bilinear'  # Interpolation method
        os.system(
            f'gdalwarp -t_srs {working_crs} -te {bounds.left} {bounds.bottom} {bounds.right} {bounds.top} '
            f'-tr {xres} {yres} -r {interpolation} -of GTiff '
            f'-co COMPRESS=LZW -co TILED=YES -co BLOCKXSIZE=256 -co BLOCKYSIZE=256 '
            f'{wgs_file} {reproj_out_file}'
        )

        time.sleep(2)
        os.remove(wgs_file)

    else:
        print(f'File {reproj_out_file} already exists')

with mp.Pool(CORES) as p:
    # open the tiles already in WGS 84
    tile_df = gpd.read_file('/home/sadc/share/project/calabria/data/aoi/grid_clean.geojsonl.json', driver='GeoJSONSeq')
    tile_df = tile_df.to_crs('EPSG:4326') #proj of the input SPI
    # use all the cores to clip the data
    p.starmap(clip_to_tiles, [(aggr, year, month, tile, tile_df) for aggr in months_aggregation
                                                                for year in years
                                                                for month in months
                                                                for tile in tiles
                                                               ])


#%% check file existance

# for aggr in months_aggregation:
#     for year in years:
#         for month in months:
#             for tile in tiles:
#                 base_folderpath = os.path.join(DATAPATH, str(aggr), str(year), f'{month:02}')
#                 day_of_interest = os.listdir(base_folderpath)[-1]
#                 out_folder = os.path.join(TILES_DIR, tile, 'climate', f'{year}_{month}')
#                 reproj_out_file = os.path.join(out_folder, f'spi_{aggr}m_epsg3857.tif')
#                 if not os.path.exists(reproj_out_file):
#                     print(f'File {reproj_out_file} does not exist')


