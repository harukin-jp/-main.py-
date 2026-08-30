import asyncio
import os
from datetime import datetime
import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# ボットの準備
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --------------------------------------------------
# 設定項目
# --------------------------------------------------
CHANNEL_ID = 1371823071979372678
TOKEN = "MTU0MzYwTk10Tgxdg2MjYwMg.GV5FL1.CaTzSCh_RXSTrP1pwiEJVhRvRR2yi0AM77bFTY"

# リアクションの定義
EMOJIS = ["🔴", "🔵", "🟡", "⚪", "🟣", "🟠", "🟢"]
OPTIONS = [
    "月曜日",
    "火曜日",
    "水曜日",
    "木曜日",
    "金曜日",
    "土曜日",
    "日曜日",
]
# --------------------------------------------------


async def send_poll():
    """定期実行されるアンケート送信関数"""
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(f"チャンネルID: {CHANNEL_ID} が見つかりませんでした。")
        return

    # 1. アンケート埋め込みメッセージの作成
    embed = discord.Embed(
        title="📅 今週のスケジュール確認",
        description="都合が良い曜日にリアクションを押してください！（複数選択可）\n※24時間後に自動集計します。",
        color=0x3498DB,
    )

    for emoji, option in zip(EMOJIS, OPTIONS):
        embed.add_field(name=f"{emoji} {option}", value="\u200b", inline=False)

    poll_message = await channel.send(embed=embed)

    # リアクションを順番に追加
    for emoji in EMOJIS:
        await poll_message.add_reaction(emoji)

    # 2. 24時間（86400秒）待機して自動集計
    await asyncio.sleep(86400)

    # 3. メッセージ情報を再取得して集計
    try:
        updated_message = await channel.fetch_message(poll_message.id)
    except discord.NotFound:
        print("アンケートメッセージが削除されていたため集計をスキップしました。")
        return

    results = []
    for reaction in updated_message.reactions:
        if str(reaction.emoji) in EMOJIS:
            idx = EMOJIS.index(str(reaction.emoji))
            count = max(0, reaction.count - 1)
            results.append((OPTIONS[idx], count))

    # 4. 集計結果の作成と送信
    result_embed = discord.Embed(
        title="📊 今週のスケジュール集計結果",
        description="アンケートの投票が締め切られました！",
        color=0x2ECC71,
    )

    for option, count in results:
        result_embed.add_field(
            name=option, value=f"**{count} 人**", inline=True
        )

    await channel.send(embed=result_embed)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

    # スケジューラーの設定（日本時間で毎週月曜日 朝6:00に実行）
    scheduler = AsyncIOScheduler(timezone="Asia/Tokyo")
    scheduler.add_job(send_poll, "cron", day_of_week="mon", hour=6, minute=0)
    scheduler.start()


@bot.command()
async def poll(ctx):
    """手動テスト用コマンド（!poll と送信すると即時アンケートを開始）"""
    await ctx.send("手動テストを開始します...")
    asyncio.create_task(send_poll())


# ボットの起動
if __name__ == "__main__":
    bot.run(TOKEN)
