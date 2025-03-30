import model
from fastapi import FastAPI, Request, Depends
from pydantic import BaseModel
from jinja2 import Environment, FileSystemLoader
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/get_keyword", response_model=list[str])  # 根路由
def get_keyword(text: str) -> list[str]:
    return model.get_keyword(text)


@app.get("/classify", response_model=str)
def classify_intent(text: str) -> str:
    return model.get_classification(text)


@app.get("/get_contents")
def get_contents(poi_id: int, max_page: int):
    return model.get_contents(poi_id, max_page)


@app.get("/wordcloud", response_model=str)
def get_wordcloud(poi_id: int):
    comments =  model.get_contents(poi_id, max_page=6)
    """返回最新生成的词云图片"""
    model.get_wordcloud(comments)
    return model.get_pic_link()

# 初始化Jinja2模板环境
template_env = Environment(
    loader=FileSystemLoader(searchpath='../src/bat'),
    autoescape=True
)

class EmailRequest(BaseModel):
    to: str
    subject: str
    template_params: dict

async def verify_recaptcha(recaptcha_token: str):
    # 预留ReCaptcha验证逻辑
    return True

@app.post('/send-email')
async def send_email(
    recaptcha_token: str,
    request: EmailRequest,
    recaptcha_valid: bool = Depends(verify_recaptcha)
):
    if not recaptcha_valid:
        return {'error': 'Invalid ReCaptcha'}

    template = template_env.get_template('rd-mailform.tpl')
    html_content = template.render(**request.template_params)

    msg = MIMEMultipart()
    msg['From'] = f"{os.getenv('MAIL_FROM_NAME')} <{os.getenv('SMTP_USERNAME')}>"
    msg['To'] = request.to
    msg['Subject'] = request.subject
    msg.attach(MIMEText(html_content, 'html'))

    with smtplib.SMTP_SSL(os.getenv('SMTP_SERVER'), int(os.getenv('SMTP_PORT'))) as server:
        server.login(os.getenv('SMTP_USERNAME'), os.getenv('SMTP_PASSWORD'))
        server.send_message(msg)

    return {'status': 'success'}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
