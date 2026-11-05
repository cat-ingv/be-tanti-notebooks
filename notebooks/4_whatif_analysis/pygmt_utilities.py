import numpy as np
import xarray as xr
import os
import pygmt





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

def _get_simulation_results_from_file(ds_path,path_exp):
    # get site code
    site_code = ds_path.split('/')[-1].split('.')[0]
    # get full path to file
    ds_full_path = os.path.join(path_exp,ds_path)
    # open file
    print(f"File Site: {site_code}")
    print(f"Load data from local file: {ds_full_path}")
    sim_values = xr.open_dataset(ds_full_path)
    #
    return site_code, sim_values

def _get_simulation_results_from_api(ds_path,path_tmp_download,sdl_client):
    # get site code
    site_code = ds_path.split('/')[-1].split('.')[0]
    print(f"File Site: {site_code}")
    #
    ds_label = ds_path.replace('/','__')
    ds_outoput_path = os.path.join(path_tmp_download,ds_label)
    print(f"Download File {ds_path} from SDL and save to {ds_outoput_path}")
    ### donwnload file locally
    sdl_client.file.download(experiment_id=207,version='1.0.0',file_path=ds_path,output_filename=ds_outoput_path)
    ### open file
    sim_values = xr.open_dataset(ds_outoput_path)
    #
    return site_code, sim_values

def _get_bathymetry_grids_OLD(list_bathy_files,path_exp,sdl_client=None):
    #
    path_bathymetry_files = {path_file.split('/')[-1].split('.')[0]:path_file for path_file in list_bathy_files}
    #
    bathy_grid_sites = {}
    for key in path_bathymetry_files.keys():
        bati_path = path_bathymetry_files[key]
        if(sdl_client is None):
            site_code, bathy_grid = _get_simulation_results_from_file(bati_path,path_exp=path_exp)
        else:
            site_code, bathy_grid = _get_simulation_results_from_api(bati_path,path_tmp_download=path_exp,sdl_client=sdl_client)
        bathy_grid_sites[site_code] = bathy_grid
    #
    return bathy_grid_sites

def _get_bathymetry_grids(df_bathy_files,path_exp,sdl_client=None):
    #
    path_bathymetry_files = df_bathy_files.set_index('site')['path_bathy_file'].to_dict()
    #
    bathy_grid_sites = {}
    for key in path_bathymetry_files.keys():
        bati_path = path_bathymetry_files[key]
        if(sdl_client is None):
            site_code, bathy_grid = _get_simulation_results_from_file(bati_path,path_exp=path_exp)
        else:
            site_code, bathy_grid = _get_simulation_results_from_api(bati_path,path_tmp_download=path_exp,sdl_client=sdl_client)
        bathy_grid_sites[site_code] = bathy_grid
    #
    return bathy_grid_sites

def _extract_data_from_files(df_ds,bathy_grid_sites,path_exp,_min_value=10,_max_value=0,sdl_client=None):
    ### select relevant data
    dict_ds_sim = df_ds[['sr_id','ds_path']].groupby('sr_id')['ds_path'].apply(np.array).to_dict()
    ### prepare output
    max_value = _max_value
    min_value = _min_value
    data_dict = {'simulations': {},
                 'n_sims': len(dict_ds_sim.keys())}
    ### read files for each simulation
    for sim in dict_ds_sim.keys():
        ### get list of files of the simulation & and append full path
        list_ds_paths = dict_ds_sim[sim]
        ### read single file
        data_dict['simulations'][sim] = []
        for ds_path in list_ds_paths:
            if(sdl_client is None):
                ### extract lat, lon, max_height from local file 
                site_code, sim_results = _get_simulation_results_from_file(ds_path,path_exp=path_exp)
            else:
                ### extract lat, lon, max_height from local file 
                site_code, sim_results = _get_simulation_results_from_api(ds_path,path_tmp_download=path_exp,sdl_client=sdl_client)
            # compute flow depth
            bathy_grid = bathy_grid_sites[site_code]
            ds_flow_depth = compute_flow_depth(sim_results,bathy_grid)
            max_flow_depth = ds_flow_depth['z'].max().item()
            min_flow_depth = ds_flow_depth['z'].min().item()
            ### create dict file
            ds_dict_sim = {'full_path': ds_path,
                            'flow_depth': ds_flow_depth,
                            'bathy_grid': bathy_grid,
                            'site': site_code,
                            'max_flow_depth': max_flow_depth,
                            'min_flow_depth': min_flow_depth}
            ### append dict to sim
            data_dict['simulations'][sim].append(ds_dict_sim)
            ### compute max/min from all files
            max_value = max(max_value,max_flow_depth)
            min_value = min(min_value,min_flow_depth)
            #break
        #break
    ### set general info
    data_dict['max_flow_depth_global'] = max_value
    data_dict['min_flow_depth_global'] = min_value
    data_dict['n_sites'] = len(list_ds_paths)
    data_dict['n_sims'] = len(dict_ds_sim.keys())
    #
    return data_dict

def show_map_height(df_ds,bathy_grid_sites,path_exp,_min_value=10,_max_value=0,sdl_client=None,cptfile_bathy = './bathy_error.cpt'):
    ###
    min_depth = 0.1
    ### parse data
    data_dict = _extract_data_from_files(df_ds=df_ds,bathy_grid_sites=bathy_grid_sites,path_exp=path_exp,_min_value=_min_value,_max_value=_max_value,sdl_client=sdl_client)
    ### define plot
    n_sim = data_dict['n_sims']
    n_site = data_dict['n_sites']
    fig = pygmt.Figure()
    pygmt.config(MAP_TITLE_OFFSET='5p',FONT_TITLE='22p,Helvetica-Bold,black')
    pygmt.makecpt(cmap='split',series=[data_dict['min_flow_depth_global'], data_dict['max_flow_depth_global'], 0.5],output='flow_depth.cpt')
    ### create subplots
    with fig.subplot(nrows=n_sim, ncols=n_site, subsize=('30c', '30c'), margins=['1c', '2.5c'], autolabel=False):
        i_sim = 0
        for sim in data_dict['simulations'].keys():   
            for i_site in range(n_site):
                bathy_grid = data_dict['simulations'][sim][i_site]['bathy_grid']
                flow_depth = data_dict['simulations'][sim][i_site]['flow_depth']
                site_code = data_dict['simulations'][sim][i_site]['site'].split('_')[-1]
                with fig.set_panel(panel=[i_sim, i_site]):
                    pygmt.makecpt(cmap=cptfile_bathy, continuous=False)
                    # countour of bathymetry
                    xmin, xmax = bathy_grid['x'].min().values, bathy_grid['x'].max().values
                    ymin, ymax = bathy_grid['y'].min().values, bathy_grid['y'].max().values
                    # flow depth
                    depth = flow_depth['z']
                    grid_depth = depth.where(depth > min_depth).rename({'lon': 'x', 'lat': 'y'})
                    print(f'max depth {float(grid_depth.max()):.2f} m')
                    # plot
                    fig.grdimage(bathy_grid['z'], cmap=True, shading=True, region=[xmin, xmax, ymin, ymax], projection='M',frame=['ag', 'x+lLongitude', 'y+lLatitude',f'+tSite: {site_code}'])
                    fig.grdcontour(bathy_grid['z'], levels=10, pen='0.5p,white', limit=[-100, 0], projection='M')
                    fig.grdimage(grid_depth, cmap='flow_depth.cpt', projection='M', nan_transparent=True, transparency=50)
                    if i_site == 0:
                        if n_site > 1:
                            fig.text(
                                #x=(xmin + xmax) / 2,
                                #y=ymax,
                                position='TC',
                                text=f'Results from Simulation Run: {sim}',
                                font='36p,Helvetica-Bold,black',
                                justify='CB',  
                                offset='18c/2c',  
                                no_clip=True,
                            )
                        else:
                            fig.text(
                                #x=(xmin + xmax) / 2,
                                #y=ymax,
                                position='TC',
                                text=f'Results from Simulation Run: {sim}',
                                font='36p,Helvetica-Bold,black',
                                justify='CB',  
                                offset='0.5c/2c',  # Sposta il testo in alto di 0.8 cm sopra il bordo
                                no_clip=True,
                            )
            i_sim = i_sim + 1
    fig.colorbar(cmap='flow_depth.cpt',frame=['a2f1', 'x+lFlow Depth (m)'],position='JBC+w20c/0.5c+h+o0/1.5c')
    #
    return fig


def show_map_height_paper(df_ds,bathy_grid_sites,path_exp,_min_value=10,_max_value=0,sdl_client=None,cptfile_bathy = './bathy_error.cpt'):
    ###
    min_depth = 0.1
    ### parse data
    data_dict = _extract_data_from_files(df_ds=df_ds,bathy_grid_sites=bathy_grid_sites,path_exp=path_exp,_min_value=_min_value,_max_value=_max_value,sdl_client=sdl_client)
    ### define plot
    n_sim = data_dict['n_sims']
    n_site = data_dict['n_sites']
    fig = pygmt.Figure()
    pygmt.config(MAP_TITLE_OFFSET='5p',FONT_TITLE='22p,Helvetica-Bold,black')
    pygmt.makecpt(cmap='split',series=[data_dict['min_flow_depth_global'], data_dict['max_flow_depth_global'], 0.5],output='flow_depth.cpt')
    ### create subplots
    with fig.subplot(nrows=n_site, ncols=n_sim, subsize=('20c', '20c'), margins=['1c', '2.5c'], autolabel=False):
        for i_site in range(n_site):
            i_sim = 0
            for sim in data_dict['simulations'].keys():
                bathy_grid = data_dict['simulations'][sim][i_site]['bathy_grid']
                flow_depth = data_dict['simulations'][sim][i_site]['flow_depth']
                site_code = data_dict['simulations'][sim][i_site]['site'].split('_')[-1]
                with fig.set_panel(panel=[i_site,i_sim]):
                    pygmt.makecpt(cmap=cptfile_bathy, continuous=False)
                    # countour of bathymetry
                    xmin, xmax = bathy_grid['x'].min().values, bathy_grid['x'].max().values
                    ymin, ymax = bathy_grid['y'].min().values, bathy_grid['y'].max().values
                    # flow depth
                    depth = flow_depth['z']
                    grid_depth = depth.where(depth > min_depth).rename({'lon': 'x', 'lat': 'y'})
                    print(f'max depth {float(grid_depth.max()):.2f} m')
                    # plot
                    fig.grdimage(bathy_grid['z'], cmap=True, shading=True, region=[xmin, xmax, ymin, ymax], projection='M',frame=['ag', 'x+lLongitude', 'y+lLatitude',f'+tSite: {site_code}'])
                    fig.grdcontour(bathy_grid['z'], levels=10, pen='0.5p,white', limit=[-100, 0], projection='M')
                    fig.grdimage(grid_depth, cmap='flow_depth.cpt', projection='M', nan_transparent=True, transparency=50)
                    if i_site == 0:
                        if n_site > 1:
                            fig.text(
                                #x=(xmin + xmax) / 2,
                                #y=ymax,
                                position='TC',
                                text=f'Simulation Run: {sim}',
                                font='36p,Helvetica-Bold,black',
                                justify='CB',  
                                offset='18c/2c',  
                                no_clip=True,
                            )
                        else:
                            fig.text(
                                #x=(xmin + xmax) / 2,
                                #y=ymax,
                                position='TC',
                                text=f'Simulation Run: {sim}',
                                font='36p,Helvetica-Bold,black',
                                justify='CB',  
                                offset='0.5c/2c',  # Sposta il testo in alto di 0.8 cm sopra il bordo
                                no_clip=True,
                            )
                i_sim = i_sim + 1
    fig.colorbar(cmap='flow_depth.cpt',frame=['a2f1', 'x+lFlow Depth (m)'],position='JBC+w20c/0.5c+h+o0/1.5c')
    #
    return fig
