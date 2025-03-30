import mimetypes
from FastAPI.model import postimages


def get_pic_link():
    filepath = "model/comment_wordcloud.png"
    filename = filepath.split('/')[-1]

    # 尝试确定文件类型
    filetype, _ = mimetypes.guess_type(filepath)
    if filetype is None:
        filetype = 'application/octet-stream'  # 使用通用二进制类型，如果无法猜测类型

    # 读取文件数据
    with open(filepath, 'rb') as file:
        filedata = file.read()

    pic_link = postimages.upload_file(filename, filedata, filetype)[0]
    return pic_link
