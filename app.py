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

    shops = firstshop + '\n\n' + secondshop + '\n\n' + thirdshop
    messages = TextSendMessage(text=shops)
    line_bot_api.reply_message(event.reply_token, messages=messages)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
