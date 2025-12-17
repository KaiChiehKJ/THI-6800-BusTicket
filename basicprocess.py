import os 
import pandas as pd 
import geopandas as gpd


def create_folder(folder_name):
    """建立資料夾"""
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return os.path.abspath(folder_name)

def findfiles(filefolderpath, filetype='.csv', recursive=True):
    """
    尋找指定路徑下指定類型的檔案，並返回檔案路徑列表。

    Args:
        filefolderpath (str): 指定的檔案路徑。
        filetype (str, optional): 要尋找的檔案類型，預設為 '.csv'。
        recursive (bool, optional): 是否檢索所有子資料夾，預設為 True；反之為False，僅查找當前資料夾的所有file。

    Returns:
        list: 包含所有符合條件的檔案路徑的列表。
    """
    filelist = []

    if recursive:
        # 遍歷資料夾及其子資料夾
        for root, _, files in os.walk(filefolderpath):
            for file in files:
                if file.endswith(filetype):
                    file_path = os.path.join(root, file)
                    filelist.append(file_path)
    else:
        # 僅檢索當前資料夾
        for file in os.listdir(filefolderpath):
            file_path = os.path.join(filefolderpath, file)
            if os.path.isfile(file_path) and file.endswith(filetype):
                filelist.append(file_path)

    return filelist

def read_combined_dataframe(file_list, filepath = True):
    dataframes = []
    
    for file in file_list:
        try:
            if file.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.endswith('.shp'):
                df = gpd.read_file(file)
            elif file.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file)
            else:
                print(f"Unsupported file format: {file}")
                continue
            if filepath:
                df['FilePath'] = file  # 添加來源檔案路徑欄位
            dataframes.append(df)
        except Exception as e:
            print(f"Error reading {file}: {e}")

    # 合併所有 DataFrame
    combined_df = pd.concat(dataframes, ignore_index=True)
    return combined_df
