import os
from pathlib import Path


def download_sdl_file(download_dir,file_sdl_path,sdl_client):
    #print(f"...Download file: {file_sdl_path}")
    # 
    file_local_path = os.path.join(download_dir,file_sdl_path)
    # create a directory if not exist
    file_dir = Path(file_local_path).parent
    file_dir.mkdir(parents=True, exist_ok=True)
    # download file only if not done before
    if os.path.exists(file_local_path):
        print(f"......File: {file_local_path} already exists")
    else:
        sdl_client.file.download(experiment_id=207,version='1.0.0',file_path=file_sdl_path,output_filename=file_local_path)



def check_download(df_paths, download_dir, cols=['c_nc', 'grid0_ts']):
    list_all_files = df_paths['c_nc'].tolist() + df_paths['grid0_ts'].tolist()
    list_missing_files = [f for f in list_all_files if not os.path.exists(os.path.join(download_dir, f))]
    if len(list_missing_files)==0:
        check = "Donwload completed: all files have been successufully downloaded"
    else:
        check = f"Donwload completed: {len(list_missing_files)} files are missing. Restart the download."
    return check