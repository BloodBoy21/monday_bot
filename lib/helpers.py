from lib.supabase import supabase
from lib import monday
from dotenv import load_dotenv
import os

load_dotenv()
MONDAY_TOKEN = os.getenv("MONDAY_TOKEN")
SERVERS_CACHE = {}


async def check_server(ctx):
    server_id = ctx.message.guild.id
    if not is_in_cache(server_id):
        server = get_server(server_id)
        if not server:
            await ctx.send("Server not found")
            return None
    server = SERVERS_CACHE[server_id]
    new_monday = monday.Monday(MONDAY_TOKEN, server)
    return new_monday


def is_in_cache(server_id):
    return server_id in SERVERS_CACHE


def get_server(server_id):
    data, _ = supabase.table("servers").select("*").eq("server_id", server_id).execute()
    groups = data[1]
    if len(groups) == 0:
        return None
    SERVERS_CACHE[server_id] = groups
    return groups


def _groupExists(server, group_id, board):
    data, _ = (
        supabase.table("servers")
        .select("*")
        .eq("server_id", server)
        .eq("group_id", group_id)
        .eq("board_id", board)
        .execute()
    )
    groups = data[1]
    return len(groups) > 0


def add_group(server, board, group, name=None):
    if _groupExists(server, group, board):
        return
    data, _ = (
        supabase.table("servers")
        .insert(
            {"server_id": server, "board_id": board, "group_id": group, "name": name}
        )
        .execute()
    )
    return data


def remove_group(server, board, group):
    if not _groupExists(server, group, board):
        return
    data, _ = (
        supabase.table("servers")
        .delete()
        .eq("server_id", server)
        .eq("board_id", board)
        .eq("group_id", group)
        .execute()
    )
    return data[1]


def get_groups(server):
    data, _ = supabase.table("servers").select("*").eq("server_id", server).execute()
    groups = data[1]
    return groups
