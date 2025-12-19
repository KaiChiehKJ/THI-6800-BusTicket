import os 
import pandas as pd 
import re
import geopandas as gpd
from datetime import datetime, timedelta


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

def filter_by_keywords(df, filtercolumn, filterlist):
    """
    從指定欄位中，排除包含 filterlist 關鍵字的資料列

    Parameters
    ----------
    df : pandas.DataFrame
        原始資料
    filtercolumn : str
        要檢查關鍵字的欄位名稱
    filterlist : list[str]
        要排除的關鍵字清單

    Returns
    -------
    pandas.DataFrame
        過濾後的 DataFrame
    """
    pattern = '|'.join(map(str, filterlist))
    return df[~df[filtercolumn].str.contains(pattern, na=False)]

def updatelog(file, text):
    """將 text 追加寫入指定的 log 檔案，並加上當前時間"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 取得當前時間
    log_entry = f"[{timestamp}] {text}"  # 格式化日誌內容
    with open(file, 'a', encoding='utf-8') as f:
        f.write(log_entry + '\n')

def is_expired(line, cutoff_date):
    """判斷該行的時間戳記是否超過 `cutoff_date`"""
    try:
        timestamp_str = line[1:20]  # 擷取 `[YYYY-MM-DD HH:MM:SS]`
        log_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        return log_time < cutoff_date
    except ValueError:
        return False  # 解析錯誤則保留該行

def refreshlog(file, day=30):
    """僅檢查第一行的時間戳記，若超過 `day` 天才執行清理"""
    if not os.path.exists(file):
        return  # 檔案不存在，直接返回

    cutoff_date = datetime.now() - timedelta(days=day)  # 計算過期時間

    with open(file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if not lines:
        return  # 檔案為空，直接返回

    # 解析第一行的時間戳記
    first_line = lines[0]
    if first_line.startswith('['):  # 確保這行有時間戳記
        try:
            timestamp_str = first_line[1:20]  # 擷取 `[YYYY-MM-DD HH:MM:SS]`
            first_log_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            if first_log_time >= cutoff_date:
                return  # 如果第一行時間還在範圍內，直接跳出
        except ValueError:
            pass  # 解析失敗就忽略，繼續清理

    # 若第一行時間超過 `day` 天，則開始過濾所有行
    new_lines = [line for line in lines if not (line.startswith('[') and is_expired(line, cutoff_date))]

    # 重新寫入檔案
    with open(file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

def log_txt_to_dataframe(
    txt_path: str,
    log_re=re.compile(
        r'^\[(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]\s*'
        r'\[(?P<level>[^\]]+)\]:(?P<msg>.*)$'
    )) -> pd.DataFrame:

    rows = []

    with open(txt_path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.rstrip("\n")

            if not line.strip():
                continue

            m = log_re.match(line)
            if m:
                rows.append({
                    "line_no": line_no,
                    "timestamp": pd.to_datetime(m.group("ts")),
                    "level": m.group("level").lower(),
                    "message": m.group("msg").strip()
                })
            else:
                if rows:
                    rows[-1]["message"] += "\n" + line

    return pd.DataFrame(rows)

def updatelog_format(file, text, level = 'INFO'):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] [{level}] {text}"
    with open(file, 'a', encoding='utf-8') as f:
        f.write(log_entry + '\n')

def transfer_log_to_dataframe(logfilepath):
    """
    將 log 檔案轉換為 pandas DataFrame
    log 格式需為：
    [YYYY-MM-DD HH:MM:SS] [LEVEL] message
    """
    pattern = r'\[(.*?)\] \[(.*?)\] (.*)'
    rows = []

    with open(logfilepath, 'r', encoding='utf-8') as f:
        for line in f:
            match = re.match(pattern, line.strip())
            if match:
                timestamp, level, message = match.groups()
                rows.append({
                    'timestamp': pd.to_datetime(timestamp),
                    'level': level,
                    'message': message
                })

    df = pd.DataFrame(rows)
    return df

def get_df_log(logfile):
    import pandas as pd

    df = pd.read_csv(
        logfile,
        sep=r"\s*\|\s*",      # 用 | 當分隔符（前後空白忽略）
        engine="python",
        names=["timestamp", "level", "message"]
    )

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df
