#misskeyの新しい投稿をTwisCordのTLに転送します。
import asyncio
import json
import websockets
import requests
import discord
import os

#botの権限 .allで全ての権限を与える。
intents = discord.Intents().all() 
#botを定義する
bot = discord.Client(intents=intents)
#discordのトークン
dcToken = os.environ["dctoken"]
#misskeyサーバーのURLの設定
misskey_url = "wss://mk.shrimpia.network/streaming" #shrinpiaのアドレス

print(dcToken)
#misskey側での処理
async def misskey():
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
                    if data["body"]["type"] == "note":
                        note = data['body']['body']
                        await discord(note)

    #エラーが起きたら内容を表示する
    except Exception as e:
        print("errer at misskey function. errer is "+ e)

#discord側での処理
async def discord(note):
    try:
        #データを取得
        user = note["user"]#ユーザー
        name_of_user = user["name"]#ユーザー名
        avatar_of_user = user["avatarUrl"]#プロフィール画像のURL
        content = note["text"]#ノートのテキスト
        #TLに表示する内容
        main_content = {
            "username": name_of_user,
            "avatar_url": avatar_of_user,
            "content": content}

        #headerを設定してTLに送信
        headers = {'Content-Type': 'application/json'}
        requests.post(discord_url, json.dumps(main_content), headers=headers)
    
    #エラーが起きたら内容を表示する
    except Exception as e:
        print("errer at discord function. errer is "+ e)

#実行
#asyncio.run(misskey())
#asyncio.run(discord())
bot.run(dcToken)