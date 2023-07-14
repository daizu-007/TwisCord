#misskeyの新しい投稿をTwisCordのTLに転送します。
import asyncio
import json
import websockets
import requests

#サーバーのURLの設定
misskey_url = "wss://mk.shrimpia.network/streaming"
#discord web hookのURLを設定
discord_url = "https://discordapp.com/api/webhooks/1127614453274386504/XknVVjktWE9NgT6WBcf5IcjvDAYrVAX8_ud8_w9rQKrQYh4vXxVRsEqJcjuSrM67tmnE"

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
                        #data = json.dumps(data)
                        await discord(data)

    #エラーが起きたら内容を表示する
    except Exception as e:
        print("error at misskey function. error is "+ e)

#discord側での処理
async def discord(data):
    try:
        #データを取得
        note = data['body']['body']#ノート
        user = note["user"]#ユーザー
        name_of_user = user["name"]#ユーザー名
        avatar_of_user = user["avatarUrl"]#プロフィール画像のURL
        content = note["text"]#ノートのテキスト
        #TLに表示する内容
        main_content = {
            "username": name_of_user,
            "avatar_url": avatar_of_user,
            "content": f"https://mk.shrimpia.network/notes/{data['body']['body']['id']}"}

        #headerを設定してTLに送信
        headers = {'Content-Type': 'application/json'}
        requests.post(discord_url, json.dumps(main_content), headers=headers)
    
    #エラーが起きたら内容を表示する
    except Exception as e:
        print("error at discord function. error is "+ e)

#実行
asyncio.run(misskey())
#asyncio.run(discord())
