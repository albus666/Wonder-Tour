import requests
import time

import uuid


def get_contents(poi_id: int,max_page:int) -> list[str]:
    # info_obj = Info(**info)
    url = "https://m.ctrip.com/restapi/soa2/13444/json/getCommentCollapseList"

    user_contents = []

    # 循环1到10页
    for page_index in range(1, max_page + 1):
        try:
            payload = {
                "arg": {
                    "channelType": 2,
                    "collapseType": 0,
                    "commentTagId": 0,
                    "pageIndex": page_index,  # 动态页码
                    "pageSize": 10,
                    "poiId": poi_id,
                    "sourceType": 1,
                    "sortType": 3,
                    "starType": 0,
                    "head": {
                        "cid": str(uuid.uuid4())[:32],  # 建议动态生成设备ID
                        "ctok": "",
                        "cver": "1.0",
                        "lang": "01",
                        "sid": "8888",
                        "syscode": "09",
                        "auth": "",
                        "xsid": "",
                        "extension": []
                    }
                }
            }

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...",
                "Content-Type": "application/json",
                "Cookie": f"GUID={str(uuid.uuid4()).replace('-', '')[:32]}"  # 动态Cookie
            }

            response = requests.request("Post", url, json=payload, headers=headers)

            # 增加状态码检查
            if response.status_code != 200:
                print(f"第{page_index}页请求失败，状态码：{response.status_code}")
                continue

            data = response.json()

            # 处理分页终止条件
            if not data.get('result', {}).get('items'):
                print(f"第{page_index}页无数据，停止爬取")
                break

            # 提取评论内容
            user_contents.extend(
                [item['content'] for item in data['result']['items']]
            )

            # 添加随机延迟防止封禁
            time.sleep(1.5 + (page_index % 3) * 0.5)

        except Exception as e:
            print(f"第{page_index}页抓取异常：{str(e)}")
            continue

    return user_contents

if __name__ == '__main__':
    print(get_contents(97241))
