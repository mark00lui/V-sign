# 輔助工具腳本

此目錄包含用於管理股票研究資料的輔助工具。

## generate_summary.py

自動生成股票研究對比摘要的腳本。

### 功能

- 掃描指定股票的所有研究報告
- 解析報告內容，提取關鍵資訊：
  - 價格預測（目標價格、當前價格、預測方向）
  - 關鍵觀點（從執行摘要提取）
  - 風險評估（風險等級）
- 生成對比摘要，包含：
  - 價格預測變化表
  - 關鍵觀點演變
  - 風險評估變化
  - 趨勢分析

### 使用方法

```bash
python scripts/generate_summary.py [股票代碼]
```

**範例**：
```bash
# 生成台積電（2330）的對比摘要
python scripts/generate_summary.py 2330

# 生成蘋果（AAPL）的對比摘要
python scripts/generate_summary.py AAPL
```

### 輸出

腳本會在 `stocks/[股票代碼]/summary.md` 生成對比摘要文件。

### 依賴

- Python 3.6 或更高版本
- 無需額外套件（僅使用 Python 標準庫）

### 注意事項

- 腳本會自動解析報告中的章節結構
- 確保研究報告遵循標準格式（參考 `stocks/TEMPLATE_REPORT.md`）
- 如果報告格式不標準，某些資訊可能無法正確提取

