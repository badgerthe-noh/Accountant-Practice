import requests

# 1. User-Agent 헤더 설정 (본인 이름과 이메일로 교체)
HEADERS = {"User-Agent": "Tommy Noh hnoh27@wisc.edu"}

# 2. 티커 -> CIK 변환용 대응표 받아오기
tickers = requests.get(
    "https://www.sec.gov/files/company_tickers.json", headers=HEADERS
).json()

cik_lookup = {row["ticker"]: str(row["cik_str"]).zfill(10) for row in tickers.values()}

# 3. 조회하고 싶은 회사의 티커로 CIK 찾기 (예: 애플)
ticker = "AAPL"
cik = cik_lookup[ticker]
print(f"{ticker}의 CIK: {cik}")

# 4. companyfacts 엔드포인트로 재무 데이터 조회
url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
response = requests.get(url, headers=HEADERS)
companyfacts = response.json()


# 5. 잘 받아졌는지 확인 - 사용 가능한 회계 항목 이름들 출력
us_gaap_items = companyfacts["facts"]["us-gaap"]
print(f"총 {len(us_gaap_items)}개 항목 존재")
print(list(us_gaap_items.keys())[:10])  # 앞에서 10개만 미리보기

#================================================================================================
import pandas as pd

def get_annual_revenue(us_gaap_items, key):
    if key not in us_gaap_items:
        return pd.DataFrame()
    df = pd.DataFrame(us_gaap_items[key]["units"]["USD"])
    df["start"] = pd.to_datetime(df["start"])
    df["end"] = pd.to_datetime(df["end"])
    annual = df[(df["form"] == "10-K") & (df["fp"] == "FY")]
    annual = annual[(annual["end"] - annual["start"]).dt.days > 300]
    annual = annual.sort_values("filed").drop_duplicates("end", keep="last")
    return annual[["end", "val"]]

# 두 태그에서 각각 뽑아서 합치기
rev_old = get_annual_revenue(us_gaap_items, "Revenues")
rev_new = get_annual_revenue(us_gaap_items, "RevenueFromContractWithCustomerExcludingAssessedTax")

combined = pd.concat([rev_old, rev_new]).drop_duplicates("end", keep="last").sort_values("end")
print(combined)

#====================================================================================================

# 9. 전년 대비 변동률(YoY % change) 계산
combined = combined.reset_index(drop=True)
combined["yoy_change_pct"] = combined["val"].pct_change() * 100

# 10. Z-score 계산: 이 변동률이 "평소" 대비 몇 표준편차만큼 벗어났는가
mean_change = combined["yoy_change_pct"].mean()
std_change = combined["yoy_change_pct"].std()

combined["z_score"] = (combined["yoy_change_pct"] - mean_change) / std_change

# 11. Z-score 기준으로 이상치 플래그 (일반적으로 |Z| >= 2를 기준으로 많이 씀)
Z_THRESHOLD = 2
combined["flag"] = combined["z_score"].abs() >= Z_THRESHOLD

print(combined[["end", "val", "yoy_change_pct", "z_score", "flag"]])