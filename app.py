import os

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
    if checktext in ['肉', 'お肉', 'にく', 'ニク', 'おにく']:
        messages = TextSendMessage(text='美味しいお肉のお店')
    elif checktext in ['魚', 'お魚', 'さかな', 'サカナ', 'おさかな']:
        messages = TextSendMessage(text='美味しいお肉のお店')
    else:
        messages = TextSendMessage(text='やあ （´・ω・｀)ようこそ、バーボンハウスへ。このテキーラはサービスだから、まず飲んで落ち着いて欲しい。うん、「また」なんだ。済まない。仏の顔もって言うしね、謝って許してもらおうとも思っていない。でも、このスレタイを見たとき、君は、きっと言葉では言い表せない「ときめき」みたいなものを感じてくれたと思う。殺伐とした世の中で、そういう気持ちを忘れないで欲しいそう思って、このスレを立てたんだ。じゃあ、注文を聞こうか。お店')        
    line_bot_api.reply_message(event.reply_token, messages=messages)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
