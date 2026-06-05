import json
import urllib.request
import ssl
from datetime import datetime, timedelta

print("🚀 [GitHub 雲端突圍] 正在直連證交所全球不擋端點 (每日收盤行情基本面)...")

# 自動計算最近一個有效交易日
d = datetime.now()
# 考慮到 GitHub 伺服器是 UTC 時間，我們稍微往前推一天確保一定有盤後資料
d = d - timedelta(days=1)
if d.weekday() == 5: d = d - timedelta(days=1) # 週六移到週五
elif d.weekday() == 6: d = d - timedelta(days=2) # 週日移到週五

date_str = d.strftime("%Y%m%d")
print(f"📅 正在嘗試下載真實交易日 {date_str} 的全市場財務排行...")

# 🎯 證交所全球開放不鎖海外 IP 的官方收盤及基本面大表（包含本益比、殖利率、股淨比）
url = f"https://www.twse.com.tw/rwd/zh/afterTrading/BWIBBU_d?date={date_str}&selectType=ALL&response=json"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

try:
    ssl_context = ssl._create_unverified_context()
    req = urllib.request.Request(url, headers=headers)
    
    with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
        raw_data = response.read().decode('utf-8')
        raw_json = json.loads(raw_data)
    
    # 檢查證交所是否有正確回傳數據
    if "data" not in raw_json:
        raise Exception(f"證交所當日 ({date_str}) 無資料，可能是假日或尚未開盤。")

    clean_data = []
    print(f"📦 連線成功！雲端正在清洗全市場 {len(raw_json['data'])} 檔個股之真實基本面財報...")
    
    for item in raw_json["data"]:
        # 證交所欄位：0:證券代號, 1:證券名稱, 2:殖利率, 3:股利年度, 4:本益比, 5:股價淨值比
        stock_id = str(item[0]).strip()
        stock_name = str(item[1]).strip()
        
        if len(stock_id) != 4 or not stock_name:
            continue
            
        try:
            # 讀取真實的本益比、殖利率、股淨比（排除"-"未評等雜訊）
            dividend_yield = float(item[2]) if item[2] != "-" else 0.0
            pe_ratio = float(item[4]) if item[4] != "-" else 0.0
            pb_ratio = float(item[5]) if item[5] != "-" else 0.0
            
            clean_data.append({
                "stock_id": stock_id,
                "stock_name": stock_name,
                "revenue": pe_ratio,       # 本益比 (暫代原表格數值)
                "mom": dividend_yield,    # 殖利率 % (暫代原 MoM 欄位)
                "yoy": pb_ratio           # 股價淨值比 (暫代原 YoY 欄位)
            })
        except Exception:
            continue

    # 💾 保存到雲端目錄
    with open("revenue_data.json", "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=4)
        
    print(f"✨ 【大功告成】成功生成全市場基本面財務排行檔案！共 {len(clean_data)} 檔個股。")

except Exception as e:
    print(f"❌ 雲端抓取失敗: {e}")
    raise e
