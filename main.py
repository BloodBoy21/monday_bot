import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from lib.helpers import check_server, add_group, remove_group, get_groups

load_dotenv()


intents = discord.Intents.default()
intents.message_content = True
intents.typing = True
bot = commands.Bot(command_prefix="!", intents=intents)
TOKEN = os.getenv("DISCORD_TOKEN")


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
            value=f"Client: {issue.client}\nAssigned to: {issue.assigned_to}\nStatus: {issue.status}\nType: {issue.type}\nDate: {issue.date}\nGroup: {issue.group}\nId: {issue.id}\n{issue.url}",
            inline=False,
        )
    return embed


@bot.command(name="ping", help="Responds with pong")
async def ping(ctx):
    await ctx.send("pong")


@bot.command(
    name="issues",
    help="!issues <user> (optional)",
)
async def allIssues(ctx, *args):
    monday = await check_server(ctx)
    if not monday:
        return
    user = args[0] if args else None
    data = monday.get_by_user(user) if user else monday.get_all_issues()
    await ctx.send(embed=embed_issues(data, user))


@bot.command(name="updateIssue", help="!updateIssue <id> <status>")
async def updateIssue(ctx, *args):
    monday = await check_server(ctx)
    if not monday:
        return
    id = args[0]
    value = args[1:]
    value = " ".join(value).lower().strip()
    status = {
        "working on it": 0,
        "done": 1,
        "stuck": 2,
    }[value]
    res = monday.update_issue(id, status)
    await ctx.send(res)


@bot.command(
    name="addGroup",
    help="!addGroup <board> <group> <name>",
)
async def addGroup(ctx, *args):
    board, group, name = args[0], args[1], args[2]
    server_id = ctx.message.guild.id
    res = add_group(server_id, board, group, name)
    if not res:
        return await ctx.send("Group already exists")
    return await ctx.send("Group added")


@bot.command(
    name="removeGroup",
    help="!removeGroup <board> <group>",
)
async def removeGroup(ctx, *args):
    board, group = args[0], args[1]
    server_id = ctx.message.guild.id
    res = remove_group(server_id, board, group)
    if not res:
        return await ctx.send("Group not found")
    return await ctx.send("Group removed")


@bot.command(
    name="groups",
    help="Shows all groups",
)
async def groups(ctx):
    server_id = ctx.message.guild.id
    groups = get_groups(server_id)
    if not groups:
        return await ctx.send("No groups found")
    embed = discord.Embed(title="Groups", description="All groups", color=0x266DD3)
    for group, index in zip(groups, range(len(groups))):
        embed.add_field(
            name=f"{index+1}. {group['name']}",
            value=f"Board: {group['board_id']}\nGroup: {group['group_id']}",
            inline=False,
        )
    return await ctx.send(embed=embed)


bot.run(TOKEN)
