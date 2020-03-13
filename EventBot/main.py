
import discord
from discord.ext import commands
from discord.utils import get
import asyncio
import pickle
import os
bot = commands.Bot(command_prefix='=', help_command=None)

class clsServer():
    """Stores information about the server the bot is running on, as well as bot settings"""
    def __init__(self):
        self.guild = bot.get_guild(114407194971209731)#114407194971209731
        self.token = 
        self.admin = "Admin"
        self.adminID = 114423908836442115
        self.bot = "Bot"
        self.botID = 141744010212409344
        self.adminChannel = ""
        self.teams = 3

class clsTeam():
    """Class that represents a single team"""
    def __init__(self):
        self.teamName = ""
        self.teamID = ""
        self.teamLeaderUser = ""
        self.teamLeaderID = ""
        self.generalChannel = ""
        self.responseChannel = ""
        self.announcementChannel = ""




server = clsServer()
teamDict = {}

if os.path.exists('teams'):
    try:
        filehandler = open('teams', 'rb') 
        object = pickle.load(filehandler)
    except:
        for x in range(server.teams):
            teamDict["Team-"+str(x)] = clsTeam()
            teamDict["Team-"+str(x)].teamName = "Team-"+str(x)
        filehandler = open('teams', 'wb')
        pickle.dump(teamDict, filehandler)
else:
    for x in range(server.teams):
        teamDict["Team-"+str(x)] = clsTeam()
        teamDict["Team-"+str(x)].teamName = "Team-"+str(x)
    filehandler = open('teams', 'wb')
    pickle.dump(teamDict, filehandler)

for team in teamDict:
    print(teamDict[team].teamName)

async def autosave():
    await bot.wait_until_ready()
    while not bot.is_closed():
        filehandler = open('teams', 'wb')
        pickle.dump(teamDict, filehandler)
        print("State saved")
        await asyncio.sleep(60)

@bot.command()
@commands.has_any_role(server.admin)
async def save(ctx,id):
    filehandler = open('teams', 'wb')
    pickle.dump(teamDict, filehandler)
    await ctx.send("State saved")

@bot.command()
@commands.has_any_role(server.admin)
async def delete(ctx):
    guild = ctx.message.guild
    for team in teamDict:
        announcementChannel = guild.get_channel(teamDict[team].announcementChannel)
        generalChannel = guild.get_channel(teamDict[team].generalChannel)
        responseChannel = guild.get_channel(teamDict[team].responseChannel)

        await announcementChannel.delete()
        await generalChannel.delete()
        await responseChannel.delete()

        teamID = guild.get_role(teamDict[team].teamID)
        leaderID = guild.get_role(teamDict[team].teamLeaderID)

        await teamID.delete()
        await leaderID.delete()

    await ctx.send("Deleted roles and channels")

@bot.command()
@commands.has_any_role(server.admin)
async def deleterole(ctx,id):
    guild = ctx.message.guild
    role = guild.get_role(id)
    await role.delete()

    await ctx.send("Deleted role")

@bot.command()
@commands.has_any_role(server.admin)
async def setteamnumber(ctx,arg):
    arg = int(arg)
    if arg > 0 and arg <= 10:
        server.teams = arg
        await ctx.send("Server team number set to" + str(arg))
    else:
        await ctx.send("Team number must be an integer greater than 1 and less than or equal to 10")

@bot.command()
@commands.has_any_role(server.admin)
async def publish(ctx,arg):
    guild = ctx.message.guild
    for team in teamDict:
        announcementChannel = guild.get_channel(teamDict[team].announcementChannel)
        await announcementChannel.send(arg)
    await ctx.message.channel.send("Message published to team announcement channels")

@bot.command()
@commands.has_any_role(server.admin)
async def generate(ctx):
    for team in teamDict:
        guild = ctx.message.guild
        memberrole = await guild.create_role(name=teamDict[team].teamName)
        teamDict[team].teamID = memberrole.id

        leaderrole = await guild.create_role(name=teamDict[team].teamName+"-leader")
        teamDict[team].teamLeaderID = leaderrole.id

        category = await guild.create_category_channel(teamDict[team].teamName)

        announcementchannel = await ctx.message.guild.create_text_channel(teamDict[team].teamName+"-announcements")
        await announcementchannel.set_permissions(guild.get_role(114423908836442115), read_messages=True, send_messages=True)
        await announcementchannel.set_permissions(memberrole, send_messages=False,read_messages=True)
        await announcementchannel.set_permissions(guild.get_role(141744010212409344), send_messages=True,read_messages=True)
        await announcementchannel.set_permissions(guild.default_role, send_messages=False,read_messages=False)
        await announcementchannel.set_permissions(guild.get_role(687811162804584465), send_messages=False,read_messages=False)
        await announcementchannel.set_permissions(guild.get_role(451457105145364480), send_messages=False,read_messages=False)
        await announcementchannel.edit(category=category)
        teamDict[team].announcementChannel = announcementchannel.id

        generalChannel = await ctx.message.guild.create_text_channel(teamDict[team].teamName+"-general")
        await generalChannel.set_permissions(guild.get_role(114423908836442115), read_messages=True, send_messages=True)
        await generalChannel.set_permissions(memberrole, send_messages=True,read_messages=True)
        await generalChannel.set_permissions(guild.get_role(141744010212409344), send_messages=True,read_messages=True)
        await generalChannel.set_permissions(guild.default_role, send_messages=False,read_messages=False)
        await generalChannel.set_permissions(guild.get_role(687811162804584465), send_messages=False,read_messages=False)
        await generalChannel.set_permissions(guild.get_role(451457105145364480), send_messages=False,read_messages=False)
        await generalChannel.edit(category=category)
        teamDict[team].generalChannel = generalChannel.id

        responseChannel = await ctx.message.guild.create_text_channel(teamDict[team].teamName+"-answers")
        await responseChannel.set_permissions(guild.get_role(114423908836442115), read_messages=True, send_messages=True)   #@Admin
        await responseChannel.set_permissions(memberrole, send_messages=False,read_messages=True)                           #Team member
        await responseChannel.set_permissions(leaderrole, send_messages=True,read_messages=True)                           #Leader role
        await responseChannel.set_permissions(guild.get_role(141744010212409344), send_messages=False,read_messages=True)   #Bot role
        await responseChannel.set_permissions(guild.default_role, send_messages=False,read_messages=False)                  #@everyone
        await responseChannel.set_permissions(guild.get_role(687811162804584465), send_messages=False,read_messages=False)  #ARG muted
        await responseChannel.set_permissions(guild.get_role(451457105145364480), send_messages=False,read_messages=False)  #Server mtued
        await responseChannel.edit(category=category)
        teamDict[team].responseChannel = responseChannel.id

        await ctx.message.channel.send("Roles and channels generated.")
        

owner = bot.get_user(226666366751604736)
guild = server.guild
@bot.event
async def on_ready():
    print('Logged in as:')
    print(bot.user.name)
    print(bot.user.id)
    print('-------------')
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("with secrets!"))
    bot.loop.create_task(autosave())
bot.run(server.token)
