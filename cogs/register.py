from discord import Embed, Member, utils, AutocompleteContext
from discord.ext import commands
from discord.commands import option
from discord.ext.commands.errors import RoleNotFound

import json

import main
from main import time_now, log_action, get_parameter, is_owner

# identifiants des comptes autorisés à utiliser les commandes administratives
admin_ids = [444504367152889877, 357202046581080067, 474220078766751774]


def user_is_allowed(ctx):
    """
    Fonction vérifiant si l'utilisateur est autorisé à utilisé cette commande
    """
    return ctx.author.id in admin_ids


async def lastname_autocomplete(ctx: AutocompleteContext):
    lastnames = []
    with open("json/students.json", "r", encoding="utf-8") as student_file:
        students = json.load(student_file)

    for student_id in students:
        lastname = students[student_id]['lastname']
        if lastname not in lastnames:
            lastnames.append(lastname)
    return lastnames


async def firstname_autocomplete(ctx: AutocompleteContext):
    lastname = ctx.options['lastname']
    firstnames = []
    with open("json/students.json", "r", encoding="utf-8") as student_file:
        students = json.load(student_file)

    for student_id in students:
        if students[student_id]['lastname'] == lastname:
            firstnames.append(students[student_id]['firstname'])

    return firstnames


class Register(commands.Cog):
    def __init__(self, client: main.MyBot):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        log_msg = f"[COG] '{self.__cog_name__}' cog loaded"
        print(f"\033[0;33m[{time_now().strftime('%d-%m-%Y][%H:%M:%S')}]{log_msg}\033[0m")
        log_action(file_name=self.client.log_file_name, txt=log_msg)

    @commands.command(name="op", description="Met un rôle avec les permissions administrateurs à un utilisateur", brief="Give a role with administrator permission to a user")
    async def set_administrator(self, ctx, user: Member = None):
        if not user:
            await ctx.reply("Please specify a user")
            return

        with open("config.json", "r", encoding="utf-8") as config_file:
            config = json.load(config_file)

        guild = self.client.get_guild(config['guild_id'])
        admin_role = config['roles'][config['current_year']]['OP']
        role = utils.get(guild.roles, id=admin_role)

        try:
            await user.add_roles(role)
            await user.send("Done")
            log_msg = f"[CMD] {ctx.author} has received 'op' role"
            log_action(file_name=self.client.log_file_name, txt=log_msg)
        except RoleNotFound:
            await ctx.author.send(f"> Le rôle <@&{admin_role}> n'existe pas/plus.")
#

    @commands.command(pass_context=True)
    @commands.is_owner()
    async def tuto(self, ctx):
        desc = "Bienvenue sur ce serveur ! Si vous êtes ici c'est que vous avez <@474220078766751774> en tant que professeur. Pour réduire le temps avant que puissiez accéder au contenu qui vous est réservé et simplifier la reconnaissance de chacun, le <@876634931911098398> se chargera de vous attribuer les rôles qui vous reviennent. \n\nPour obtenir vos rôles, il suffit d'exécuter la commande \n`/register [nom_de_famille] [prenom]` ci-dessous. Veuillez toutefois noter qu'il faut respecter quelques règles : \n- pas de majuscules \n- pas de caractères spéciaux (remplacez les `é` par des `e`) \n- pour les noms composés, remplacez les espaces par des tirets (`-`) \n\nEn cas de problème quelconque, n'hésitez pas à contacter <@444504367152889877>.\n\u200b"
        emb = Embed(color=0xf5b04c, description=desc)
        emb.set_author(name="Made by Lionceot#6962", url="https://discord.gg/3knPcHE2yt", icon_url="https://cdn.discordapp.com/attachments/876897530867236884/943879217786011698/classbot-pp-square.png")
        emb.set_footer(text="『 Tutoriel 』     『 ClassBot 』•『 v2.0 』")
        emb.set_thumbnail(url="https://cdn.discordapp.com/attachments/876897530867236884/943879217786011698/classbot-pp-square.png")
        await ctx.send(embed=emb)

    #
    @commands.slash_command(name="register", description="Attribue les rôles et renomme l'élève selon la liste.", brief="Rename et give roles to the student according to the list", guild_ids=[747064216447352854])
    @option(name="lastname", description="Votre nom de famille", autocomplete=lastname_autocomplete)
    @option(name="firstname", description="Votre prénom")
    @option(name="user", description="Administrateur seulement", type=Member, required=False)
    @commands.check(is_owner)
    async def register(self, ctx, lastname: str, firstname: str, user: Member = None):
        if not user or (user and not user_is_allowed(ctx)):
            user = ctx.author

        member = await commands.MemberConverter().convert(ctx, str(user.id))
        guild = self.client.get_guild(get_parameter('guild_id'))

        with open("json/linked_accounts.json", "r", encoding="utf-8") as link_file:
            linked_accounts = json.load(link_file)

        with open("json/students.json", "r", encoding="utf-8") as student_file:
            students = json.load(student_file)

        if str(user.id) in linked_accounts:
            student_id = linked_accounts[str(user.id)]
            student_info = students[student_id]

            lastname = student_info['lastname']
            firstname = student_info['firstname']
            groups = student_info['groups']

            nick = f"{firstname} {lastname}".title()

            for role_id in groups:
                role = utils.get(guild.roles, id=role_id)
                await member.add_roles(role)

            await member.edit(nick=nick)
            await ctx.respond("Vos rôles vous ont été attribués !", ephemeral=True)

            ds_start = "\🔗 ❱❱"
            file_start = "[REGISTER] 🔗"
            log_msg = f" {user.mention} ▬ `{nick} - {' '.join(groups)}` ({user.id})"

            log_action(file_name=self.client.log_file_name, txt=file_start + log_msg)
            log_channel = self.client.get_channel(get_parameter('log_channel'))
            await log_channel.send(ds_start +log_msg)

        else:
            for student_id in students:
                if student_id in linked_accounts.values():
                    continue

                elif students[student_id]['lastname'] == lastname and students[student_id]['firstname']:
                    student_info = students[student_id]

                    lastname = student_info['lastname']
                    firstname = student_info['firstname']
                    groups = student_info['groups']

                    nick = f"{firstname} {lastname}".title()

                    for role_id in groups:
                        role = utils.get(guild.roles, id=role_id)
                        await member.add_roles(role)

                    await member.edit(nick=nick)
                    await ctx.respond("Vos rôles vous ont été attribués !", ephemeral=True)

                    with open("json/linked_accounts.json", "w", encoding="utf-8") as link_file:
                        linked_accounts[user.id] = student_id
                        json.dump(linked_accounts, link_file, indent=2)

                    ds_start = "\🆕 ❱❱"
                    file_start = "[REGISTER] 🆕"
                    log_msg = f" {user.mention} ▬ `{nick} - {' '.join(groups)}` ({user.id})"

                    log_action(file_name=self.client.log_file_name, txt=file_start + log_msg)
                    log_channel = self.client.get_channel(get_parameter('log_channel'))
                    await log_channel.send(ds_start + log_msg)
                    break

            else:
                emergency_contact = self.client.get_user(get_parameter('emergency_contact')).mention
                await ctx.respond(f"L'élève {firstname.title()} {lastname.title()} n'a pas été trouvé ou est déjà "
                                  f"présent sur le serveur. S'il s'agit d'une erreur, contactez {emergency_contact}.",
                                  ephemeral=True)


def setup(client):
    client.add_cog(Register(client))
