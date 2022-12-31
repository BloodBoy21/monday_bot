# This example requires the 'message_content' intent.

import discord
from discord.ext import commands
from dotenv import load_dotenv
from lib import monday
import os

load_dotenv()

MONDAY_TOKEN = os.getenv("MONDAY_TOKEN")

monday = monday.Monday(MONDAY_TOKEN, "750538269", "next_week")

intents = discord.Intents.default()
intents.message_content = True
intents.typing = True
bot = commands.Bot(command_prefix="!", intents=intents)


def embed_issues(issues, user=None):
    description = (
        "All issues from the team" if not user else f"All issues assigned to {user}"
    )
    embed = discord.Embed(title="Issues", description=description, color=0x266DD3)
    if not issues:
        embed.add_field(name="No issues found :)", value="Good job!", inline=False)
    for issue in issues:
        embed.add_field(
            name=issue.title,
            value=f"Client: {issue.client}\nAssigned to: {issue.assigned_to}\nStatus: {issue.status}\nType: {issue.type}\nDate: {issue.date}\nGroup: {issue.group}",
            inline=False,
        )
    return embed


@bot.command(name="ping", help="Responds with pong")
async def ping(ctx):
    print("ping")
    await ctx.send("pong")


# TODO: implement a request method to get all issues from monday
@bot.command(name="issues", help="Get all issues from the team or a specific user")
async def allIssues(ctx, *args):
    user = args[0] if args else None
    data = monday.get_by_user(user) if user else monday.get_all_issues()
    await ctx.send(embed=embed_issues(data, user))


# @bot.event
# async def on_message(message):
#     if message.author == bot.user:
#         return
#     print(str(message.author) + ' said: ' + str(message.content))
#     await message.channel.send(f'You said: {message.content}')


TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
