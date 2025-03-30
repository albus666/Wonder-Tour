import json
import requests


def find_sight_data(data):
    """在data数组中查找type为sight的有效数据"""
    for item in data:
        if isinstance(item, dict) and item.get('type') == 'sight':
            required_fields = ['districtName', 'districtId', 'productId']
            if all(item.get(field) for field in required_fields):
                return item
    return None


def main(keyword: str):
    url = "https://m.ctrip.com/restapi/soa2/30668/search"

    querystring = {
        "action": "globalonline",
        "source": "globalonline",
        "keyword": keyword
    }

    payload = ""
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Cookie": "GUID=09031022317999445208",
        "Host": "m.ctrip.com",
        "Content-Length": "0"
    }

    try:
        response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
        response.raise_for_status()

        result = response.json()
        print(result['data'][0])
        sight_data = find_sight_data(result.get('data', []))

        if not sight_data:
            print("未找到有效的景区数据")
            return None

        # 生成拼音部分
        district_name = sight_data['eName'] if sight_data['eName'] else sight_data['districtName']
        district_id = sight_data['districtId']
        product_id = sight_data['productId']

        # 查找额外信息
        poi_id = str(sight_data['poiId'])

        # 拼接URL
        ctrip_url = f"https://you.ctrip.com/sight/{district_name}{district_id}/{product_id}.html"

        search_result = {
            'url': ctrip_url,
            'poi_id': poi_id,
        }
        return search_result

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {str(e)}")
    except json.JSONDecodeError:
        print("响应数据解析失败")
    except Exception as e:
        print(f"处理异常: {str(e)}")
    return None
if __name__ == '__main__':
    print(main('郑州'))
