
#%%

from geospatial_tools import geotools as gt
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import pandas as pd

#%%

# raster = gt.Raster()
home = '/home/sadc/share/project/calabria/data'
ba_file = f'{home}/raw/burned_area/incendi_dpc_2007_2023_ita_260325.shp'
tiles_file = f'{home}/aoi/grid_clean.geojsonl.json'
working_crs = 'EPSG:3857' #pseudo mercator (metric) - same as input dem (dem.crs)
out_folder = f'{home}/ML'

# clip dem per tile 
tiles = gpd.read_file(tiles_file, driver='GeoJSONseq')
ba = gpd.read_file(ba_file)
ba = ba.to_crs(working_crs)

# eliminate if only year (4 digits) are present
ba = ba[ba['data'].str.len() != 4]
# convert string from %d/%m/%Y" in %Y-%m-%d'
ba['date_iso'] = pd.to_datetime(ba['data'], format='%d/%m/%Y', errors='coerce').dt.strftime('%Y-%m-%d')
# save
ba.to_file(ba_file)

for i, tile in tiles.iterrows():
    print(f'Processing tile {tile["id_sorted"]}')
    # buffer tile of 25 km in degree
    tile['geometry'] = tile['geometry'].buffer(5000)
    # clip with overlay
    # convert tile to df
    # tile_df = gpd.GeoDataFrame([tile], crs=working_crs)
    # ba_tile = gpd.overlay(ba, tile_df, how='intersection')
    #I can do clip instead of overlay
    ba_tile = gpd.clip(ba, tile['geometry'])
    #remove fires under 5 ha
    ba_tile['area'] = ba_tile.area / 10000
    ba_tile = ba_tile[ba_tile['area'] > 5]
    # save clipped raster   
    outpath = f'{out_folder}/tile_{tile["id_sorted"]}/fires'
    out_file = f'{outpath}/fires_2007_2023_epsg3857.shp'
    os.makedirs(outpath, exist_ok=True)
    ba_tile.to_file(out_file, driver='ESRI Shapefile')
    if i == 0 or i == 1 or i == 2:
        fig, ax = plt.subplots()
        ba_tile.plot(ax=ax, facecolor='none', edgecolor='black')
        # off axis and title
        ax.set_axis_off()
        ax.set_title(f'Tile {tile["id_sorted"]}')
    
    



# plot tile 1 fires:
