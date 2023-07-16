#misskeyの新しい投稿をTwisCordのTLに転送します。
#必要なライブラリのインポート
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
#URL集
urls = {"misskeyio_icon":"https://s3.arkjp.net/misskey/webpublic-0c66b1ca-b8c0-4eaa-9827-47674f4a1580.png"}

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
                data = json.loads(await ws.recv())#jsonをオブジェクトに変換
                #print(data)
                if data["type"] == "channel":#もしchannelの情報なら
                    await PostToDiscord(data)#PostToDiscord関数を呼び出す

    #エラーが起きたら内容を表示する
    except Exception as e:
        print("error at GetFromMisskey function. error is "+ str(e))

#discord側での処理
async def PostToDiscord(data):
    try:
        if data["body"]["type"] == "note":#もし新規ノートなら
            #データを取得
            note = data['body']['body']#ノートのデータ
            user = note["user"]#ユーザー
            name_of_user = user["name"]#ユーザー名
            avatar_of_user = user["avatarUrl"]#プロフィール画像のURL
            note_text = note["text"]#ノートのテキスト
            note_url = f"https://misskey.io/notes/{data['body']['body']['id']}"#ノートのURL
            user_url = f"https://misskey.io/@{user['username']}"#ユーザープロフィールのURL
            attachment_file = note['files']#添付ファイル

            #ユーザー名が取得できないユーザーへの特例処置
            if name_of_user == None:
                name_of_user = "名無しのMisskey.io民"
            
            #TLに表示する内容を作成（埋め込み）
            embed = discord.Embed(title=name_of_user, url=user_url, #ユーザープロフィールのリンク付きユーザー名
                                  description=note_text)#ノートの本文
            embed.set_author(name="Misskey.io", #送信元
                             icon_url=urls["misskeyio_icon"], #アイコンのURL
                             url=note_url)#ノートのURL
            embed.set_thumbnail(url=avatar_of_user)#ユーザーのアイコン

            if not attachment_file == []:
                #print(note['files'])
                embed.set_image(url=attachment_file[0]['url'])#添付ファイルの一番目のURLを取得し画像として表示（要修正）

            #TLに表示する内容と受信した内容を表示（デバック用）
            #print(f"{line}\n title: {name_of_user}\n url: {note_url}\n text: {note_text}\n{line}\n"+json.dumps(note, indent=4))
            
            #TLに送信
            await timeline.send(embed=embed)
    
    #エラーが起きたら内容を表示する
    except Exception as e:
        print("error at PostToDiscord function. error is "+ str(e))

    
#botの起動時に実行
@bot.event
async def on_ready():
    global timeline #timelineというグローバル関数を定義
    timeline = discord.utils.get(bot.get_all_channels(), name='👥timeline')#tiemlineチャンネル
    await GetFromMisskey()#GetFromMisskey関数を呼び出す

#実行
#asyncio.run(GetFromMisskey()) #テスト用
#asyncio.run(PostToDiscord()) #テスト用
bot.run(dcToken) #botを起動

