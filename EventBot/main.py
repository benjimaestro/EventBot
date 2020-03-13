
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

class clsTeam():
    """Class that represents a single team"""
    def __init__(self):
        self.teamName = ""
        self.teamID = ""
        self.teamLeader = ""
        self.generalchannel = ""
        self.responseChannel = ""
        self.announcementChannel = ""




server = clsServer()
teamDict = {}

if os.path.exists('teams'):
    try:
        filehandler = open('teams', 'rb') 
        object = pickle.load(filehandler)
    except:
        for x in range(2):
            teamDict["Team-"+str(x)] = clsTeam()
            teamDict["Team-"+str(x)].teamName = "Team-"+str(x)
        filehandler = open('teams', 'wb')
        pickle.dump(teamDict, filehandler)
else:
    for x in range(2):
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
async def generatechannels(ctx,arg):
    botrole = ctx.message.guild.get_role(141744010212409344)
    channel = await ctx.message.guild.create_text_channel(arg)
    await channel.set_permissions(ctx.message.author, read_messages=True, send_messages=True)
    await channel.set_permissions(botrole, send_messages=True,read_messages=True)
    await channel.set_permissions(ctx.message.guild.default_role, send_messages=False,read_messages=False)
    await ctx.send(channel.id)

@bot.command()
@commands.has_any_role(server.admin)
async def generate(ctx):
    for team in teamDict:
        guild = ctx.message.guild
        memberrole = await guild.create_role(name=teamDict[team].teamName)
        teamDict[team].teamID = memberrole.id

        leaderrole = await guild.create_role(name=teamDict[team].teamName+"-leader")
        teamDict[team].teamID = memberrole.id

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

        generalchannel = await ctx.message.guild.create_text_channel(teamDict[team].teamName+"-general")
        await generalchannel.set_permissions(guild.get_role(114423908836442115), read_messages=True, send_messages=True)
        await generalchannel.set_permissions(memberrole, send_messages=True,read_messages=True)
        await generalchannel.set_permissions(guild.get_role(141744010212409344), send_messages=True,read_messages=True)
        await generalchannel.set_permissions(guild.default_role, send_messages=False,read_messages=False)
        await generalchannel.set_permissions(guild.get_role(687811162804584465), send_messages=False,read_messages=False)
        await generalchannel.set_permissions(guild.get_role(451457105145364480), send_messages=False,read_messages=False)
        await generalchannel.edit(category=category)
        teamDict[team].generalchannel = generalchannel.id

        submissionchannel = await ctx.message.guild.create_text_channel(teamDict[team].teamName+"-answers")
        await submissionchannel.set_permissions(guild.get_role(114423908836442115), read_messages=True, send_messages=True)   #@Admin
        await submissionchannel.set_permissions(memberrole, send_messages=False,read_messages=True)                           #Team member
        await submissionchannel.set_permissions(leaderrole, send_messages=False,read_messages=True)                           #Leader role
        await submissionchannel.set_permissions(guild.get_role(141744010212409344), send_messages=False,read_messages=True)   #Bot role
        await submissionchannel.set_permissions(guild.default_role, send_messages=False,read_messages=False)                  #@everyone
        await submissionchannel.set_permissions(guild.get_role(687811162804584465), send_messages=False,read_messages=False)  #ARG muted
        await submissionchannel.set_permissions(guild.get_role(451457105145364480), send_messages=False,read_messages=False)  #Server mtued
        await submissionchannel.edit(category=category)
        teamDict[team].submissionchannel = submissionchannel.id
        

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
