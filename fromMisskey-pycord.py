#misskeyの新しい投稿をTwisCordのTLに転送します。
import asyncio
import json
import websockets
import requests
import discord
import os

#初期設定
#デバックように区切りを定義
line = "========================================================================================================================================================================"
#botの権限 .allで全ての権限を与える。
intents = discord.Intents.default()
#botを定義する
bot = discord.Client(intents=intents)
#discordのトークン
dcToken = os.environ["dctoken"]
#misskeyサーバーのURLの設定
misskey_url = "wss://misskey.io/streaming" #misskey.ioのアドレス
#discord web hookのURLを設定
discord_url = os.environ["DcURL"]

#misskey側での処理
async def GetFromMisskey():
    try:
        #設定したmisskeyのURLでmisskeyにストリーミング接続
        async with websockets.connect(misskey_url) as ws:
            #localTimelineに接続
            await ws.send(json.dumps({
            "type": "connect",
            "body": {
                "channel": "localTimeline",
                "id": "frommisskeybot"
            }
            }))
            #localTimelineの新規投稿を処理
            while True:
                data = json.loads(await ws.recv())
                #print(data)
                if data["type"] == "channel":
                    await PostToDiscord(data)#PostToDiscordを呼び出す

    #エラーが起きたら内容を表示する
    except Exception as e:
        print("error at GetFromMisskey function. error is "+ str(e))

#discord側での処理
async def PostToDiscord(data):
    try:
        if data["body"]["type"] == "note":#もし新規ノートなら
            #データを取得
            note = data['body']['body']
            user = note["user"]#ユーザー
            name_of_user = user["name"]#ユーザー名
            avatar_of_user = user["avatarUrl"]#プロフィール画像のURL
            note_text = note["text"]#ノートのテキスト
            note_url = f"https://misskey.io/notes/{data['body']['body']['id']}"

            #ユーザー名が取得できないユーザーへの特例処置
            if name_of_user == None:
                name_of_user = "名無しのMisskey.io民"
            
            #TLに表示する内容を作成（埋め込み）
            embed = discord.Embed(title=name_of_user, description=note_text, url=note_url)
            embed.set_author(name=name_of_user, icon_url=avatar_of_user, url=f"https://misskey.io/users/{data['body']['body']['user']['id']}")

            #TLに表示する内容と受信した内容を表示（デバック用）
            print(f"{line}\n title: {name_of_user}\n url: {note_url}\n text: {note_text}\n{line}\n"+json.dumps(note, indent=4))

            #TLに送信
            await timeline.send(embed=embed)
    
    #エラーが起きたら内容を表示する
    except Exception as e:
        print("error at PostToDiscord function. error is "+ str(e))

    
#botの起動時に実行
@bot.event
async def on_ready():
    global timeline
    timeline = discord.utils.get(bot.get_all_channels(), name='👥timeline')
    await GetFromMisskey()

#実行
#asyncio.run(GetFromMisskey())
#asyncio.run(PostToDiscord())
bot.run(dcToken)