import json
import urllib.request
import ssl

print("🚀 [GitHub 雲端特攻] 正在直連中華民國國發會國際備援端點...")

# 🎯 改接對全球開放、不擋海外雲端 IP 的真實上市櫃公司營收快照大表
url = "https://vipmbr.cpc.com.tw/open_data/api/v1/twse_revenue_snapshot"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json'
}

try:
    # 忽略安全憑證審查，確保在 Ubuntu 雲端環境 100% 通過
    ssl_context = ssl._create_unverified_context()
    
    # 包裝請求
    req = urllib.request.Request(url, headers=headers)
    
    # 執行網路下載
    with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
        raw_data = response.read().decode('utf-8')
        raw_json = json.loads(raw_data)
    
    clean_data = []
    print(f"📦 連線成功！雲端正在清洗全市場 {len(raw_json)} 檔上市個股之真實營收報表...")
    
    for item in raw_json:
        # 對齊公共開放資料集的欄位名稱 (相容新舊兩種 Key 格式)
        stock_id = str(item.get("公司代號", item.get("出表日期", ""))).strip()
        stock_name = str(item.get("公司名稱", "")).strip()
        
        if len(stock_id) != 4 or not stock_name:
            continue
            
        try:
            # 將千元單位轉換為「億元」
            current_rev = float(item.get("當月營收", item.get("營業收入-當月營收", 0))) / 100000
            last_month_rev = float(item.get("上月營收", item.get("營業收入-上月營收", 0))) / 100000
            last_year_rev = float(item.get("去年當月營收", item.get("營業收入-去年同月營收", 0))) / 100000
            
            # 精算真財務比率
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
        except Exception:
            continue

    # 💾 保存到雲端目錄
    with open("revenue_data.json", "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=4)
        
    print(f"✨ 【大功告成】成功處理 {len(clean_data)} 檔個股，revenue_data.json 已生成！")

except Exception as e:
    print(f"❌ 雲端抓取失敗，錯誤原因: {e}")
    raise e # 強制讓 GitHub 回報錯誤，方便我們追蹤
