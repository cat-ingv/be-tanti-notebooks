import numpy as np
import xarray as xr
import os



def compute_flow_depth(sim_result,bathy_grid):
    # get max height
    max_height = sim_result['max_height']
    max_height = max_height.values
    # get deformation
    deformation = sim_result['deformation']
    deformation = deformation.values
    # get coordinates
    lat = sim_result['lat']
    lat = lat.values
    lon = sim_result['lon']
    lon = lon.values
    # get original bathymetry
    orig_bathy_array = np.asarray(bathy_grid.z)
    # compute deformed bathymetry
    def_bathy = np.subtract(orig_bathy_array, deformation)
    # mask height
    max_height[orig_bathy_array < 0] = np.nan
    # compute flow depth
    flow_depth = np.subtract(max_height, def_bathy)
    flow_depth_ds = xr.Dataset(data_vars=dict(z=(["lat", "lon"], flow_depth)),
                            coords=dict(lon=(["lon"], lon), lat=(["lat"], lat)))
    #
    return flow_depth_ds



def get_simulation_results_from_file(ds_path,path_exp):
    # get site code
    #site_code = ds_path.split('/')[-1].split('.')[0]
    # get full path to file
    ds_full_path = os.path.join(path_exp,ds_path)
    # open file
    #print(f"File Site: {site_code}")
    print(f"Load data from local file: {ds_full_path}")
    sim_values = xr.open_dataset(ds_full_path)
    #
    return sim_values