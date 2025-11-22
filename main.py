import os
import pytz
import datetime as dt
import json
import discord
from discord.ext import tasks
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()

MODEL_NAME = "google/gemini-3-pro-preview"
talk_history_file = "talk_history.json"


with open(talk_history_file, "a") as f:
    f.close()


def read_talk_history():
    try:
        with open(talk_history_file, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def write_talk_history(append_talk):
    with open(talk_history_file, "w") as f:
        json.dumps(append_talk, f, ensure_ascii=False, indent=2)


def is_messagetime():
    jst = pytz.timezone("Asia/Tokyo")
    today = dt.datetime.now(jst)

    return today.weekday() == 2 and today.strftime("%H:%M") == "09:00"


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.circle_message_started = False
        self.channel_id = os.getenv("CHANNEL_ID")

    async def on_ready(self):
        print(f"ログインしました: {self.user}")
        if not self.circle_message_started:
            self.circle_message.start()
            self.circle_message_started = True

    async def on_message(self, message):
        print(f"送信: {message.author}: {message.content}")
        if message.author == self.user:
            return

        if message.content == "$Hello":
            await message.channel.send("Hello!")

        if "$Kotone_Bot" in message.content:
            talk_history = read_talk_history()
            message = message.content.replace("$Kotone_Bot", "")
            if not talk_history:
                talk_history.append([{
                    "role": "system", 
                    "content": "あなたは気楽に話せるボットです。"
                }, {
                    "role": "user", 
                    "content": message
                }])
            else:
                

    @tasks.loop(seconds=30)
    async def circle_message(self):
        channel = self.get_channel(int(self.channel_id))

        if is_messagetime():
            await channel.send(
                "おはようございます。今日のサークル参加予定の方は👍で反応お願いします。"
            )
            print("メッセージを送信しました")

    @circle_message.before_loop
    async def before_circle_message(self):
        await self.wait_until_ready()


intents = discord.Intents.default()
intents.guilds = True  # サーバー情報（チャンネル含む）を取得するために必要
intents.messages = True  # メッセージ内容を取得する場合（もし必要なら）
intents.message_content = True  # 特権インテント（もし必要なら）
client = MyClient(intents=intents)

client.run(os.getenv("TOKEN"))
