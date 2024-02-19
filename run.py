import discord
from discord.ext import commands
from config import config
import os
import asyncio


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=config.BOT_PREFIX,intents=intents)

# 調用event函式庫
@bot.event
# 當機器人完成啟動
async def on_ready():
    print(f"目前登入身份 --> {bot.user}")   #顯示訊息提示啟動成功

async def load_extensions():    #載入cog
    for filename in os.listdir("./commands"):
        if filename.endswith(".py"):
            await bot.load_extension(f"commands.{filename[:-3]}")

@bot.command()
async def reload(ctx):
    for filename in os.listdir("./commands"):
        if filename.endswith(".py"):
            await bot.unload_extension(f"commands.{filename[:-3]}")
    for filename in os.listdir("./commands"):
        if filename.endswith(".py"):
            await bot.load_extension(f"commands.{filename[:-3]}")
    await ctx.send("reload successfully.")

if __name__ == "__main__":
    asyncio.run(load_extensions())
    bot.run(config.Bot_TOKEN)