import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from lib.helpers import check_server, add_group, remove_group, get_groups
from disputils import BotEmbedPaginator

load_dotenv()

intents = discord.Intents(
    messages=True, guilds=True, reactions=True, members=True, presences=True
)
bot = commands.Bot(command_prefix="!", intents=intents)
TOKEN = os.getenv("DISCORD_TOKEN")


def split_list(my_list, sublist_size=20):
    return [my_list[i : i + sublist_size] for i in range(0, len(my_list), sublist_size)]


def issue_list_embed(description):
    return discord.Embed(title="Issues", description=description, color=0x266DD3)


def embed_issues(issues, user=None):
    description = (
        "All issues from the team" if not user else f"All issues assigned to {user}"
    )
    embed = issue_list_embed(description)
    if not issues:
        embed.add_field(name="No issues found :)", value="Good job!", inline=False)
        return [embed]
    embed_issues = split_list(issues, 10)
    embed_list = list()
    issue_count = 0
    for issue_list in embed_issues:
        for issue in issue_list:
            issue_count += 1
            embed.add_field(
                name=f"{issue_count}. {issue.title}",
                value=issue.__str__(),
                inline=False,
            )
        embed_list.append(embed)
        embed = issue_list_embed(description)
    return embed_list


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
        return ctx.send("No monday board found. Please add one with !addBoard <board>")
    user = args[0] if args else None
    async with ctx.typing():
        data = await (monday.get_by_user(user) if user else monday.get_all_issues())
        embed_issues_list = embed_issues(data, user)
    paginator = BotEmbedPaginator(ctx, embed_issues_list)
    await paginator.run()


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
    try:
        board, group, name = args[0], args[1], " ".join(args[2:])
        if not name:
            raise Exception("No name provided")
        if not board or not group:
            raise Exception("Board or group not provided")
        server_id = ctx.message.guild.id
        res = add_group(server_id, board, group, name)
        if not res:
            return await ctx.send("Group already exists")
        return await ctx.send("Group added")
    except Exception as e:
        print(e)
        return await ctx.send(f"Error adding group: {str(e)}")


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


@bot.command(
    name="lsBoard",
    help="!lsBoard <board>",
)
async def lsBoard(ctx, *args):
    monday = await check_server(ctx)
    if not monday:
        return
    board = args[0]
    name, groups = monday.get_board_groups(board=board)
    if not groups:
        return await ctx.send("No groups found")
    embed = discord.Embed(
        title=f"{name} groups", description=f"All groups in {name}", color=0x266DD3
    )
    for group in groups:
        embed.add_field(
            name=f"{group['title']}",
            value=f"Id: {group['id']}",
            inline=False,
        )
    return await ctx.send(embed=embed)


@bot.command(
    name="group",
    help="!group <name> <user> (optional)",
)
async def group(ctx, *args):
    monday = await check_server(ctx)
    if not monday:
        return
    group = args[0]
    user = " ".join(args[1:]) if len(args) > 1 else None
    async with ctx.typing():
        data = await monday.get_group_issues(group, user)
        embed_issues_list = embed_issues(data)
    paginator = BotEmbedPaginator(ctx, embed_issues_list)
    await paginator.run()


bot.run(TOKEN)
