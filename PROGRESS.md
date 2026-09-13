## 2026-09-13
- SEC EDGAR API 첫 테스트: 티커→CIK 변환, companyfacts 조회 성공
- 애플 매출 데이터 연도별로 추출 (태그가 Revenues → RevenueFromContractWithCustomerExcludingAssessedTax로 바뀌는 이슈 발견, 두 태그 합쳐서 해결)
- YoY 변동률 계산 → Z-score 기반 이상치 탐지 구현, 2021년 팬데믹 매출 급증이 정확히 플래그됨
- 다음에 할 것: 변동성 다른 회사(성장주)로 비교, 여러 계정과목 확장, 여러 회사 순회하는 함수로 리팩토링