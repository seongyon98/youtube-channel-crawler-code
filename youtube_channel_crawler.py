from googleapiclient.errors import HttpError
import os
import sys
import io
import time
import argparse
from dotenv import load_dotenv

# Windows 터미널에서 이모지 출력 시 발생하는 cp949 인코딩 에러 방지
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from src.config import (
    MAX_RESULTS_PER_KEYWORD, KOREAN_ONLY, ORDER,
    CONTACTABLE_ONLY, EDUCATION_ONLY, CHANNEL_AGE_MONTHS,
    LAST_UPLOAD_MONTHS, KEYWORD_SLEEP_SECONDS,
    USE_OPENAI_FILTER
)
from src.crawler import YouTubeChannelCrawler


def main():
    load_dotenv()
    API_KEY = os.getenv('YOUTUBE_API_KEY')

    if not API_KEY or API_KEY == 'YOUR_ACTUAL_API_KEY_HERE':
        print("⚠️  오류: API 키가 설정되지 않았습니다!")
        print("📝 .env 파일을 생성하고 다음 내용을 입력하세요:")
        print("   YOUTUBE_API_KEY=your_actual_api_key_here")
        return

    if USE_OPENAI_FILTER:
        OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        if not OPENAI_API_KEY or OPENAI_API_KEY == 'YOUR_ACTUAL_OPENAI_API_KEY_HERE':
            print("⚠️  오류: OpenAI API 키가 설정되지 않았습니다!")
            print("📝 .env 파일에 다음 내용을 추가하거나 환경 변수에 설정하세요:")
            print("   OPENAI_API_KEY=your_actual_openai_api_key_here")
            print("💡 AI 필터링을 원하지 않는다면 src/config.py에서 USE_OPENAI_FILTER = False 로 변경하세요.")
            return

    NAME_FILE = 'my_name.txt'
    my_name = "default"
    if os.path.exists(NAME_FILE):
        try:
            with open(NAME_FILE, 'r', encoding='utf-8') as f:
                name_str = f.read().strip()
                # 윈도우 파일명에 안전한 문자만 남기기
                safe_name = "".join(c for c in name_str if c.isalnum() or c in (' ', '_', '-')).strip()
                if safe_name:
                    my_name = safe_name.replace(" ", "_")
        except:
            pass

    KEYWORDS_FILE = f'keywords_{my_name}.txt'

    if not os.path.exists(KEYWORDS_FILE):
        print(f"⚠️  오류: {KEYWORDS_FILE} 파일이 없습니다!")
        print(f"\n📝 {KEYWORDS_FILE} 파일을 생성하고 키워드를 한 줄에 하나씩 입력하세요.")
        try:
            with open(KEYWORDS_FILE, 'w', encoding='utf-8') as f:
                f.write("파이썬\n업무자동화\nAI 에이전트\n")
            print(f"\n✅ 예시 파일({KEYWORDS_FILE})을 생성했습니다! 파일을 수정한 후 다시 실행하세요.")
        except Exception as e:
            print(f"\n❌ 파일 생성 실패: {e}")
        return

    try:
        with open(KEYWORDS_FILE, 'r', encoding='utf-8') as f:
            keywords = [line.strip() for line in f if line.strip()]
        if not keywords:
            print(f"⚠️  오류: {KEYWORDS_FILE} 파일이 비어있습니다!")
            return
    except Exception as e:
        print(f"⚠️  파일 읽기 오류: {e}")
        return

    crawler = YouTubeChannelCrawler(API_KEY)

    print("="*60)
    print("🎯 YouTube 채널 자동 수집 시작")
    print("="*60)
    print(f"📋 키워드 파일: {KEYWORDS_FILE}")
    print(f"📊 총 키워드 수: {len(keywords)}개")
    print(f"🎯 키워드당 목표: {MAX_RESULTS_PER_KEYWORD}개")
    print(f"🇰🇷 한국 채널만: {'예' if KOREAN_ONLY else '아니오'}")
    print(f"📧 연락처 필수: {'예' if CONTACTABLE_ONLY else '아니오'}")
    print(f"🎓 강의 채널만: {'예' if EDUCATION_ONLY else '아니오'}")
    if CHANNEL_AGE_MONTHS: print(f"📅 채널 개설: {CHANNEL_AGE_MONTHS}개월 이내")
    if LAST_UPLOAD_MONTHS: print(f"🎬 최근 활동: {LAST_UPLOAD_MONTHS}개월 이내")
    print(f"📊 정렬: 관련성순")
    print("="*60)
    print("\n키워드 목록:")
    for i, keyword in enumerate(keywords, 1):
        print(f"  {i}. {keyword}")
    print("\n" + "="*60)
    
    # [추가] 자동 모드 인자 확인
    parser = argparse.ArgumentParser()
    parser.add_argument('--auto', action='store_true', help='Skip start prompt')
    args, unknown = parser.parse_known_args()

    if not args.auto:
        input("\n계속하려면 Enter를 누르세요... (Ctrl+C로 취소)")

    total_failed = 0
    results_summary = []

    for idx, keyword in enumerate(keywords, 1):
        print(f"\n\n{'#'*60}")
        print(f"# 진행: {idx}/{len(keywords)} - '{keyword}'")
        print(f"{'#'*60}\n")

        try:
            channels, data_file, new_count = crawler.crawl(
                keyword,
                max_results=MAX_RESULTS_PER_KEYWORD,
                korean_only=KOREAN_ONLY,
                order=ORDER,
                data_file=None,
                update_mode=True,
                contactable_only=CONTACTABLE_ONLY,
                channel_age_months=CHANNEL_AGE_MONTHS,
                last_upload_months=LAST_UPLOAD_MONTHS,
                education_only=EDUCATION_ONLY
            )
            if not channels:
                print(f"\n⚠️ '{keyword}' 검색 결과가 0건입니다. 빈 파일을 저장하지 않거나 기존 파일을 삭제합니다.")
                if os.path.exists(data_file):
                    os.remove(data_file)
            else:
                crawler.save_to_json(channels, data_file)

            results_summary.append({
                'keyword': keyword, 'file': data_file,
                'total': len(channels), 'new': new_count,
                'contactable': sum(1 for ch in channels if ch.get('contactable'))
            })
            print(f"\n✅ '{keyword}' 완료!")
            print(f"   파일: {data_file}")
            print(f"   수집: {len(channels)}개 (전체), 신규: {new_count}개")

        except HttpError as e:
            if e.resp.status == 403 and 'quotaExceeded' in str(e):
                print(f"\n🚨 [치명적 오류] YouTube API 일일 할당량(Quota) 초과! 수집 작업을 중단합니다.")
                break
            print(f"\n❌ '{keyword}' 실패: {e}")
            total_failed += 1
            results_summary.append({'keyword': keyword, 'file': None, 'total': 0, 'new': 0, 'contactable': 0, 'error': str(e)})
        except Exception as e:
            print(f"\n❌ '{keyword}' 실패: {e}")
            total_failed += 1
            results_summary.append({'keyword': keyword, 'file': None, 'total': 0, 'new': 0, 'contactable': 0, 'error': str(e)})

        if idx < len(keywords):
            print(f"\n⏳ 다음 키워드로 이동... ({KEYWORD_SLEEP_SECONDS}초 대기)")
            time.sleep(KEYWORD_SLEEP_SECONDS)

    # 최종 요약
    print("\n\n" + "="*60)
    print("🎉 전체 수집 완료!")
    print("="*60)
    print(f"\n📊 최종 통계:")
    print(f"   처리한 키워드: {len(results_summary)}개")
    print(f"   성공: {len(results_summary) - total_failed}개")
    print(f"   실패: {total_failed}개")
    print(f"\n📋 키워드별 결과:")
    print("-" * 60)
    for i, result in enumerate(results_summary, 1):
        if 'error' in result:
            print(f"{i:2d}. {result['keyword']:20s} - ❌ 실패")
        else:
            print(f"{i:2d}. {result['keyword']:20s} - ✅ {result['total']:3d}개 채널 (신규: {result['new']}개)")
            print(f"    └─ 파일: {result['file']}")
    print("\n" + "="*60)
    print("🎉 전체 수집 및 동기화 작업이 완료되었습니다!")
    print(f"⏰ 완료 시각: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")
    print("✨ 이제 이 창을 닫으셔도 좋습니다.")
    print("="*60)


if __name__ == '__main__':
    main()