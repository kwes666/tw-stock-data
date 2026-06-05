import json
import urllib.request
import ssl

print("🚀 雲端引擎啟動，正在直連台灣證交所下載真實營收大表...")
url = "https://openapi.twse.com.tw/v1/opendata/t187ap05_l"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

try:
    ssl_context = ssl._create_unverified_context()
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
        raw_json = json.loads(response.read().decode('utf-8'))
    
    clean_data = []
    for item in raw_json:
        stock_id = item.get("公司代號", "").strip()
        stock_name = item.get("公司名稱", "").strip()
        if len(stock_id) == 4 and stock_name:
            try:
                current_rev = float(item.get("當月營收", 0)) / 100000
                last_month_rev = float(item.get("上月營收", 0)) / 100000
                last_year_rev = float(item.get("去年當月營收", 0)) / 100000
                
                mom_calc = ((current_rev - last_month_rev) / last_month_rev * 100) if last_month_rev > 0 else 0.0
                yoy_calc = ((current_rev - last_year_rev) / last_year_rev * 100) if last_year_rev > 0 else 0.0
                
                if current_rev > 0:
                    clean_data.append({
                        "stock_id": stock_id,
                        "stock_name": stock_name,
                        "revenue": round(current_rev, 2),
                        "mom": round(mom_calc, 2),
                        "yoy": round(yoy_calc, 2)
                    })
            except: continue

    with open("revenue_data.json", "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=4)
    print("✨ 資料清洗完成，已成功生成 revenue_data.json！")
except Exception as e:
    print(f"❌ 抓取失敗: {e}")
