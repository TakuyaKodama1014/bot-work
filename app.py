import os
import requests
import json

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, CarouselTemplate, CarouselColumn)

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]

GURUNAVI_KEY_ID = os.environ["GURUNAVI_KEY_ID"]

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def response_message(event):
    checktext = event.message.text
    if '@' in checktext:
        freeword = checktext.replace('@', ',')
    elif '＠' in checktext:
        freeword = checktext.replace('＠', ',')
    else:
        freeword = checktext

    api = "https://api.gnavi.co.jp/RestSearchAPI/v3/?keyid={key}&freeword={freeword}"
    url = api.format(key=GURUNAVI_KEY_ID, freeword=freeword)
    data = requests.get(url)
    data_json = json.loads(data.text)
    firstshop = data_json["rest"][0]["url"]
    secondshop = data_json["rest"][1]["url"]
    thirdshop = data_json["rest"][2]["url"]

    if checktext in ['肉', 'お肉', 'にく', 'ニク', 'おにく']:
        niku = firstshop + '\n' + secondshop + '\n' + thirdshop
        messages = TextSendMessage(text=niku)
    elif checktext in ['魚', 'お魚', 'さかな', 'サカナ', 'おさかな']:
        s = 'Line1\nLine2\nLine3'
        messages = TextSendMessage(text=s)
    else:
        bourbon = 'やあ （´・ω・｀)ようこそ、バーボンハウスへ。\nこのテキーラはサービスだから、まず飲んで落ち着いて欲しい。\nうん、「また」なんだ。済まない。\n仏の顔もって言うしね、謝って許してもらおうとも思っていない。\nでも、このスレタイを見たとき、君は、きっと言葉では言い表せない「ときめき」みたいなものを感じてくれたと思う。\n殺伐とした世の中で、そういう気持ちを忘れないで欲しいそう思って、このスレを立てたんだ。\nじゃあ、注文を聞こうか。'
        messages = TextSendMessage(text=bourbon)

    line_bot_api.reply_message(event.reply_token, messages=messages)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
