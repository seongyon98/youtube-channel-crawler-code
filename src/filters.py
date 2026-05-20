import re
from src.config import EDU_KEYWORDS, EXCLUDE_KEYWORDS


def has_exclude_keyword(title, description):
    """설명란이나 제목에 명백한 제외 키워드(게임, 먹방 등)가 있는지 확인"""
    text = (title + ' ' + description).lower()
    for keyword in EXCLUDE_KEYWORDS:
        if keyword in text:
            return True
    return False


def is_education_channel(title, description):
    """
    강의/교육 채널인지 판단.
    포함 키워드(EDU_KEYWORDS)가 하나라도 있고,
    제외 키워드(EXCLUDE_KEYWORDS)가 없어야 True 반환.
    """
    text = (title + ' ' + description).lower()

    for keyword in EXCLUDE_KEYWORDS:
        if keyword in text:
            return False

    for keyword in EDU_KEYWORDS:
        if keyword in text:
            return True

    # 키워드가 없으면 제외
    return False


def is_korean_text(text):
    """한글 포함 여부 확인"""
    if not text:
        return False
    korean_pattern = re.compile('[가-힣]+')
    return bool(korean_pattern.search(text))


def make_safe_filename(query):
    """검색어로부터 안전한 파일명 생성"""
    safe_query = re.sub(r'[<>:"/\\|?*]', '', query)
    safe_query = safe_query.replace(' ', '_')
    safe_query = safe_query[:50]
    return f"youtube_channels_{safe_query}.json"
