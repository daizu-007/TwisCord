#misskeyの新しい投稿をTwisCordのTLに転送します。
#必要なライブラリのインポート
import asyncio
import json
import websockets
import requests
import discord
import os

#初期設定
#デバック用に区切りを定義
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
#discord_url = os.environ["DcURL"] #webhookを使用しない場合不要
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
    await GetFromMisskey #GetFromMisskey関数を呼び出す。いつかエラー内容を考慮するように変更したい。

#discord側での処理
async def PostToDiscord(data):
    try:
        if data["body"]["type"] == "note":#もし新規ノートなら

            #print("on PostToDiscord function") #デバック用

            #データを取得
            note = data['body']['body']#ノートのデータ
            user = note["user"]#ユーザー
            name_of_user = user["name"]#ユーザー名
            avatar_of_user = user["avatarUrl"]#プロフィール画像のURL
            note_text = note["text"]#ノートのテキスト
            note_url = f"https://misskey.io/notes/{data['body']['body']['id']}"#ノートのURL
            user_url = f"https://misskey.io/@{user['username']}"#ユーザープロフィールのURL
            attachment_file = note['files']#添付ファイル

            #デバック用、添付ファイルが含まれなければ処理をやめる
            """
            if attachment_file == []:
                return
            else:
                print("Get posts with files")
            """

            #ユーザー名が取得できないユーザーへの特例処置 (要改善)
            if name_of_user == None:
                name_of_user = "名無しのMisskey.io民"
            
            #TLに表示する内容を作成（埋め込み）
            embed = discord.Embed(title=name_of_user, url=user_url, #ユーザープロフィールのリンク付きユーザー名
                                  description=note_text)#ノートの本文
            embed.set_author(name="Misskey.io", #送信元
                             icon_url=urls["misskeyio_icon"], #アイコンのURL
                             url=note_url)#ノートのURL
            embed.set_thumbnail(url=avatar_of_user)#ユーザーのアイコン

            embeds = [embed]#複数画像に対応するために埋め込みをリスト化
            
            #すべての画像を埋め込む処理
            for number, file in enumerate(attachment_file):#添付ファイルリスト内のファイルを順に処理
                #numberはファイルの番号,fileは処理中のファイル
                #print(note['files']) #デバック用

                if file['isSensitive']: #NSFWなら
                    continue #スキップ

                if number == 0:
                    # 最初のファイルは既存のembedに追加する
                    embed.set_image(url=file['url'])#画像を埋め込む
                else:
                    # 2つ目以降のファイルは新しい埋め込みオブジェクトを作成してリストに追加
                    embed = discord.Embed(url=user_url)#新しい埋め込みオブジェクトを作成
                    embed.set_image(url=file['url'])#画像を埋め込む
                    embeds.append(embed)#リストに埋め込みを追加

                    #print("A post was made with multiple files") #デバック用
            
            #TLに表示する内容と受信した内容を表示（デバック用）
            #print(f"{line}\n title: {name_of_user}\n url: {note_url}\n text: {note_text}\n{line}\n"+json.dumps(note, indent=4))
            
            #print("I'll send") #デバック用

            #埋め込み一覧を表示（デバック用）
            #print(embeds)

            try:
                #TLに送信
                await timeline.send(embeds=embeds)#embed"s"とすることでlist型を受け取らせられる
            except Exception as e:
                print("error at posting to discord. error is "+ str(e))#discordへの返信に失敗したらエラー内容を表示

    #エラーが起きたら内容を表示する
    except Exception as e:
        print("error at PostToDiscord function. error is "+ str(e))

    
#botの起動時に実行
@bot.event
async def on_ready():
    global timeline #timelineというグローバル関数を定義
    timeline = discord.utils.get(bot.get_all_channels(), name='👥timeline')#timelineチャンネル
    await GetFromMisskey()#GetFromMisskey関数を呼び出す

#実行
#asyncio.run(GetFromMisskey()) #テスト用
#asyncio.run(PostToDiscord()) #テスト用
bot.run(dcToken) #botを起動

