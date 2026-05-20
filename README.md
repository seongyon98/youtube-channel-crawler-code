# 🎯 YouTube 채널 자동 수집기

YouTube Data API v3를 사용하여 키워드 기반으로 채널을 자동 수집하는 Python 스크립트입니다.

**완전 자동화 + 스마트 필터링**: 키워드 파일만 만들면 활발하고 연락 가능한 한국 강의/교육 채널만 자동으로 수집합니다!

## ✨ 주요 기능

### 🤖 완전 자동화
- ✅ **키워드 파일 기반 자동 수집** - keywords.txt에 키워드만 입력하면 자동 실행
- ✅ **키워드당 지정 개수 자동 수집** - 설정 변경 가능
- ✅ **중복 자동 제거** - 같은 채널은 한 번만 저장
- ✅ **부족분 자동 보충** - 목표 개수 달성까지 자동 추가 검색

### 🎯 스마트 필터링
- ✅ **교육 채널 집중** - 채널 제목, 설명에 강의/교육 관련 키워드 포함시 수집 (게임/먹방 등 자동제외)
- ✅ **한국 채널 필터링** - 국가 설정 또는 한글 포함 여부로 판단
- ✅ **연락처 필수 필터** - 연락 수단이 없는 채널 자동 제외
- ✅ **채널 활동 필터링** - 최근 n개월 이내 활동 채널만 수집
- ✅ **관련성순 정렬** - 검색어와 가장 관련성 높은 채널 우선

### 📧 연락처 자동 추출
채널 설명에서 다음 연락처를 자동으로 추출:
- 이메일 주소
- 전화번호 (개인 휴대폰 번호 위주)
- 카카오톡 ID
- 기타 링크 (블로그, 개인 웹사이트 등)

### 💾 효율적인 데이터 관리
- ✅ **단일 파일 관리** - 키워드당 하나의 JSON 파일로 누적 저장 (`data/` 폴더)
- ✅ **검색어별 자동 분류** - 각 키워드마다 별도 파일
- ✅ **날짜 필드 저장** - 수집 날짜를 데이터 내부에 저장
- ✅ **키워드 추적** - 어떤 검색어로 찾았는지 기록
- ✅ **무제한 누적** - 실행할 때마다 기존 데이터에 새 채널 계속 추가


## 🚀 빠른 시작

### 1. 설치

```bash
# 필수 라이브러리 설치
pip install google-api-python-client python-dotenv
```

또는

```bash
pip install -r requirements.txt
```

### 2. API 키 설정

1. 프로젝트 폴더에 `.env` 파일 생성:
```text
YOUTUBE_API_KEY=여기에_발급받은_API_키_입력
```

### 3. 키워드 파일 생성

`keywords.txt` 파일을 만들고 수집할 키워드 입력 (한 줄에 하나씩):
```text
파이썬
업무자동화
AI 에이전트
```

### 4. 실행

```bash
python youtube_channel_crawler.py
```


## 📁 프로젝트 구조 및 결과 파일

### 기본 구조
최신 업데이트로 코드 모듈화가 완료되어 가독성과 유지보수성이 대폭 향상되었습니다.

```text
youtube crawler/
  ├── .env                              ← API 키 입력
  ├── keywords.txt                      ← 검색 키워드 목록
  ├── youtube_channel_crawler.py        ← 🎯 메인 실행 스크립트
  │
  ├── src/                              ← ⚙️ 코어 모듈
  │   ├── config.py                     ← 🔧 수집 설정 및 키워드 리스트 수정
  │   ├── crawler.py                    ← 크롤러 메인 클래스
  │   ├── filters.py                    ← 교육 채널 및 한국어 판별 로직
  │   └── contact.py                    ← 연락처 텍스트 추출 로직
  │
  └── data/                             ← 📂 크롤링 결과 저장 폴더
      ├── youtube_channels_파이썬.json
      └── youtube_channels_업무자동화.json
```

**결과물은 실행 시 무조건 `data/` 폴더 내부에 저장되며 매 실행 시 기존 JSON에 누적 업데이트 됩니다.**


## ⚙️ 설정 변경 가이드 (`src/config.py`)

수집 개수나 필터링 조건을 바꾸고 싶을 때 더 이상 복잡한 크롤러 코드를 열 필요가 없습니다. 
**`src/config.py` 파일만 열어서 수정해 주세요!**

```python
# src/config.py 내부

MAX_RESULTS_PER_KEYWORD = 50     # 키워드당 최대 수집 채널 수
KOREAN_ONLY = True               # 한국 채널만 수집 여부
CONTACTABLE_ONLY = True          # 연락처 있는 채널만 수집 여부
EDUCATION_ONLY = True            # 강의/교육 채널만 수집 여부

CHANNEL_AGE_MONTHS = None        # 채널 개설 기간 제한 (None = 제한 없음)
LAST_UPLOAD_MONTHS = 6           # 최근 업로드 기간 제한 (6 = 최근 6개월 이내)

# 강의 키워드 / 제외 키워드 리스트 역시 여기서 관리합니다.
EDU_KEYWORDS = ['강의', '강좌', '튜토리얼', ... ]
EXCLUDE_KEYWORDS = ['게임 실황', '일상 브이로그', ... ]
```


## 📋 JSON 데이터 형식

수집된 데이터(`data/` 폴더 내)는 다음과 같은 형식을 가집니다.

```json
[
  {
    "channel_id": "UC1234567890",
    "title": "파이썬Master",
    "description": "파이썬 강의를 제공합니다.\n문의: contact@example.com",
    "custom_url": "@pythonmaster",
    "published_at": "2023-01-15T00:00:00Z",
    "last_upload_date": "2024-02-15T10:30:00Z",
    "country": "KR",
    "is_korean": true,
    "subscriber_count": "4780",
    "video_count": "120",
    "view_count": "263482",
    "channel_url": "https://www.youtube.com/channel/UC1234567890",
    "custom_channel_url": "https://www.youtube.com/@pythonmaster",
    "email": "contact@example.com",
    "phone": "N/A",
    "kakao": "N/A",
    "other_links": "N/A",
    "contactable": true,
    "thumbnail": "...",
    "collected_date": "2025-02-20",
    "search_keyword": "파이썬"
  }
]
```


## ⚠️ 주의사항

### API 할당량 (Quota) 정책
- YouTube Data API 무료 할당량은 **하루 10,000 units** 입니다.
- 50개 채널 수집 시 키워드 1개당 약 1500~2000 units를 소비합니다. (Batch 최적화 완료 상태)
- 할당량을 모두 소진하면 스크립트가 `quotaExceeded` 에러를 감지하고 자동으로 안전하게 종료됩니다.
- 할당량은 매일 오후 4시(PST 기준 자정)에 초기화됩니다.

---

**Happy Crawling! 🎉**
*v3.0 - 모듈 아키텍처 개편 및 구조 최적화*
