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
            fires_col= 'finaldate', # 'date_iso',
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
            normalize_over_y_axis= 60,
            limit_barperc_to_show= 2,
        )

        fft.plot_susc_with_bars(**settings)
        plt.close('all')


if __name__ == '__main__':

    fft = ff.FireTools()
    # fires_file = '/home/sadc/share/project/calabria/data/raw/burned_area/incendi_dpc_2007_2023_calabria_3857.shp'
    fires_file = '/home/sadc/share/project/calabria/data/raw/burned_area/2024_effis/calabria_effis_2024.shp'
    total_ba = gpd.read_file(fires_file).area.sum() / 10000
    tr_path = '/home/sadc/share/project/calabria/data/susceptibility/v4/thresholds/thresholds.json'
    thresholds = json.load(open(tr_path))
    tr1, tr2 = thresholds['lv1'], thresholds['lv2']

    with multiprocessing.Pool(processes=8) as pool:
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
                for year in [2024] #range(2007, 2024)
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
years = [2024] # list(range(2008, 2024))
months = list(range(1, 13))

os.makedirs(out_folder, exist_ok=True)

yearmonths = [f"{year}{month}" for year in years for month in months]
year_filenames = [f'susc_plot_{yrm}' for yrm in yearmonths]
year_files = [f"{basep}/{filename}.png" for filename in year_filenames]

fig = Img.merge_images(year_files, ncol=12, nrow=6)
# fig.savefig(f"{out_folder}/susc_plot_{year}.png", dpi=500, bbox_inches='tight')
# save image (Image object)
fig.save(f"{out_folder}/susc_plot_2008-2023.png")


# for year in years:
#     yearmonths = [f"{year}{month}" for month in months]
#     year_filenames = [f'susc_plot_{m}' for m in yearmonths]
#     year_files = [f"{basep}/{filename}.png" for filename in year_filenames]

#     fig = Img.merge_images(year_files, ncol=4, nrow=3)
#     # fig.savefig(f"{out_folder}/susc_plot_{year}.png", dpi=500, bbox_inches='tight')
#     # save image (Image object)
#     fig.save(f"{out_folder}/susc_plot_{year}.png")
    



#%% merge the merged


# inp = '/home/sadc/share/project/calabria/data/susceptibility/v4/PNG/MERGED'
# filesname = os.listdir(inp)
# # exclude 2007
# filesname = [f for f in filesname if f.startswith('susc_plot_') and f != 'susc_plot_2007.png']
# files = [f for f in filesname if f.endswith('.png')] 

# merged_fig = Img.merge_images([f"{inp}/{f}" for f in files], ncol=4, nrow=4)
# merged_fig.save(f"{inp}/susc_plot_2008-2023.png")


#%%