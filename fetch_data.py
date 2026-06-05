import json
import urllib.request
import ssl

print("🚀 [GitHub 雲端特攻] 正在透過全球開放通道下載台股真實營收統計大表...")

# 🎯 改接全球不封鎖雲端 IP 的開放式財務數據端點 (直接鏡像政府資訊觀測站的最新營收大表)
url = "https://raw.githubusercontent.com/FinMind/FinMindData/main/data/taiwan_stock_month_revenue_snapshot.json"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

try:
    ssl_context = ssl._create_unverified_context()
    req = urllib.request.Request(url, headers=headers)
    
    with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
        raw_data = response.read().decode('utf-8')
        raw_json = json.loads(raw_data)
    
    clean_data = []
    print(f"📦 連線成功！雲端正在清洗 {len(raw_json)} 檔上市櫃個股之真實當月營收財報...")
    
    for item in raw_json:
        # 對齊營收大表的中文欄位
        stock_id = str(item.get("公司代號", "")).strip()
        stock_name = str(item.get("公司名稱", "")).strip()
        
        if len(stock_id) != 4 or not stock_name:
            continue
            
        try:
            # 轉換為億元（原始單位為千元，除以 100,000）
            current_rev = float(item.get("當月營收", 0)) / 100000
            last_month_rev = float(item.get("上月營收", 0)) / 100000
            last_year_rev = float(item.get("去年當月營收", 0)) / 100000
            
            # 精算營收雙增率 (MoM 與 YoY)
            mom_calc = ((current_rev - last_month_rev) / last_month_rev * 100) if last_month_rev > 0 else 0.0
            yoy_calc = ((current_rev - last_year_rev) / last_year_rev * 100) if last_year_rev > 0 else 0.0
            
            if current_rev > 0:
                clean_data.append({
                    "stock_id": stock_id,
                    "stock_name": stock_name,
                    "revenue": round(current_rev, 2),  # 這就是你要的當月營收（億元）
                    "mom": round(mom_calc, 2),          # 營收月增率 %
                    "yoy": round(yoy_calc, 2)           # 營收年增率 %
                })
        except Exception:
            continue

    # 💾 保存到雲端目錄
    with open("revenue_data.json", "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=4)
        
    print(f"✨ 【大功告成】成功生成全市場最新真實營收大表！共 {len(clean_data)} 檔個股。")

except Exception as e:
    print(f"❌ 雲端抓取失敗: {e}")
    raise e
