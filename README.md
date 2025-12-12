# 公車票證分析

## 專案說明
票證來源為[TICP(交通數據匯流平臺)](https://ticp.motc.gov.tw/)，其他公車相關靜態資料資料則源於[TDX(運輸資料流通平臺)](https://tdx.transportdata.tw/)，可使用個人的金鑰下載相關公車靜態資料，公車票證資料則需要行文進行購買，因此此專案的資料清洗流程僅供參考。  <br>
 <br>
為透過市區公車/公路客運的悠遊卡票證資料，找出通過各個交通屏柵線的通過量，作為後續交通分析應用於總體運輸模型輸入的大眾運輸交通量。並且此專案會包含檢視 Tableau視覺化儀表板的內容。 <br>
主要的程式碼如下列幾個，需要依序進行執行： <br>
1. 01_TDX資料下載.ipynb：用於下載公車動態網站的班表爬蟲，可自行利用此程式碼的函數下載TDX提供的API(此預設為寫入xml檔案)。
2. 02_公車路線shp拆分.ipynb：包含讀取01所下載的公車站序及公車路線資料，並且利用站序黏貼公車站點至路線上，再以這些站點進行切分公車路線。(可用於計算每個站與站之間的行駛長度)
3. 03_TicketAnalysisCode.ipynb：比對營運資料、電子票證刷卡資料進行計算，並且利用批次處理刷卡大數據。過程包含票證清理、確認行經站點、比對站序、與營運票證比對，最後再將資料匯出為每日站間量、OD起訖熱區"

## 安裝步驟
因本專案的資料涉及個資無法提供，但欲使用相關的路線資料，可以至TDX官網進行下載路線資料，以及函文請示相關資料。 <br>
需要確保目錄架構為： <br>
project_name <br>
├── code/ # 此專案的資料夾 <br> 
│   ├── requirements.txt # 用於安裝依賴包的列表 <br>
│   ├── 01_TDX資料下載.ipynb <br>
│   ├── 02_公車路線shp拆分.ipynb <br>
│   └── 03_TicketAnalysisCode.ipynb  <br>
├── 參考資料/ <br>
│   └── Date.xlsx # 提供非技術人員挑選塞選的票證時間區間 <br>
├── 00_TDX資料下載/ <br>
├── 01_初步整理票證/ # 因資料量過大需要批次輸出，可改為自行串接資料庫加速處理 <br>
├── 02_初步分析/ <br>
├── 03_處理後資料/ # tableau的資料都會在這個資料夾之內，不會直接取用原始資料(未進行資料清理) <br>
├── Tableau/ # tableau儀表版納入版控 <br>
└── README.md              # 項目的說明文件 <br>

## 貢獻者指引
* email:timothychang.kj@gmail.com
* [https://linkedin.com/in/timothychang.kj](https://www.linkedin.com/in/timothy-chang-kj/)

## 授權信息
MIT License

Copyright (c) 2025 TimothyChang

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

NOTE: Data related to this project is not included and is not provided for public use. Please refer to the respective data sources for more information.
