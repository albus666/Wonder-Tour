import jieba.posseg as pseg

from FastAPI.model import get_keyword


def get_classification(text: str) -> str:
    # 获取关键词列表（例如：["郑州方特"]）
    keywords = get_keyword(text)
    if not keywords:
        return "-1"

    # 关键词的词性分析（每个关键词单独分词）
    keyword_props = []
    for kw in keywords:
        words = pseg.cut(kw)
        props = {
            'text': kw,
            'flags': [flag for word, flag in words],  # 记录词性列表（如 ['ns', 'nz']）
            'is_composite': False
        }
        # 判断是否为复合结构（包含地名且混合其他词性）
        if 'ns' in props['flags'] and len(set(props['flags'])) > 1:
            props['is_composite'] = True
        keyword_props.append(props)

    # 提取修饰词特征
    text_lower = text.lower()
    compare_words = ['哪个', '对比', '比较', 'vs']
    info_words = ['开放时间', '门票', '预约', '多久', '怎么去']

    has_compare = any(w in text_lower for w in compare_words)
    has_info = any(w in text_lower for w in info_words)

    # 逻辑判断流程
    # 1. 存在对比关键词 → 景点对比
    if has_compare:
        return "景点对比"

    # 2. 存在复合结构 → 强制进入信息/对比判断，跳过推荐
    if any(k['is_composite'] for k in keyword_props):
        if len(keywords) >= 2:  # 多个景点名称 → 对比
            return "景点对比"
        else:  # 单个复合景点 → 信息
            return "景点信息" if has_info else "景点信息"  # 默认信息

    # 3. 常规判断流程
    recommend_words = ['推荐', '有什么', '哪里']
    if any(w in text_lower for w in recommend_words):
        return "景点推荐"

    # 4. 默认逻辑
    return "景点信息" if has_info else "景点推荐"