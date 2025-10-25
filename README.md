## 抽卡策略分析器 (Gacha Strategy Simulator)
這是一個使用 **Python + Streamlit** 製作的抽卡模擬工具，  
用於分析活動前後的抽卡成本變化與機率差異，  
幫助設計者或玩家理解不同抽卡策略的影響。

---

## 功能簡介
- 模擬多次活動抽卡的平均成本  
- 顯示抽卡成本分布與信賴區間  
- 匯出分析結果為 PDF / Excel 報告  

---

## 使用技術

| 技術 | 用途 |
|------|------|
| **Streamlit** | 建立互動式網頁介面 |
| **Pandas / Numpy** | 資料處理與統計分析 |
| **Matplotlib / Seaborn** | 視覺化抽卡成本分布 |
| **ReportLab** | 產生 PDF 分析報告 |
| **OpenPyXL** | 匯出 Excel 結果表格 |

---

## 執行方式

### 第一步：安裝套件  
```bash
pip install -r requirements.txt
```

### 第二步 : 執行程式
```bash
streamlit run card_drawing.py
```
