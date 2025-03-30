import json
import re
import requests


def main(url):
    headers = {
        "User-Agent": "PostmanRuntime-ApipostRuntime/1.1.0",
        "Cookie": "_pd=%7B%22_o%22%3A70%2C%22s%22%3A1030%2C%22_s%22%3A9%7D;GUID=09031167317991829446"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {'result_code': response.status_code, 'info': {}}

    # Part 1: 使用正则提取JSON数据
    script_pattern = re.compile(r'<script id="__NEXT_DATA__".*?>(.*?)</script>', re.DOTALL)
    script_match = script_pattern.search(response.text)

    if not script_match:
        return {'result_code': 404, 'info': {}}

    json_data = json.loads(script_match.group(1))
    poi_data = json_data["props"]["pageProps"]["initialState"]["poiDetail"]

    # Part 2: 使用正则提取标签数据
    hot_tags_section = re.search(r'<div class="hotTags".*?>(.*?)</div>', response.text, re.DOTALL)
    if not hot_tags_section:
        return {'result_code': 404, 'info': {}}

    span_pattern = re.compile(r'<span.*?>(.*?)</span>')
    spans = span_pattern.findall(hot_tags_section.group(1))

    def extract_number(text):
        return int(re.search(r'\d+', text).group()) if re.search(r'\d+', text) else 0

    return {
        'info': {
            'poi_id': int(poi_data["poiId"]),
            'poi_name': str(poi_data["poiName"]),
            'comment_score': float(poi_data["commentScore"]),
            'review_count': extract_number(spans[0]) if len(spans) >= 1 else 0,
            'positive': extract_number(spans[1]) if len(spans) >= 2 else 0,
            'negative': extract_number(spans[3]) if len(spans) >= 4 else 0
        }
    }
if __name__ == '__main__':
    print(main('https://you.ctrip.com/sight/zhongmu1446088/135594.html'))