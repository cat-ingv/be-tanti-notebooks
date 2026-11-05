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