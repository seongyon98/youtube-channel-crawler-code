import os
from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi

def get_video_transcript(video_id):
    """
    유튜브 영상의 한글 또는 영어 자동 생성/수동 자막을 가져옵니다.
    """
    if not video_id:
        return None
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en'])
        text = " ".join([item['text'] for item in transcript])
        # 앞부분 1500자만 추출 (강의 스타일 파악에 충분하며 토큰 비용 절약)
        return text[:1500]
    except Exception:
        return None

def review_channel_with_ai(channel_title, description, video_id, video_title, video_thumbnail_url, search_keyword):
    """
    OpenAI API를 사용하여 채널명과 설명이 교육적이며 '검색어'와 관련이 있는지 판별합니다.
    """
    import os
    import time
    
    time.sleep(1.5) # API 속도 제한(TPM) 방지를 위한 기본 지연

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return True # API 키가 없으면 기본적으로 통과시킴

    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    
    transcript_text = get_video_transcript(video_id)
    
    if transcript_text:
        # 자막이 있는 경우: 자막 기반 텍스트 분석
        prompt = f"""You are an expert YouTube channel analyst. Evaluate the following channel based on its title, description, latest video title, and video transcript snippet.
Objective: Determine if this channel primarily produces 'Educational, Informational, or Tech/Business Review' content AND if it is RELEVANT to the search keyword.

Keyword: "{search_keyword}"

- CRITICAL FINANCE RULE: If the Keyword "{search_keyword}" does NOT explicitly imply finance/trading (e.g., stocks, crypto, real estate), you MUST REJECT (Answer NO) any channels focused on stock/crypto trading or real-estate speculation, even if they use the keyword.
- ACCEPTABLE (Answer YES): Professional lectures, coding/tech tutorials, informative tech/business news, or expert knowledge sharing THAT are contextually related or useful to someone searching for "{search_keyword}".
- UNACCEPTABLE (Answer NO): Low-effort AI TTS (Text-to-Speech) spam, generic gameplay/streaming, purely personal vlogs, mukbang, clickbait gossip, OR channels that have NO meaningful relation to the target keyword "{search_keyword}".

Respond ONLY with YES or NO.

[Channel Title]: {channel_title}
[Channel Description]: {description}
[Latest Video Title]: {video_title}
[Transcript Snippet]: {transcript_text}
"""
        messages = [
            {"role": "system", "content": "Respond ONLY with YES or NO."},
            {"role": "user", "content": prompt}
        ]
    else:
        # 자막이 없는 경우: 썸네일 이미지를 포함한 비전(Vision) 분석 Fallback
        prompt_text = f"""You are an expert YouTube channel analyst. Evaluate this channel based on its title, description, latest video title, and the provided video thumbnail (since there is no transcript).
Objective: Determine if this channel primarily produces 'Educational, Informational, or Tech/Business Review' content AND if it is RELEVANT to the search keyword.

Keyword: "{search_keyword}"

- CRITICAL FINANCE RULE: If the Keyword "{search_keyword}" does NOT explicitly imply finance/trading (e.g., stocks, crypto, real estate), you MUST REJECT (Answer NO) any channels focused on stock/crypto trading or real-estate speculation, even if they use the keyword.
- ACCEPTABLE (Answer YES): Professional lectures, coding/tech tutorials, informative tech/business news, software showcase screen captures, or a real person delivering expert knowledge THAT are contextually related or useful to someone searching for "{search_keyword}".
- UNACCEPTABLE (Answer NO): Low-effort AI avatars/spam, generic gameplay/streaming, purely personal vlogs, mukbang, clickbait gossip, OR channels that have NO meaningful relation to the target keyword "{search_keyword}".

Respond ONLY with YES or NO.

[Channel Title]: {channel_title}
[Channel Description]: {description}
[Latest Video Title]: {video_title}
"""
        # 썸네일 URL이 없을 수도 있는 아주 희귀한 케이스 방어
        content_array = [{"type": "text", "text": prompt_text}]
        if video_thumbnail_url:
            content_array.append({
                "type": "image_url",
                "image_url": {"url": video_thumbnail_url}
            })
            
        messages = [
            {"role": "system", "content": "Respond ONLY with YES or NO."},
            {
                "role": "user",
                "content": content_array
            }
        ]
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0,
                max_tokens=10
            )
            result = response.choices[0].message.content.strip().upper()
            return "YES" in result
        except Exception as e:
            err_str = str(e)
            if '429' in err_str or 'rate_limit_exceeded' in err_str or 'insufficient_quota' in err_str:
                if attempt < max_retries - 1:
                    print(f"  ⏳ OpenAI API 처리량 초과 대기 중... (20초 후 재시도 {attempt+1}/{max_retries})")
                    time.sleep(20)
                    continue
            print(f"⚠️ OpenAI API 호출 오류 (일단 통과 처리함): {e}")
            return True
