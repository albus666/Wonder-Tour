from typing import List

import jieba
import jieba.posseg as pseg

jieba.setLogLevel(jieba.logging.INFO)
jieba.load_userdict('dataset/district.dict')

"""
# 加载中文停用词表
"""


def load_stopwords(stopwords_path='dataset/cn_stopwords.txt'):
    with open(stopwords_path, 'r', encoding='utf-8') as f:
        stopwords = set([line.strip() for line in f.readlines()])
    return stopwords


"""
# 提取地点名词
"""


def get_keyword(text: str) -> list[str]:
    # 加载停用词
    stopwords = load_stopwords()
    # 定义允许的词性：地名、专有名词、名词、机构团体名、人名
    allowed_flags = {'ns', 'nz', 'n', 'nt', 'nr'}
    # 定义数值相关词性：数词、量词、非语素字
    numeric_flags = {'m', 'q', 'x'}
    # 定义需要排除的非景区修饰词（与停用词合并）
    exclude_modifiers = {'天气', '温度', '风景', '地方','评价','特点'}
    exclude_modifiers.update(stopwords)  # 合并停用词库

    # 步骤1：提取连续的名词块（保持不变）
    words_flags = list(pseg.cut(text))
    candidates = []
    current_chunk = []
    for word, flag in words_flags:
        if flag in allowed_flags:
            current_chunk.append(word)
        else:
            if current_chunk:
                candidates.append(''.join(current_chunk))
                current_chunk = []
    if current_chunk:
        candidates.append(''.join(current_chunk))

    # 步骤2：过滤候选名称（增加停用词过滤）
    result = []
    for candidate in candidates:
        sub_words_flags = list(pseg.cut(candidate))
        merged = ''.join([word for word, _ in sub_words_flags])
        if merged != candidate:
            continue

        valid = True
        temp_name = []
        for word, flag in sub_words_flags:
            # 增加停用词判断条件
            if word in exclude_modifiers or flag in numeric_flags:
                valid = False
                break
            if flag not in allowed_flags:
                valid = False
                break
            temp_name.append(word)

        if valid:
            result.append(candidate)
        else:
            # 截断到第一个非法词前（包含停用词）
            truncated = []
            for word, flag in sub_words_flags:
                if word in exclude_modifiers or flag in numeric_flags or flag not in allowed_flags:
                    break
                truncated.append(word)
            if truncated:
                result.append(''.join(truncated))

    # 步骤3：最终词性验证（保持不变）
    keywords = []
    for name in result:
        sub_words = list(pseg.cut(name))
        merged = ''.join([word for word, _ in sub_words])
        if merged != name:
            continue
        all_allowed = all(flag in allowed_flags for _, flag in sub_words)
        if all_allowed:
            keywords.append(name)

    return keywords
