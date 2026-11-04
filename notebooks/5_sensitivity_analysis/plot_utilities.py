import os
import numpy as np
import netCDF4 as nc
#
import matplotlib.pyplot as plt


def _get_inundation_area(max_height_marray,thr_val,cell_area_m2=10):
    ### compute number of cells
    n_cells_thr = np.sum(max_height_marray >= thr_val)
    ### convert area to square meter
    area_km2 = (n_cells_thr * 10)/(10**6)
    return area_km2

def _get_maxheight_from_file(ds_path,path_exp):
    ### get full path to file
    ds_full_path = os.path.join(path_exp,ds_path)
    print(f"Load data from local file: {ds_full_path}")
    ### open file
    ds_file = nc.Dataset(ds_full_path)
    ### get max height from file
    maxh = ds_file.variables['max_height'][:]
    return maxh

def _get_maxheight_from_api(ds_path,path_tmp_download,sdl_client):
    #
    ds_label = ds_path.replace('/','__')
    ds_outoput_path = os.path.join(path_tmp_download,ds_label)
    print(f"Download File {ds_path} from SDL and save to {ds_outoput_path}")
    ### donwnload file locally
    sdl_client.file.download(experiment_id=207,version='1.0.0',file_path=ds_path,output_filename=ds_outoput_path)
    ### open file
    ds_values = nc.Dataset(ds_outoput_path)
    maxh = ds_values.variables['max_height'][:]
    #
    return maxh



def get_inundation_area_from_dataset(df_ds,path_exp,sdl_client=None):
    ### define list threshold
    list_thresholds = np.arange(0.01, 1, 0.01).round(2)
    ### select relevant data
    dict_ds_sim = df_ds[['ds_path','magnitude','manning_coeff','strike','dip','rake_bs_ps']].set_index('ds_path').to_dict(orient='index')
    ### compute inundation area for each file
    for ds_path in dict_ds_sim.keys():
        ### get max height from dataset
        if sdl_client is None:
            ds_max_height = _get_maxheight_from_file(ds_path=ds_path,path_exp=path_exp)
        else:
            ds_max_height = _get_maxheight_from_api(ds_path=ds_path,path_tmp_download=path_exp,sdl_client=sdl_client)
        ### compute inundation area for each threshold
        list_areas_km2 = [_get_inundation_area(ds_max_height,thr_val) for thr_val in list_thresholds]
        ### append data to dict
        dict_ds_sim[ds_path]["list_thresholds"] = list_thresholds
        dict_ds_sim[ds_path]["list_areas_km2"] = list_areas_km2
    #
    return dict_ds_sim


def show_comparison_plot(dict_data,variable_key='manning_coeff',variable_label="Manning Coefficient"):

    ### create figure
    fig, ax = plt.subplots(1,figsize=(8, 8))
    ax.grid(True)

    ### plot inundated area for different parameters
    for ds_path in dict_data.keys():
        ax.plot(dict_data[ds_path]["list_thresholds"],dict_data[ds_path]["list_areas_km2"],linestyle='-',label=dict_data[ds_path][variable_key])

    ### personalize plot
    ax.set_xlabel("Height (m)")  # Title for the x-axis
    ax.set_ylabel("Area (km^2)")
    ax.set_xlim(left=0)  # Set the x-axis to start from 0
    ax.set_ylim(bottom=0)
    ax.set_xticks([item for item in dict_data[ds_path]["list_thresholds"] if int(item*100)%5==0])

    #
    plot_title = f"Area in which Height(m) is exceeded"
    ax.set_title(plot_title)
    #
    ax.legend(title=variable_label)

    return fig