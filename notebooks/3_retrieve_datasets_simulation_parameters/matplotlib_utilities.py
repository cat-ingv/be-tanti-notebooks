import netCDF4 as nc
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np

def _get_maxheight(ds_path):
    print(f"Load data from dataset: {ds_path}")
    ds_values = nc.Dataset(ds_path)
    maxh = ds_values.variables['max_height'][:]
    lon = ds_values.variables['lon'][:].data
    lat = ds_values.variables['lat'][:].data
    return lat,lon,maxh


def show_maxheight_maps(df_ds,path_exp):
    ### get list of datasets for each simulation run
    dict_ds_sim = df_ds[['sr_id','ds_path']].groupby('sr_id')['ds_path'].apply(np.array).to_dict()
    dict_ds_sim
    n_sim = len(dict_ds_sim)
    ### define plot
    fig, axes = plt.subplots(n_sim,
            figsize=(10, 5),
            subplot_kw={'projection': ccrs.PlateCarree()}
        )
    if n_sim==1:
        axes = [axes]
    ### show results for each simulation run
    for ax,sim in zip(axes,dict_ds_sim.keys()):
        #
        #ax.coastlines(resolution='10m',linestyle='--', edgecolor='gray')
        #ax.add_feature(cfeature.BORDERS, linestyle=':')
        ax.add_feature(cfeature.LAND, facecolor='lightgray')
        ax.add_feature(cfeature.OCEAN, facecolor='lightblue')
        #ax.add_feature(cfeature.LAKES, edgecolor='black')
        #ax.add_feature(cfeature.RIVERS)
        ax.set_title(f"Max Height for Simulation {sim}")
        #
        list_ds_paths = dict_ds_sim[sim]
        list_ds_paths = path_exp + list_ds_paths
        #
        for ds_path in list_ds_paths:
            ### load netcdf file
            lat, lon, max_height = _get_maxheight(ds_path)
            ### plot data
            lon_grid, lat_grid = np.meshgrid(lon, lat)
            pcm = ax.pcolormesh(lon_grid, lat_grid, max_height, transform=ccrs.PlateCarree(), cmap='viridis')
        fig.colorbar(pcm, ax=ax, orientation='vertical', label='Max Height')

    return fig



def show_maxheight_map(list_ds_paths):
    #
    ### prepare map
    fig, ax = plt.subplots(
        figsize=(10, 5),
        subplot_kw={'projection': ccrs.PlateCarree()}
    )
    #ax.coastlines(resolution='10m',linestyle='--', edgecolor='gray')
    #ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.LAND, edgecolor='lightgray')
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue')
    #ax.add_feature(cfeature.LAKES, edgecolor='black')
    #ax.add_feature(cfeature.RIVERS)
    #
    ### plot data on the map
    for ds_path in list_ds_paths:
        ### load data
        lat, lon, max_height = _get_maxheight(ds_path)
        ### plot data
        lon_grid, lat_grid = np.meshgrid(lon, lat)
        pcm = ax.pcolormesh(lon_grid, lat_grid, max_height, transform=ccrs.PlateCarree(), cmap='viridis')
        fig.colorbar(pcm, ax=ax, orientation='vertical', label='Max Height')
    return fig