# 🎯 AI 필터 기반 YouTube 채널 자동 수집 & 데이터 파이프라인

YouTube Data API v3와 OpenAI GPT-4o-mini를 활용하여 특정 키워드 기반의 활성화된 교육/강의 목적의 한국 채널을 수집하고 연락처를 자동 추출하는 스마트 데이터 수집 파이프라인입니다.

> [!NOTE]
> 이 프로젝트는 단순한 API 호출기가 아닙니다. **멀티모달 AI 검증(자막 분석 + 썸네일 비전 분석)**, **API 할당량 최적화(Batch 처리)**, **글로벌 상태 관리 기반의 실시간 중복 차단** 등 엔지니어링 요소를 고려하여 설계되었습니다.

---

## ✨ 주요 기능

### 🤖 1. 멀티모달 AI 심층 필터링 (OpenAI GPT-4o-mini)
단순한 텍스트 매칭을 넘어, AI를 활용하여 채널의 전문성과 의도(강의/교육)를 깊이 있게 분석합니다.
* 📝 **자막 텍스트 분석 (Text Mode)**: 동영상 자막 추출 API(`youtube-transcript-api`)를 활용하여 영상의 초반 1500자 자막을 추출한 뒤, 실제 전문 지식 전달이나 강의 형태의 콘텐츠인지 판별합니다.
* 🖼️ **썸네일 비전 분석 (Vision Mode)**: 자동 자막이 없거나 영어/한국어 자막이 제공되지 않는 경우, 영상의 썸네일 이미지 URL을 분석하여 강의용 프레젠테이션/코딩화면 캡처/지식 전달용 레이아웃 등 시각 정보로 교육 채널 여부를 판단하는 Fallback 로직을 제공합니다.
* 🚫 **금융/스팸 필터링**: 타겟 키워드와 무관하게 조회수 유도 목적의 주식/가상자산/부동산 투기성 정보 제공 채널, 그리고 AI TTS 기반 저품질 공장형 채널을 자동 차단합니다.
* ⏳ **Rate Limit 대응**: OpenAI API 호출 시 발생하는 처리량 제한(TPM/RPM 429 에러)에 대처하기 위해 자동 지연 및 재시도(Backoff/Retry) 로직이 설계되어 있습니다.

### ⚙️ 2. 데이터 파이프라인 및 필터링
* 📧 **연락처 자동 분석**: 채널 설명 텍스트 및 상세 본문 내에서 **이메일 주소, 전화번호, 카카오톡 ID, 블로그/홈페이지 외부 링크**를 정규표현식(Regex)을 이용해 자동 수집합니다.
* 🇰🇷 **한국 채널 선별**: 설정된 국가 코드(KR)뿐만 아니라, 채널명 및 설명의 한글 글자 비율을 분석해 다국어 검색 결과 중 순수 한국어 채널만 골라냅니다.
* 🎬 **채널 활성도 필터**: 휴면 채널 제외를 위해 채널의 **최근 업로드일(최근 6개월 등)**을 파악하여 현재 활동 중인 채널만 선별적으로 수집합니다.
* ⭐️ **우선 검수 채널 자동 태깅**: 채널 소개글에 비즈니스 및 협업 관련 핵심 키워드(`문의`, `강연`, `강의`, `협업`, `제안`)가 존재하면, 채널 제목 앞에 **`⭐ [우선검수]`** 표시를 붙이고 `priority_review: true` 플래그를 자동으로 부여합니다.

### 💾 3. 글로벌 중복 방지 및 캐싱 시스템 (Global Checked Engine)
* 🛡️ **과거 이력 완전 차단**: `data/processed_ids.json` 파일을 통해 기존에 한 번이라도 수집되었거나 필터링(탈락)된 채널 ID들을 글로벌하게 추적하여, 재수집 시 불필요한 API 요청과 연산 낭비를 0%로 통제합니다.
* 📂 **검색어별 격리 보관**: 수집 데이터는 `data/youtube_channels_{키워드}.json` 형태로 저장되며, 실행 시 기존 데이터가 존재하면 누적 병합(Upsert) 방식으로 저장됩니다.
* 🗂️ **JSON 키 순서 정렬 표준화**: 수집 및 저장 시 모든 채널 데이터의 JSON 키 순서를 동일하게 보장합니다. `collected_date`, `search_keyword`, `priority_review` 키가 항상 데이터 블록의 가장 마지막 줄에 일관되게 정렬되어 가독성을 높입니다.

### ⚡ 4. 실행 및 배포 편의성
* 🔄 **자동화 모드 지원**: `--auto` 파라미터를 추가하여 실행할 경우, 사용자 프롬프트 입력 단계(Enter 대기)를 건너뛰고 스케줄러(cron, Windows 작업 스케줄러)를 통해 100% 무인 자동 크롤링을 수행할 수 있습니다.
* 🏷️ **이름 기반 파일 매핑**: 작업자 혹은 프로젝트 프로필에 따라 독립된 키워드 파일을 매핑하도록 `my_name.txt`에 기록된 이름을 참조하여 `keywords_{이름}.txt` 형식의 입력 파일을 자동으로 구분하여 로드합니다.

---

## 🚀 빠른 시작

### 1. 설치 및 의존성 패키지 설치
이 프로젝트는 Google API 및 OpenAI SDK, 자막 추출 패키지를 사용합니다.

```bash
pip install -r requirements.txt
```

> `requirements.txt` 필수 라이브러리 목록:
> * `google-api-python-client` (YouTube Data API 연동)
> * `python-dotenv` (환경 변수 관리)
> * `youtube-transcript-api` (자막 추출 분석)
> * `openai` (GPT-4o-mini 멀티모달 분석)

### 2. 환경 변수 설정
프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 발급받은 API 키를 입력합니다. (템플릿: `.env.example`)

```env
# YouTube Data API Key (필수)
YOUTUBE_API_KEY=AIzaSy...

# OpenAI API Key (AI 검수 활성화 시 필수)
OPENAI_API_KEY=sk-proj-...
```

### 3. 작업자 이름 및 키워드 설정
1. `my_name.txt` 파일에 본인의 영문명 혹은 구분자 입력 (예: `seongyon`)
2. `keywords_seongyon.txt` 파일을 만들고 수집하고 싶은 키워드를 한 줄에 하나씩 입력합니다.
```text
파이썬 자동화
AI 에이전트
코딩 입문
```

### 4. 크롤러 실행
* **인터랙티브 모드** (검색 전 요약 정보 확인 및 Enter 입력 후 시작):
  ```bash
  python youtube_channel_crawler.py
  ```
* **무인 자동화 모드** (스케줄러 연동용):
  ```bash
  python youtube_channel_crawler.py --auto
  ```

---

## 📁 프로젝트 구조

```text
youtube-crawler/
  ├── .env.example              ← API 설정 템플릿 파일
  ├── .gitignore                ← API 키 및 개인 데이터 수집 폴더 배제 설정
  ├── requirements.txt          ← 의존 패키지 정보
  ├── youtube_channel_crawler.py← 🎯 프로그램 메인 진입점 (설정 로드 및 검색 실행)
  │
  ├── src/                      ← ⚙️ 코어 비즈니스 로직
  │   ├── __init__.py
  │   ├── config.py             ← 🔧 크롤링 수집 제어 설정 (필터 온오프, 키워드 목록)
  │   ├── crawler.py            ← 🔄 크롤링 파이프라인 통제 및 배치 API 요청 관리
  │   ├── ai_filter.py          ← 🤖 OpenAI GPT-4o-mini 자막 및 비전 판별 엔진
  │   ├── filters.py            ← 🧹 정규 표현식, 한글 판별 및 텍스트 기반 1차 필터
  │   └── contact.py            ← 📧 설명 본문 내 이메일, 전화번호, 카카오톡 Regex 추출기
  │
  └── data/                     ← 📂 크롤링 결과 저장 폴더 (Git 제외 대상)
      ├── processed_ids.json    ← 글로벌 중복 체크 및 탈락 이력 데이터베이스
      └── youtube_channels_{키워드}.json ← 수집된 최종 채널 데이터 목록
```

---

## ⚙️ 상세 설정 가이드 (`src/config.py`)

기본 수집 거동 및 필터링 사용 여부는 `src/config.py`에서 손쉽게 수정 가능합니다.

```python
# src/config.py

# 수집 설정
MAX_RESULTS_PER_KEYWORD = 100   # 키워드당 최대 수집 채널 수
KOREAN_ONLY = True              # 한국 채널만 수집 여부
ORDER = 'relevance'             # 검색 정렬 (relevance / date / viewCount)
CONTACTABLE_ONLY = True         # 연락처(이메일, 카톡 등)가 존재하는 채널만 수집
EDUCATION_ONLY = True           # 강의/교육 목적 채널 필터 적용 여부

CHANNEL_AGE_MONTHS = None       # 채널 개설 기간 제한 (None = 제한 없음)
LAST_UPLOAD_MONTHS = 6          # 최근 업로드 기간 제한 (6 = 최근 6개월 이내 업로드 활성 채널만)
KEYWORD_SLEEP_SECONDS = 2       # 키워드 간 API 호출 대기 시간(초)

USE_OPENAI_FILTER = True        # OpenAI GPT를 활용한 실시간 자막/비전 심층 검수 사용 여부
```

---

## 📋 JSON 데이터 출력 예시

수집 완료 시 `data/` 폴더 내 저장되는 채널의 JSON 객체 모델 구조는 다음과 같습니다.

```json
[
  {
    "channel_id": "UC1234567890",
    "title": "개발자 파이썬 튜브",
    "description": "다양한 파이썬 자동화 프로그램을 만드는 법을 알려드립니다.\n비즈니스 문의: python_dev@gmail.com",
    "custom_url": "@python_dev",
    "published_at": "2023-01-15T00:00:00Z",
    "last_upload_date": "2026-05-18T10:30:00Z",
    "country": "KR",
    "is_korean": true,
    "subscriber_count": "4520",
    "video_count": "72",
    "view_count": "153402",
    "channel_url": "https://www.youtube.com/channel/UC1234567890",
    "custom_channel_url": "https://www.youtube.com/@python_dev",
    "email": "python_dev@gmail.com",
    "phone": "N/A",
    "kakao": "N/A",
    "other_links": "https://blog.naver.com/python_dev",
    "contactable": true,
    "thumbnail": "https://yt3.ggpht.com/.../photo.jpg",
    "latest_video_id": "ab_12cdeFGh",
    "latest_video_title": "[파이썬] 10분 만에 웹 자동화 매크로 만들기!",
    "latest_video_thumb": "https://i.ytimg.com/vi/ab_12cdeFGh/hqdefault.jpg",
    "collected_date": "2026-05-20 15:40:00",
    "search_keyword": "파이썬 자동화",
    "priority_review": false
  }
]
```

---

## ⚠️ Quota 및 제한 사항

* **API 할당량 관리**: YouTube Data API는 일일 **10,000 units**의 무료 쿼터를 가집니다.
* **효율화**: 채널 정보 검색을 위해 1회당 50개의 ID를 Batch로 묶어 조회하므로 할당량 소모가 매우 효율적입니다. (채널 하나당 개별 API를 치는 구조 대비 90% 이상 절감)
* **자동 셧다운**: 할당량이 고갈될 경우 스크립트가 `quotaExceeded` 에러를 감지하여 현재까지의 결과물을 안전하게 커밋 및 저장한 후 비정상 에러 종료 대신 깔끔하게 종료됩니다.
