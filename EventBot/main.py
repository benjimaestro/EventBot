
import discord
from discord.ext import commands
from discord.utils import get
import asyncio
import pickle
import os
import random
import pprint
import time
bot = commands.Bot(command_prefix='=', help_command=None)

class clsServer():
    """Stores information about the server the bot is running on, as well as bot settings"""
    def __init__(self):
        self.guild = bot.get_guild(114407194971209731)#114407194971209731
        self.token = open("key.txt", "r").read()
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
        self.vote = {"timestamp":0,"type":"votekick","status":"failed","targetID":0,"messageID":0,"channelID":0}
        self.mutes = []
    def export(self):
        return {"teamName":self.teamName,
                "teamID":self.teamID,
                "teamLeaderUser":self.teamLeaderUser,
                "teamLeaderID":self.teamLeaderID,
                "generalChannel":self.generalChannel,
                "responseChannel":self.responseChannel,
                "announcementChannel":self.announcementChannel,
                "vote":self.vote,
                "mutes":self.mutes}
    def importTeam(self,imported):
        self.teamName = imported["teamName"]
        self.teamID = imported["teamID"]
        self.teamLeaderUser = imported["teamLeaderUser"]
        self.teamLeaderID = imported["teamLeaderID"]
        self.generalChannel = imported["generalChannel"]
        self.responseChannel = imported["responseChannel"]
        self.announcementChannel = imported["announcementChannel"]
        self.vote = {"timestamp":0,"type":"votekick","status":"failed","targetID":0,"messageID":0,"channelID":0}#imported["vote"]
        self.mutes = imported["mutes"]




server = clsServer()
teamDict = {}
pickleDump = {}

if os.path.exists('teams'):
    try:
        with open("teams", "rb") as f:
            pickleDump = pickle.load(f)
            for key in pickleDump:
                teamDict[key] = clsTeam()
                teamDict[key].importTeam(pickleDump[key])
    except Exception as e:
        for x in range(server.teams):
            teamDict["Team-"+str(x)] = clsTeam()
            teamDict["Team-"+str(x)].teamName = "Team-"+str(x)
            pickleDump["Team-"+str(x)] = teamDict["Team-"+str(x)].export()
        with open("teams", "wb") as f:
            pickle.dump(pickleDump, f)
        print("ERROR",e)
else:
    for x in range(server.teams):
        teamDict["Team-"+str(x)] = clsTeam()
        teamDict["Team-"+str(x)].teamName = "Team-"+str(x)
        pickleDump["Team-"+str(x)] = teamDict["Team-"+str(x)].export()
    with open("teams", "wb") as f:
        pickle.dump(pickleDump, f)

print(pickleDump)

async def autosave():
    await bot.wait_until_ready()
    while not bot.is_closed():
        for x in range(server.teams):
            if teamDict["Team-"+str(x)].vote["status"] == "active":
                message = await bot.get_channel(teamDict["Team-"+str(x)].vote["channelID"]).fetch_message(teamDict["Team-"+str(x)].vote["messageID"])
                
                if (int(time.time()) - teamDict["Team-"+str(x)].vote["timestamp"]) > 600:
                    yes = -1
                    no = -1
                    teamSize = len(bot.get_role(teamDict["Team-"+str(x)].teamID))

                    if teamDict["Team-"+str(x)].vote["type"] == 'votekick':
                        required = round((teamSize/100)*60)
                    else:
                        required = round((teamSize/100)*75)

                    for reaction in message.reactions:
                        if reaction == '✅':
                            yes += 1
                        if reaction == '❌':
                            no += 1
                    print("YES:",str(yes))
                    print("NO:",str(no))
                    print("REQUIRED:",str(required))
                    if yes >= required and yes >= teamSize/2:
                        if teamDict["Team-"+str(x)].vote["type"] == 'votekick':
                            guild = bot.get_guild(114407194971209731)
                            user = guild.get_member(teamDict["Team-"+str(x)].vote["targetID"])
                            role = guild.get_role(teamDict["Team-"+str(x)].teamID)
                            await bot.remove_roles(user, role)
                        else:
                            pool = []
                            guild = bot.get_guild(114407194971209731)
                            user = guild.get_member(teamDict["Team-"+str(x)].teamLeaderUser)
                            leaderRole = guild.get_role(teamDict["Team-"+str(x)].teamLeaderID)
                            memberRole = guild.get_role(teamDict["Team-"+str(x)].teamID)
                            for member in guild.members:
                                for role in member.roles:
                                    if role.id == memberRole.id:
                                        print(member)
                                        pool.append(member)

                            newLeader = random.choice(pool)
                            await newLeader.add_roles(leaderRole)
                            teamDict["Team-"+str(x)].teamLeaderUser = newLeader.id
                            channel = guild.get_channel(teamDict["Team-"+str(x)].generalChannel)
                            await channel.send("Vote results: YES wins")
                            await channel.send(" was set as leader")

                    else:
                        channel = guild.get_channel(teamDict["Team-"+str(x)].generalChannel)
                        await channel.send("Vote results: NO wins")
                    teamDict["Team-"+str(x)].vote["status"] = "finished"

        for x in range(server.teams):
            pickleDump["Team-"+str(x)] = teamDict["Team-"+str(x)].export()
        with open("teams", "wb") as f:
            pickle.dump(pickleDump, f)
        print("State saved")

        await asyncio.sleep(10)

@bot.command()
@commands.has_any_role(server.admin)
async def save(ctx,id):
    filehandler = open('teams', 'wb')
    pickle.dump(teamDict, filehandler)
    await ctx.send("State saved")

@bot.command()
async def votekick(ctx,arg):
    guild = ctx.message.guild
    kickMember = guild.get_member(int(arg[3:-1]))
    for role in ctx.message.author.roles:
        if "leader" in role.name and ctx.message.author.id != kickMember.id:
            team = "Team-"+role.name.split("-")[1]
            if (time.time() - teamDict[team].vote["timestamp"]) > 3600:
                await ctx.send(kickMember.mention)
                embed = discord.Embed(title=team + " vote", description="Votekicking "+kickMember.mention +". Requires at least 50% of the team to vote and at least 60% of votes need to be yes to kick.", color=0xff0000)
                message = await ctx.message.channel.send(embed=embed)
                teamDict[team].vote = {"timestamp":int(time.time()),"type":"votekick","status":"active","targetID":kickMember.id,"messageID":message.id,"channelID":ctx.channel.id}
            else:
                await ctx.send("You must wait at least an hour after the last vote to start another!")

@bot.command()
async def mutiny(ctx):
    guild = ctx.message.guild
    kickMember = guild.get_member(int(arg[3:-1]))
    for role in ctx.message.author.roles:
        if "team" in role.name:
            team = "Team-"+role.name.split("-")[1]
            if (time.time() - teamDict[team].vote["timestamp"]) > 3600:
                await ctx.send(kickMember.mention)
                embed = discord.Embed(title=team + " vote", description="The team has declared mutiny! If this passes, the team leader will be removed and another member will be given the role at random. Requires at least 50% of the team to vote and at least 75% of votes need to be yes to kick.", color=0xff0000)
                message = await ctx.message.channel.send(embed=embed)
                teamDict[team].vote = {"timestamp":int(time.time()),"type":"votekick","status":"active","targetID":kickMember.id,"messageID":message.id,"channelID":ctx.channel.id}
            else:
                await ctx.send("You must wait at least an hour after the last vote to start another!")

@bot.command()
@commands.has_any_role(server.admin)
async def teaminfo(ctx,arg):
    await ctx.send(str(teamDict[arg].export()))

@bot.command()
@commands.has_any_role(server.admin)
async def rolemembers(ctx,arg):
    arg = int(arg)
    guild = ctx.message.guild
    role = guild.get_role(687814139065925647)
    memberList = []
    if role is None:
        await ctx.send('There is no participant role!')
        return
    empty = True
    for member in guild.members:
        if role in member.roles:
            #await ctx.send("{0.name}: {0.id}".format(member))
            empty = False
            memberList.append(member)
    if empty:
        pass
        #await ctx.send("Nobody has the role {}".format(role.mention))
    random.shuffle(memberList)

    def chunks(lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]
    memberListSplit = list(chunks(memberList, arg))
    x = 0
    for team in memberListSplit:
        output = ""
        output += "Team "+str(x)+"\n"
        x += 1
        for member in team:
            output += "{0.name}: {0.id}".format(member) + "\n"
        await ctx.send(output)

@bot.command()
@commands.has_any_role(server.admin)
async def setleader(ctx,arg):
    pool = []
    guild = bot.get_guild(114407194971209731)
    #user = guild.get_member(int(arg[3:-1]))
    leaderRole = guild.get_role(teamDict[arg].teamLeaderID)
    memberRole = guild.get_role(teamDict[arg].teamID)
    await ctx.send(str(leaderRole.id)+ " " +str(memberRole.id))
    for member in guild.members:
        for role in member.roles:
            if role.id == memberRole.id:
                print(member)
                pool.append(member)

    newLeader = random.choice(pool)
    await newLeader.add_roles(leaderRole)
    teamDict[arg].teamLeaderUser = newLeader.id
    await ctx.send(str(newLeader.id) + " was set as leader")

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
