import json

import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import matplotlib

matplotlib.rc("font", family='Microsoft YaHei')
# 示例数据 - 替换为实际爬取的评论列表

def get_wordcloud(comments: str | list[str]):
    if type(comments) == str:
        json_str = comments.strip('"')
        comments = json.loads(json_str)

    # 1. 加载停用词表
    with open('../dataset/cn_stopwords.txt', 'r', encoding='utf-8') as f:
        stopwords = set([line.strip() for line in f])

    # 2. 中文分词处理
    text = ' '.join(comments)
    words = jieba.cut(text)
    filtered_words = [word for word in words if len(word) > 1 and word not in stopwords]

    # 3. 词频统计
    word_counts = Counter(filtered_words)

    # 4. 生成词云
    font_path = 'msyh.ttc'  # 微软雅黑字体，需确保字体文件存在
    # mask = np.array(Image.open('cloud_mask.png'))  # 可选形状蒙版

    wc = WordCloud(
        font_path=font_path,
        background_color='white',
        max_words=200,
        # mask=mask,  # 移除该行不使用形状
        max_font_size=175,
        width=1600,
        height=1200,
        collocations=False,  # 去除重复词语
        scale=1  # 默认分辨率
    ).generate_from_frequencies(word_counts)

    # 5. 可视化展示
    plt.figure(figsize=(20, 15))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.show()

    # 保存文件
    wc.to_file("./model/comment_wordcloud.png")
