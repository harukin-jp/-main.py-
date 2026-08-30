import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

# ボットの基本設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 投票を投稿したいチャンネルのID（数字のみ）
CHANNEL_ID = 1371823071979372678

# リアクションの定義
EMOJIS = ["🔴", "🔵", "🟡", "⚪"]
OPTIONS = ["月曜日", "火曜日", "水曜日", "できない"]

# 24時間後に投票を締め切る処理
async def close_poll(channel, msg_id):
    await asyncio.sleep(24 * 3600)  # 24時間待機（86,400秒）
    
    try:
        msg = await channel.fetch_message(msg_id)
        
        # 集計処理
        results = []
        for emoji, label in zip(EMOJIS, OPTIONS):
            # 該当リアクションを探す
            reaction = discord.utils.get(msg.reactions, emoji=str(emoji))
            # ボット自身の1票分を引いて集計
            count = (reaction.count - 1) if reaction else 0
            results.append(f"・{label}: {count}票")
        
        # 締め切りメッセージを送信
        result_text = "\n".join(results)
        await channel.send(
            f"【投票終了】\n"
            f"先ほどの投票を締め切りました！集計結果です：\n\n"
            f"{result_text}"
        )
    except Exception as e:
        print(f"集計エラー: {e}")

# 毎週月曜日に投票箱を設置する処理
async def send_weekly_poll():
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        msg = await channel.send(
            "【今週の予定調査（複数選択可）】\n"
            "該当する曜日にリアクションを押してください！（何個でも選べます）\n"
            "※24時間後に自動で締め切られます。\n\n"
            "🔴 : 月曜日\n"
            "🔵 : 火曜日\n"
            "🟡 : 水曜日\n"
            "⚪ : できない"
        )
        
        # 4つの絵文字リアクションを順番に追加
        for emoji in EMOJIS:
            await msg.add_reaction(emoji)
            
        # 24時間後の自動締め切りタスクを開始
        bot.loop.create_task(close_poll(channel, msg.id))

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    
    # 定期実行スケジューラー設定
    scheduler = AsyncIOScheduler(timezone="Asia/Tokyo")
    # 毎週月曜日（day_of_week='mon'）の朝6時（hour=6, minute=0）に実行
    scheduler.add_job(send_weekly_poll, 'cron', day_of_week='mon', hour=6, minute=0)
    scheduler.start()

# Discord Botのトークンを貼り付け
bot.run("MTU0MzYwOTk1OTgxODg2MjYwMg.Ggfrzp.h6i66ak3goG2TcT-t-i4BGY3TPqa3KdYZRVOBY")
