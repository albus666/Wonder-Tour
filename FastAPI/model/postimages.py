__author__ = "Yishang"
__date__ = "2024-06-16"
__version__ = "1.0"
__description__ = "postimages 图床"

import re
import time
import random
import string
import requests
import mimetypes

from bs4 import BeautifulSoup

form_data = b"""------WebKitFormBoundary
Content-Disposition: form-data; name="gallery"


------WebKitFormBoundary
Content-Disposition: form-data; name="optsize"

optsize_data
------WebKitFormBoundary
Content-Disposition: form-data; name="expire"

expire_data
------WebKitFormBoundary
Content-Disposition: form-data; name="numfiles"

1
------WebKitFormBoundary
Content-Disposition: form-data; name="upload_session"

upload_session_data
------WebKitFormBoundary
Content-Disposition: form-data; name="upload_referer"

upload_referer_data
------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="filename.jpg"
Content-Type: image/jpeg

""".replace(b"\n", b"\r\n")


def upload_file(filename, filedata, filetype, optsize=0, expire=0, session=None):
    """
    将文件上传至 postimages.org 。

    optsize：
    0 -- 不缩放
    1 -- 100x75 (avatar)
    2 -- 150x112 (thumbnail)
    3 -- 320x240 (for websites and email)
    4 -- 640x480 (for message boards)
    5 -- 800x600 (15-inch monitor)
    6 -- 1024x768 (17-inch monitor)
    7 -- 1280x1024 (19-inch monitor)
    8 -- 1600x1200 (21-inch monitor)

    :param filename: 文件名
    :param filedata: 文件二进制数据
    :param filetype: 文件 Content-Type
    :param optsize: 是否重设大小
    :param expire: 过期天数
    :param session: 指定 Session
    :return: URL 为了统一，放在列表里
    """
    if session is None:
        session = requests.session()

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'max-age=0',
        'priority': 'u=0, i',
        'referer': 'https://postimg.cc/',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
    }

    # 获取 Content-Disposition: form-data; name="upload_referer"
    response = session.get("https://postimages.org", headers=headers)

    # 生成 upload_session
    # new Date().getTime()+Math.random().toString().substring(1)
    timestamp = int(time.time() * 1000)
    random_number = random.randint(1111111111111111, 9999999999999999)
    upload_session = f"{timestamp}.{str(random_number)}"

    match = re.search(r'upload_referer":"(.*?)"}}', response.content.decode())
    upload_referer = match.group(1)
    if not match:
        raise RuntimeError("无法找到 upload_referer 。")

    # 生成 WebKitFormBoundary
    boundary_chars = string.ascii_letters + string.digits
    boundary = '----WebKitFormBoundary' + ''.join(random.choices(boundary_chars, k=16))

    headers = {
        "Host": "postimages.org",
        "Connection": "keep-alive",
        "Content-Length": "57810",
        "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126"',
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
        "Content-Type": "multipart/form-data; " + boundary,
        "Accept": "application/json",
        "Cache-Control": "no-cache",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua-platform": '"Windows"',
        "Origin": "https://postimages.org",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://postimages.org/",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cookie": "__gads=ID=fda8c3227d713471:T=1718510189:RT=1718510189:S=ALNI_Ma-Fl6l8vBWezF4p_HBTbAGdMHl9Q; __gpi=UID=00000e4f157d4f6a:T=1718510189:RT=1718510189:S=ALNI_MYLnQtlIZaVGzXIPZptJeS9RlfY2Q; __eoi=ID=ad4aaddebc39c1c7:T=1718510189:RT=1718510189:S=AA-AfjZyhBj3XKDo_P6X_hDfxG8C"
    }

    # 构造 data
    data = form_data.replace(b"----WebKitFormBoundary", boundary.encode())
    data = data.replace(b"upload_session_data", upload_session.encode())
    data = data.replace(b"upload_referer_data", upload_referer.encode())
    data = data.replace(b"filename.jpg", filename.encode())
    data = data.replace(b"image/jpeg", filetype.encode())
    data = data.replace(b"optsize_data", str(optsize).encode())
    data = data.replace(b"expire_data", str(expire).encode())
    data += filedata
    data += b"\r\n--" + boundary.encode() + b"--"

    headers['Content-Type'] = "multipart/form-data; boundary=" + boundary
    response = session.post("https://postimages.org/json/rr", headers=headers, data=data)

    # return
    # {"url":"https:\/\/postimg.cc\/R6HLCktD\/0028fd8d","status":"OK","status_code":200,
    # "success": {"message":"image uploaded","code":200},
    # "request":
    #       {"gallery":"","optsize":"0","expire":"0","numfiles":"1",
    #       "upload_session":"1718510839874.5931331972712656","upload_referer":"aHR0cHM6Ly9wb3N0aW1nLmNjLw=="},
    # "status_txt":"OK"}
    try:
        assert response.json()['status_code'] == 200
    except BaseException as error:
        raise RuntimeError("服务器返回数据不正确：", response.content.decode())

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'max-age=0',
        'priority': 'u=0, i',
        'referer': 'https://postimg.cc/',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
    }

    # 获取真实图片链接
    response = session.get(response.json()['url'], headers=headers)
    soup = BeautifulSoup(response.content.decode(), "lxml")

    return [soup.find(id="code_direct").attrs['value']]

