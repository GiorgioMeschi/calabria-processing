#%%

import geopandas as gpd
import matplotlib.pyplot as plt
from geospatial_tools import FF_tools as ff
import json
import multiprocessing 


#%% plot all the single maps

def plot_susc(fires, total_ba, outfolder, tr1, tr2, year, month):

    path = f'/home/sadc/share/project/calabria/data/susceptibility/v4/susc_calabria_{year}_{month}.tif'
    outputlike = f'{outfolder}/susc_plot_{year}{month}.png'
    if not os.path.exists(outputlike):
        settings = dict(
            fires_file= fires,
            fires_col= 'date_iso',
            crs= 'epsg:3857',
            susc_path= path,
            xboxmin_hist= 0.2,
            yboxmin_hist= 0.1,
            xboxmin_pie= 0.2,
            yboxmin_pie= 0.7,
            threshold1= tr1,
            threshold2= tr2,
            out_folder= outfolder,
            year= year,
            month= month,
            season= False,
            total_ba_period= total_ba,
            susc_nodata= -1,
            pixel_to_ha_factor= 0.04,
            allow_hist= True,
            allow_pie= True,
            allow_fires= True,
            normalize_over_y_axis= 13,
            limit_barperc_to_show= 2,
        )

        fft.plot_susc_with_bars(**settings)
        plt.close('all')


if __name__ == '__main__':

    fft = ff.FireTools()
    fires_file = '/home/sadc/share/project/calabria/data/raw/burned_area/incendi_dpc_2007_2023_calabria_3857.shp'
    total_ba = gpd.read_file(fires_file).area.sum() / 10000
    tr_path = '/home/sadc/share/project/calabria/data/susceptibility/v4/thresholds/thresholds.json'
    thresholds = json.load(open(tr_path))
    tr1, tr2 = thresholds['lv1'], thresholds['lv2']

    with multiprocessing.Pool(processes=20) as pool:
        pool.starmap(
            plot_susc,
            [
                (
                    fires_file,
                    total_ba,
                    '/home/sadc/share/project/calabria/data/susceptibility/v4/PNG',
                    tr1,
                    tr2,
                    year,
                    month
                )
                for year in range(2007, 2024)
                for month in range(1, 13)
            ]
        )



#%%  merge pngs by year
import os
from geospatial_tools import geotools as gt

#images
Img = gt.Imtools()

basep = '/home/sadc/share/project/calabria/data/susceptibility/v4/PNG'
out_folder = '/home/sadc/share/project/calabria/data/susceptibility/v4/PNG/MERGED'
years = list(range(2007, 2024))
months = list(range(1, 13))

os.makedirs(out_folder, exist_ok=True)

for year in years:
    yearmonths = [f"{year}{month}" for month in months]
    year_filenames = [f'susc_plot_{m}' for m in yearmonths]
    year_files = [f"{basep}/{filename}.png" for filename in year_filenames]

    fig = Img.merge_images(year_files, ncol=4, nrow=3)
    fig.savefig(f"{out_folder}/susc_plot_{year}.png", dpi=500, bbox_inches='tight')



