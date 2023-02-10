import requests
from datetime import datetime
import os
from dotenv import load_dotenv
from lib.supabase import supabase

load_dotenv()
TOKEN = os.getenv("MONDAY_TOKEN")
MONDAY_HOST = os.getenv("MONDAY_HOST")


def _search_issue(issue_id):
    res, _ = supabase.table("issues").select("*").eq("issue_id", issue_id).execute()
    data = res[1]
    return data[0]


def _create_columns(columns):
    columns = {}
    for column in columns:
        title = column["title"].lower().strip()
        columns[title] = column["text"]
    return columns


class Issue:
    def __init__(self, data, title=None):
        self.title = title or data["title"]
        self.client = data["client"]
        self.assigned_to = data["asignado a"]
        self.status = data["estado"]
        self.type = data["tipo"]
        self.date = data["creation log"]
        self.group = data["group"] or "Sin grupo"
        self.platform = data["plataforma"] or "Sin plataforma"
        self.resolution = data["fecha de resolución"] or "Sin resolución"
        self.id = data["id"]
        self.board_id = data["board"]
        self.__save_in_db()
        self.url = f"https://{MONDAY_HOST}/boards/{self.board_id}/pulses/{self.id}"

    def __repr__(self) -> str:
        return f"\nIssue(\ntitle = {self.title}\nid={self.id}\nclient = {self.client}\nusers = {self.assigned_to}\nstatus = {self.status}\ntype = {self.type}\ndate = {self.date}\ngroup = {self.group})\n"

    def __str__(self) -> str:
        return f"**ID**: {self.id}\n**Client**: {self.client}\n**Assigned to**: {self.assigned_to}\n**Status**: {self.status}\n**Type**: {self.type}\n**Date**: {self.date}\n**Group**: {self.group}\n**Platform**: {self.platform}\n**Resolution**: {self.resolution}\n\n**URL**: {self.url}"

    def __save_in_db(self):
        exists = _search_issue(self.id)
        if exists:
            return
        supabase.table("issues").insert(
            {
                "issue_id": self.id,
                "title": self.title,
                "client": self.client,
                "assigned_to": self.assigned_to,
                "status": self.status,
                "group": self.group,
                "board": self.board_id,
            },
        ).execute()


class Monday:
    def __init__(self, api_key, server=[]):
        self.api_key = api_key
        self.base_url = "https://api.monday.com/v2/"
        self.groups = {}
        self.server = server

    def __get_all_issues(self, board_id, group_id):
        query = """
        {
          boards(ids: %s) {
          groups (ids: %s) {
            title 
            items { 
              name
              id 
              column_values {
                text
                title
                }
              }
            } 
          name
          }
        }
        """ % (
            board_id,
            group_id,
        )
        r = requests.post(
            self.base_url,
            json={"query": query},
            headers={"Authorization": self.api_key},
        )
        data = r.json()
        groups = data["data"]["boards"][0]["groups"]
        return self.__create_issues(groups, board_id)

    def get_all_issues(self):
        issues = []
        for board in self.server:
            issues += self.__get_all_issues(board["board_id"], board["group_id"])
        return issues

    def update_issue(self, issue_id, status):
        issue = _search_issue(issue_id)
        if not issue:
            return "Issue not found"
        query = (
            """mutation {change_simple_column_value(item_id: %s, board_id: %s, column_id: \"status\", value: \"%s\") {id name}}"""
            % (issue_id, issue["board"], str(status))
        )
        r = requests.post(
            self.base_url,
            json={"query": query},
            headers={"Authorization": self.api_key},
        )
        data = r.json()
        try:
            errors = data["errors"] or data["error_message"]
            print(errors)
        except KeyError:
            errors = None
        return "Issue updated successfully" if not errors else "Error updating issue"

    # TODO: Add custom method to get fields
    def __create_issues(self, groups, board_id=None):
        is_done = [
            "done",
            "terminado",
            "finalizado",
            "cerrado",
            "listo",
            "closed",
        ]
        for issue_group in groups:
            self.groups[issue_group["title"]] = []
            for item in issue_group["items"]:
                data = _create_columns(item["column_values"])
                title = item["name"]
                status = data["status"]
                group = issue_group["title"]
                if status.lower() in is_done:
                    continue
                data["id"] = item["id"]
                data["board"] = board_id
                data["group"] = group
                issue = Issue(title, data=data)
                self.groups[group] += [issue]
        return [issue for group in self.groups.values() for issue in group]

    def get_by_user(self, user):
        self.get_all_issues()
        issues = []
        for group in self.groups.values():
            for issue in group:
                includes_user = user.lower() in issue.assigned_to.lower()
                if not includes_user:
                    continue
                issues += [issue]
        return issues

    @staticmethod
    def get_board_groups(self, board):
        query = """{boards(ids: %s) {groups{ id title} name}}""" % board
        r = requests.post(
            self.base_url,
            json={"query": query},
            headers={"Authorization": self.api_key},
        )
        data = r.json()
        try:
            board_name = data["data"]["boards"][0]["name"]
            groups = data["data"]["boards"][0]["groups"]
            return board_name, groups
        except KeyError:
            return None, None
