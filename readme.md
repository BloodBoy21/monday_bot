# Monday Bot 🤖
This is a Discord bot written in Python that can be used to get issues created in monday and listed using easy commands.

## Getting Started 🚀
1. Clone this repository.
2. Install the necessary dependencies by running pip install -r requirements.txt.
3. Create a new Discord application and bot account by following the instructions  [here](https://discordpy.readthedocs.io/en/stable/discord.html)
4. Copy the bot token and paste it into the .env file.
5. Invite the bot to your Discord server by following the instructions [here](https://discordpy.readthedocs.io/en/stable/discord.html#inviting-your-bot).
6. Run the bot by running python main.py in your terminal.

You can also run the bot using Docker. To do so, follow these steps:

1. Create a docker-compose.yml file with the following contents:

```yaml
version: '3.9'
services:
  monday-bot:
    image: bloodboy21/monday-bot:latest 
    environment:
      MONDAY_TOKEN: ''
      DISCORD_TOKEN: ''
      SUPABASE_PASSWORD: ''
      SUPABASE_URL: ''
      SUPABASE_KEY: ''
      MONDAY_HOST: ''
```

2. Replace the environment variables with your own values.
3. Run the bot by running ```sudo docker compose up```.


## Features 📋
This Discord bot currently supports the following commands:

- !addGroup: Add a group to board list to get issues.
- !group: Get all the issues in a group.
- !groups: Get all the groups in that are used to get issues.
- !issues: Get all issues created in monday.
- !lsBoard: Get all the groups in the board.
- !removeGroup: Remove a group from board list to get issues.
- !updateIssue: Update the status of an issue.

Additional features and commands can be added by modifying the main.py file.

## Configuration ⚙️
All configuration options for this Discord bot are stored in the .env file. The following environment variables are required:

- DISCORD_TOKEN: The bot token obtained from the Discord Developer Portal.
- MONDAY_TOKEN: The API token obtained from monday.com.
- SUPABASE_URL: The URL of the Supabase database.
- SUPABASE_KEY: The API key of the Supabase database.
- SUPABASE_PASSWORD: The password of the Supabase database.
- MONDAY_HOST: The host of the monday.com API.

## Supabase configuration 🗄️
This bot uses Supabase to store the groups that are used to get issues. To configure Supabase, follow these steps:

1. Create a new Supabase project.
2. Create a new table called issues.
3. Add the following columns to the issues table:
    - id: integer, primary key, auto increment
    - created_at: timestamp
    - issue_id: varchar
    - board: varchar
    - group: varchar
    - title: text
    - status: text
    - assigned_to: text
    - client: text
    - group_id: varchar
4. Create a new table called servers.
5. Add the following columns to the servers table:
    - id: integer, primary key, auto increment
    - created_at: timestamp
    - server_id: varchar
    - group_id: varchar
    - board_id: varchar
    - name: text
    - status_list: json

## Additional Information 📖
This bot uses the [discord.py](https://discordpy.readthedocs.io) library to interact with the Discord API and use python 3.9. It also uses the [monday API](https://monday.com/developers/v2) to get issues from monday.com.

You can edit the `issue class` in the monday.py file to add more fields to the issues table and the `__create_issue` method in the monday.py file to save your required fields in the database.

```python
class Issue:
    def __init__(self, data, title=None):
        self.title = title or data.get("name", "Sin título")
        self.client = data.get("client", "Sin cliente")
        self.assigned_to = data.get("asignado a", "Sin asignar")
        self.status = data.get("estado", "Sin estado")
        self.type = data.get("tipo", "Sin tipo")
        self.date = data.get("creation log", "Sin fecha")
        self.group = data.get("group", "Sin grupo")
        self.platform = data.get("plataforma", "Sin plataforma")
        self.resolution = data.get("fecha de resolución", "Sin resolver")
        self.id = data.get("id", "Sin id")
        self.board_id = data["board"]
        self.group_id = data["group_id"]
        self.__save_in_db()
        self.url = f"https://{MONDAY_HOST}/boards/{self.board_id}/pulses/{self.id}"
```
#### Please consider starring this repository if you found it useful ✨❤️ 
## Contributing 🤝
If you would like to contribute to this project, please fork the repository and submit a pull request with your changes.

## License 📄
This project is licensed under the MIT License.