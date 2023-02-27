import json
from pytz import timezone
from datetime import datetime
from os import getenv, listdir
from os.path import isdir
from dotenv import load_dotenv

from discord import Status, Intents, SlashCommandGroup, ApplicationContext, AutocompleteContext, File, Member, utils
from discord.ext import commands
from discord.commands import option
from discord.ext.commands import RoleNotFound
from discord.errors import ExtensionNotLoaded, ExtensionNotFound, ExtensionAlreadyLoaded


# identifiant des serveurs discord où seront créées les commandes d'application
guild_ids = [
    # 733722460771581982,
    747064216447352854
]


def get_parameter(param: str):
    with open("config.json", "r", encoding="utf-8") as config_file:
        config = json.load(config_file)
    try:
        return config[param]
    except KeyError:
        return "KeyError"


def time_now():
    """Simple commande renvoyant un objet au format datetime.datetime correspondant à la date et à l'heure
    d'appel de la fonction à Paris"""
    return datetime.now(tz=timezone("Europe/Paris"))


def log_action(file_name: str, txt: str):
    with open(f"logs/{file_name}.log", "a", encoding="utf-8") as log_file:
        log_file.write(f"{time_now().strftime('[%d-%m-%Y][%H:%M:%S]')}{txt}\n")


class MyBot(commands.Bot):
    """ A slightly modified version of commands.Bot"""
    def __init__(self):
        with open("config.json", "r") as f:
            config = json.load(f)
            prefix = config["prefix"]
            owners = config['owner_ids']

        intents = Intents.all()
        super().__init__(
            command_prefix=commands.when_mentioned_or(prefix),
            intents=intents,
            owner_ids=owners,
            debug_servers=[
                # 733722460771581982,
                747064216447352854
            ]
        )
        self.remove_command("help")
        self.log_file_name = time_now().strftime('%d-%m-%Y_%H.%M.%S')

        for filename in listdir('./cogs'):
            if filename.endswith('.py'):
                self.load_extension(f"cogs.{filename[:-3]}")

    async def on_ready(self):
        start_msg = f"[STATUS] Bot connecté en tant que {bot.user}"
        print(f"\033[0;34m[{time_now().strftime('%d-%m-%Y][%H:%M:%S')}]{start_msg}\033[0m")
        log_action(file_name=self.log_file_name, txt=start_msg)
        await self.change_presence(status=Status.idle)


bot = MyBot()

# Creating a slash command group for all admin commands
admin_group = SlashCommandGroup("admin", "Commandes réservées à l'administrateur du bot")


@admin_group.command(name="clear", description="Administrateur seulement", guild_ids=guild_ids)
@option(name="amount", description="The amount of message you want to delete")
@commands.has_permissions(manage_messages=True)
async def admin_clear(ctx: ApplicationContext, amount: int):
    await ctx.channel.purge(limit=amount)
    log_msg = f"[CMD] {ctx.author} has deleted {amount} messages in {ctx.channel.id}"
    log_action(file_name=bot.log_file_name, txt=log_msg)
    await ctx.respond(f"> {amount} messages have been deleted !", ephemeral=True)


async def cog_autocomplete(ctx: AutocompleteContext):
    search = ctx.options['cog']
    cogs = [filename[:-3] for filename in listdir('./cogs') if filename.endswith('.py') and search in filename]
    return cogs if cogs else ["Nothing found"]


@admin_group.command(name="reload", description="Administrateur seulement", guild_ids=guild_ids)
@option(name="cog", description="The cog you want to reload", autocomplete=cog_autocomplete)
async def admin_reload(ctx: ApplicationContext, cog: str):
    if ctx.author.id not in bot.owner_ids:
        await ctx.respond("> This command is for bot administrators only !", ephemeral=True)
        return
    try:
        bot.reload_extension(f"cogs.{cog}")
        log_msg = f"[COG] '{cog}' cog reloaded by {ctx.author}"
        print(f"\033[0;33m[{time_now().strftime('%d-%m-%Y][%H:%M:%S')}]{log_msg}\033[0m")
        log_action(bot.log_file_name, log_msg)
        await ctx.respond(f"> Cog `{cog}` reloaded", ephemeral=True)

    except ExtensionNotLoaded:
        try:
            bot.load_extension(f"cogs.{cog}")
            log_msg = f"[COG] '{cog}' cog loaded by {ctx.author}"
            print(f"\033[0;33m[{time_now().strftime('%d-%m-%Y][%H:%M:%S')}]{log_msg}\033[0m")
            log_action(bot.log_file_name, log_msg)
            await ctx.respond(f"> Cog `{cog}` loaded", ephemeral=True)

        except ExtensionNotFound:
            await ctx.respond("> Unknown cog", ephemeral=True)


@admin_group.command(name="load", description="Administrateur seulement", guild_ids=guild_ids)
@option(name="cog", description="The cog you want to reload", autocomplete=cog_autocomplete)
async def admin_load(ctx: ApplicationContext, cog: str):
    if ctx.author.id not in bot.owner_ids:
        await ctx.respond("> This command is for bot administrators only !", ephemeral=True)
        return
    try:
        bot.load_extension(f"cogs.{cog}")
        log_msg = f"[COG] '{cog}' cog loaded by {ctx.author}"
        print(f"\033[0;33m[{time_now().strftime('%d-%m-%Y][%H:%M:%S')}]{log_msg}\033[0m")
        log_action(file_name=bot.log_file_name, txt=log_msg)
        await ctx.respond(f"> Cog `{cog}` loaded", ephemeral=True)

    except ExtensionAlreadyLoaded:
        await ctx.respond("Cog already loaded", ephemeral=True)

    except ExtensionNotFound:
        await ctx.respond("Unknown cog", ephemeral=True)


@admin_group.command(name="unload", description="Administrateur seulement", guild_ids=guild_ids)
@option(name="cog", description="The cog you want to reload", autocomplete=cog_autocomplete)
async def admin_unload(ctx: ApplicationContext, cog: str):
    if ctx.author.id not in bot.owner_ids:
        await ctx.respond("> This command is for bot administrators only !", ephemeral=True)
        return
    try:
        bot.reload_extension(f"cogs.{cog}")
        log_msg = f"[COG] '{cog}' cog unloaded by {ctx.author}"
        print(f"\033[0;33m[{time_now().strftime('%d-%m-%Y][%H:%M:%S')}]{log_msg}\033[0m")
        log_action(bot.log_file_name, log_msg)
        await ctx.respond(f"> Cog `{cog}` reloaded", ephemeral=True)

    except ExtensionNotLoaded:
        await ctx.respond("> Unknown cog or cog not loaded", ephemeral=True)


async def directory_autocomplete(ctx: AutocompleteContext):
    directories = ['.']
    search = ctx.options['directory']
    ignored_directories = get_parameter('ignored_directories')
    for item in listdir('./'):
        if isdir(item) and item not in ignored_directories and search in item:
            directories.append(item)

    # directories.remove('logs')
    return directories if directories else ["Nothing found"]


async def filename_autocomplete(ctx: AutocompleteContext):
    directory = ctx.options['directory']
    search = ctx.options['filename']
    files = []
    for item in listdir(f"{directory}/"):
        if not isdir(item) and search in item:
            files.append(item)
    return files if files else ["Nothing found"]


@admin_group.command(name="download", description="Administrateur seulement", guild_ids=guild_ids)
@option(name="directory", description="The directory of the file.", autocomplete=directory_autocomplete)
@option(name="filename", description="The targeted file", autocomplete=filename_autocomplete)
async def download_file(ctx: ApplicationContext, directory: str, filename: str):
    if ctx.author.id not in bot.owner_ids:
        await ctx.respond("> This command is for bot administrators only !", ephemeral=True)
        return
    if directory in get_parameter('ignored_directories'):
        await ctx.respond("> Access denied !", ephemeral=True)

    else:
        try:
            log_msg = f"[DOWNLOAD] '{directory}/{filename}' has been downloaded by {ctx.author}"
            log_action(file_name=bot.log_file_name, txt=log_msg)
            await ctx.respond(file=File(fp=f"{directory}/{filename}", filename=filename), ephemeral=True)

        except Exception as e:
            await ctx.respond(e, ephemeral=True)


@admin_group.command(name="op", description="Administrateur seulement", guild_ids=guild_ids)
@option(name="user", description="The targeted user", type=Member)
async def admin_op(ctx: ApplicationContext, user: Member):
    if ctx.author.id not in bot.owner_ids:
        await ctx.respond("> This command is for bot administrators only !", ephemeral=True)
        return
    if not user:
        await ctx.respond("Please specify a user")
        return

    with open("config.json", "r", encoding="utf-8") as config_file:
        config = json.load(config_file)

    guild = bot.get_guild(config['guild_id'])
    admin_role = config['roles'][config['current_year']]['OP']
    role = utils.get(guild.roles, id=admin_role)

    try:
        await user.add_roles(role)
        await user.send("Done")
        log_msg = f"[CMD] {ctx.author} has received 'op' role"
        log_action(file_name=bot.log_file_name, txt=log_msg)
    except RoleNotFound:
        await ctx.author.send(f"> Le rôle <@&{admin_role}> n'existe pas/plus.")


@admin_group.command(name="shutdown", description="Administrateur seulement", guild_ids=guild_ids)
async def admin_shutdown(ctx: ApplicationContext):
    if ctx.author.id not in bot.owner_ids:
        await ctx.respond("> This command is for bot administrators only !", ephemeral=True)
        return
    await ctx.respond("Closing bot !", ephemeral=True)
    log_msg = f"[STATUS] Bot stopped by {ctx.author}"
    log_action(file_name=bot.log_file_name, txt=log_msg)
    await bot.close()


#########################################

if __name__ == "__main__":
    load_dotenv()
    bot.add_application_command(admin_group)
    bot.run(getenv("TOKEN"))
