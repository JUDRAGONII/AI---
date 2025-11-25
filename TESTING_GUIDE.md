# 系統測試指南

完整的測試流程與驗證清單

## 🧪 測試層級

### 1. 單元測試（Unit Tests）

#### 後端 Python 模組測試

```bash
# 安裝測試依賴
pip install pytest pytest-cov

# 執行所有測試
pytest tests/ -v

# 生成覆蓋率報告
pytest tests/ --cov=. --cov-report=html
```

**測試範例**：

```python
# tests/test_factor_engine.py
import pytest
from calculators import FactorEngine

def test_factor_engine_initialization():
    engine = FactorEngine()
    assert engine is not None

def test_calculate_value_factor():
    engine = FactorEngine()
    score = engine.calculate_all_factors('2330', 580.0, 'tw', save_to_db=False)
    assert 'value_score' in score
    assert 0 <= score['value_score'] <= 100

def test_calculate_total_score():
    engine = FactorEngine()
    score = engine.calculate_all_factors('2330', 580.0, 'tw', save_to_db=False)
    assert 'total_score' in score
    assert score['total_score'] > 0
```

#### 前端元件測試

```bash
cd frontend

# 安裝測試依賴
npm install --save-dev @testing-library/react @testing-library/jest-dom vitest

# 執行測試
npm run test
```

### 2. 整合測試（Integration Tests）

#### API 端點測試

```python
# tests/test_api.py
import requests

BASE_URL = 'http://localhost:5000'

def test_健康檢查():
    response = requests.get(f'{BASE_URL}/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'healthy'

def test_獲取因子分數():
    response = requests.get(f'{BASE_URL}/api/factors/2330?market=tw')
    assert response.status_code == 200
    data = response.json()
    assert 'scores' in data
    assert 'stock_code' in data

def test_搜尋股票():
    response = requests.get(f'{BASE_URL}/api/stocks/search?q=台積')
    assert response.status_code == 200
    results = response.json()
    assert results['count'] > 0
```

#### 資料庫連接測試

```python
# tests/test_database.py
from data_loader.database_connector import DatabaseConnector

def test_database_connection():
    db = DatabaseConnector()
    assert db is not None

def test_query_execution():
    db = DatabaseConnector()
    result = db.execute_query("SELECT 1 as test")
    assert result[0]['test'] == 1

def test_stock_data_query():
    db = DatabaseConnector()
    result = db.execute_query("""
        SELECT stock_code FROM tw_stock_info LIMIT 1
    """)
    assert len(result) > 0
```

### 3. 端到端測試（E2E Tests）

#### 完整流程測試

**測試腳本**：`tests/e2e_test.py`

```python
import requests
import time

def test_complete_workflow():
    """測試完整的數據流程"""
    
    # 1. 檢查API服務
    health = requests.get('http://localhost:5000/health')
    assert health.status_code == 200
    print("✅ API 服務正常")
    
    # 2. 獲取股票清單
    stocks = requests.get('http://localhost:5000/api/stocks/list?market=tw')
    assert stocks.status_code == 200
    print(f"✅ 獲取到 {stocks.json()['count']} 筆股票資料")
    
    # 3. 計算因子分數
    factors = requests.get('http://localhost:5000/api/factors/2330?market=tw')
    assert factors.status_code == 200
    print(f"✅ 台積電因子總分: {factors.json()['scores']['total_score']}")
    
    # 4. 生成AI報告
    report = requests.post('http://localhost:5000/api/ai/daily-report')
    assert report.status_code == 200
    print("✅ AI 報告生成成功")
    
    # 5. 獲取TDCC數據
    tdcc = requests.get('http://localhost:5000/api/tdcc/2330/latest')
    if tdcc.status_code == 200:
        print("✅ TDCC 數據獲取成功")
    
    print("\n🎉 完整流程測試通過！")

if __name__ == '__main__':
    test_complete_workflow()
```

## 📊 功能測試清單

### 資料層測試

- [ ] 資料庫連接正常
- [ ] 所有表格存在
- [ ] 台股價格資料可查詢
- [ ] 美股價格資料可查詢
- [ ] TDCC 籌碼資料可查詢
- [ ] 財務資料可查詢

### 計算層測試

- [ ] 價值因子計算正確
- [ ] 品質因子計算正確
- [ ] 動能因子計算正確
- [ ] 規模因子計算正確
- [ ] 波動率因子計算正確
- [ ] 成長因子計算正確
- [ ] 技術指標計算正確（MA, RSI, MACD等）

### AI 層測試

- [ ] Gemini API 連接正常
- [ ] 每日報告生成成功
- [ ] 決策模板生成成功
- [ ] Markdown 格式正確

### API 層測試

- [ ] 所有15個端點運作正常
- [ ] 錯誤處理正確
- [ ] 返回格式正確
- [ ] CORS 設定正常

### 前端測試

- [ ] 所有15個頁面可訪問
- [ ] 圖表正常顯示
- [ ] Dark Mode 切換正常
- [ ] 響應式布局正常
- [ ] 表單提交正常
- [ ] 數據載入正常

## 🎯 效能測試

### 負載測試

```python
# tests/load_test.py
import concurrent.futures
import requests
import time

def make_request(url):
    start = time.time()
    response = requests.get(url)
    duration = time.time() - start
    return duration, response.status_code

def load_test(url, num_requests=100):
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request, url) for _ in range(num_requests)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    durations = [r[0] for r in results]
    avg_time = sum(durations) / len(durations)
    success_rate = sum(1 for r in results if r[1] == 200) / len(results) * 100
    
    print(f"平均響應時間: {avg_time:.3f}秒")
    print(f"成功率: {success_rate:.1f}%")

if __name__ == '__main__':
    print("負載測試：API 健康檢查端點")
    load_test('http://localhost:5000/health', 100)
```

### 資料庫查詢效能

```sql
-- 檢查慢查詢
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE mean_exec_time > 1000  -- 超過1秒的查詢
ORDER BY mean_exec_time DESC
LIMIT 10;
```

## 🔒 安全測試

### API 安全性檢查

```python
# tests/security_test.py
import requests

def test_sql_injection():
    """SQL 注入測試"""
    response = requests.get('http://localhost:5000/api/factors/2330\'; DROP TABLE--')
    # 應該返回錯誤而非執行
    assert response.status_code in [400, 404, 500]

def test_xss_protection():
    """XSS 攻擊測試"""
    response = requests.get('http://localhost:5000/api/stocks/search?q=<script>alert(1)</script>')
    # 應該進行轉義
    assert '<script>' not in response.text
```

## 📝 測試報告範本

```markdown
# 測試報告

**測試日期**: 2024-11-23  
**測試環境**: 開發環境  
**測試人員**: 系統自動化測試

## 測試摘要

| 測試類型 | 總數 | 通過 | 失敗 | 通過率 |
|---------|------|------|------|--------|
| 單元測試 | 50 | 48 | 2 | 96% |
| 整合測試 | 30 | 30 | 0 | 100% |
| E2E 測試 | 10 | 10 | 0 | 100% |

## 失敗測試

1. test_macro_data_availability - 宏觀經濟數據缺失
2. test_news_api_integration - 新聞 API 限流

## 建議

1. 補充宏觀經濟數據回溯
2. 增加 API Key 避免限流
```

## 🚀 執行測試

### 快速測試

```bash
# 基本功能測試
python tests/quick_test.py

# API 測試
python tests/api_test.py

# 端到端測試
python tests/e2e_test.py
```

### 完整測試套件

```bash
# 執行所有測試
./run_all_tests.sh

# 或使用 pytest
pytest tests/ -v --cov --html=report.html
```

## 📊 持續整合（CI）

### GitHub Actions 配置

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/ -v --cov
```

---

**版本**: 1.0.0  
**最後更新**: 2024-11-23
