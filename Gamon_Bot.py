# -*- coding: utf-8 -*-
# Work with Python 3.6
import random
import asyncio
from discord import Game
from discord.ext.commands import Bot
from datetime import datetime, time
from io import BytesIO
import requests
import pandas as pd
from collections import Counter
from ascii_graph import Pyasciigraph
import discord
import feedparser
import pickle
from discord.ext.commands import CommandNotFound
import operator

# Channel in news_update and token need to be changed when testing.
BOT_PREFIX = ("?", "!")
TOKEN = '' # 

client = Bot(command_prefix=BOT_PREFIX)
# Read in lists
global black_list
try:
    with open ('blacklist_file', 'rb') as fp:
        black_list = pickle.load(fp)
    print("[" + datetime.now().strftime('%H:%M:%S') + "] " + "Read blacklist from file.")
except:
    black_list = {}
    print("[" + datetime.now().strftime('%H:%M:%S') + "] " + "Created new blacklist.")

global bounty_list
try:
    with open ('bounty_file', 'rb') as fp:
        bounty_list = pickle.load(fp)
    print("[" + datetime.now().strftime('%H:%M:%S') + "] " + "Read bounty list from file.")
except:
    bounty_list = {}
    print("[" + datetime.now().strftime('%H:%M:%S') + "] " + "Created new bounty list.")

# Bot Commands
@client.command(name="commands",
                description="Display all commands.",
                brief="Display all commands.")
async def commands(ctx):
    # Display the full list of commands
    await ctx.send('''The following commands are available:
    `!8ball` Shake the magic eight ball to see what the future holds.
    
    `!roll` Roll a random number between 1-100.
    
    `!specinfo` Displays numbers of each spec of every class.
    `!specinfo <class>` Displays numbers of each spec for a specific class.
    
    `!roleinfo` Displays numbers of each role of every class.
    `!roleinfo <class>` Displays numbers of each role for a specific class.
    
    `!profinfo` Displays numbers of each profession.
    `!profinfo <60/leveling>` Displays numbers of each profession either at level 60 or while leveling.
    `!profinfo <60/leveling> <profession name>` Displays which members have a specific profession either at level 60 or while leveling.
    
    `!classinfo` Displays numbers of each class.
       
    `!attendance <player name>` Displays current raid attendance for a specific player.
    
    `!news <number>` Displays the last <number> Classic articles from Wowhead. Default is last 3 articles.
    
    `!phases` Information on the Classic content schedule.
    
    `!recruitment` Example recruitment messages.
    
    `!raidtimes` Information on raid times.
    
    `!blacklist` List of blacklisted players.
    `!blacklist add <name>` Add a player to the blacklist.
    `!blacklist add <name> <reason>` Add a player to the blacklist with a reason for their listing. The reason must be in quotation marks.
    `!blacklist rm <name>` Remove a player from the blacklist.
    
    `!bounties` List of current bounties on players and rewards for their demise.
    `!bounties add <name> <reward>` Add a player to the bounty list and a reward for their death.
    `!bounties rm <name>` Remove a player from the bounty list.
    ''')

@client.command(name='8ball',
                description="Answers a yes/no question.",
                brief="Answers from the beyond.",
                aliases=['eight_ball', 'eightball', '8-ball'],
                pass_context=True)
async def eight_ball(context):
    # List of possible responses.
    possible_responses = [
        'That is a resounding no',
        'It is not looking likely',
        'Too hard to tell',
        'It is quite possible',
        'Definitely',
        'Only if you wish hard enough'
    ]
    # Display a random value from the responses list
    await context.send(random.choice(possible_responses) + ", " + context.message.author.mention)


@client.command(name='countdown',
                description = 'Displays the time until classic release.',
                brief = 'Countdown to classic release.')
async def countdown(ctx):
    # Count down the time remaining until Classic release.
    def dateDiffInSeconds(date1, date2):
        timedelta = date2 - date1
        return timedelta.days * 24 * 3600 + timedelta.seconds
    
    def daysHoursMinutesSecondsFromSeconds(seconds):
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        if days > 0:
            return (days, hours, minutes, seconds)
        else:
            if hours > 0:
                return (hours, minutes, seconds)
            else:
                if minutes > 0:
                    return (minutes, seconds)
                elif seconds > 0:
                    return(seconds)
                else:
                    return('done')
    
    leaving_date = datetime.strptime('2019-08-26 23:00:00', '%Y-%m-%d %H:%M:%S')
    now = datetime.now()
    
    # Format the string and post to the channel
    if len(daysHoursMinutesSecondsFromSeconds(dateDiffInSeconds(now, leaving_date))) == 4:
        await ctx.send("Time until Classic release: %d days, %d hours, %d minutes, %d seconds." % daysHoursMinutesSecondsFromSeconds(dateDiffInSeconds(now, leaving_date)))
    elif len(daysHoursMinutesSecondsFromSeconds(dateDiffInSeconds(now, leaving_date))) == 3:
        await ctx.send("Time until Classic release: %d hours, %d minutes, %d seconds." % daysHoursMinutesSecondsFromSeconds(dateDiffInSeconds(now, leaving_date)))
    elif len(daysHoursMinutesSecondsFromSeconds(dateDiffInSeconds(now, leaving_date))) == 2:
        await ctx.send("Time until Classic release: %d minutes, %d seconds." % daysHoursMinutesSecondsFromSeconds(dateDiffInSeconds(now, leaving_date)))
    elif len(daysHoursMinutesSecondsFromSeconds(dateDiffInSeconds(now, leaving_date))) == 1:
        await ctx.send("Time until Classic release: %d seconds." % daysHoursMinutesSecondsFromSeconds(dateDiffInSeconds(now, leaving_date)))
    elif daysHoursMinutesSecondsFromSeconds(dateDiffInSeconds(now, leaving_date)) == 'done':
        await ctx.send("Stop typing countdown. It's over. We've made it.")


@client.command(name='roll',
                description = 'Roll a number between 1-100.',
                brief = 'Roll a number between 1-100',
                pass_context=True)
async def roll(ctx):
    # Generates a random number between 1-100
    # Post the random number to the channel    
    await ctx.send(ctx.message.author.mention + " rolls " + str(random.randint(1, 100)) )
    
@client.command(name='updatetable',
                description="Updates Gamon's version of the roster table spreadsheet.",
                brief="Update the roster table",
                pass_context=True)
async def updatetable(ctx):
    # Read the guild's Google Sheet into a Pandas dataframe and set it as a global variable
    r = requests.get('sheetname')
    data = r.content
    global roster_df
    roster_df = pd.read_csv(BytesIO(data), skiprows=3,)
    roster_df = roster_df[:60] # Read only the first 60 rows (should be updated in the future - the later rows are for lurkers and have been excluded)
    
    await ctx.send("Roster table updated.")
    
@client.command(name='specinfo',
                description="Displays numbers of each spec of every class.",
                brief="Displays numbers of each spec of every class.")
async def specinfo(ctx, class_type = ''):
    class_list = ['Mage', 'Rogue', 'Warlock', 'Warrior', 'Shaman', 'Priest', 'Hunter']
    
    def get_info(x): 
        # Function that takes in the variable x - a dictionary of counts and generates a histogram         
        test_list = []
        for key, val in x.items():
            test_list.append((key, int(val)))
                         
        graph = Pyasciigraph()
        out_string = "```"
        
        # Sort the dictionary in descending order and create a multi-line string
        for line in  graph.graph(class_type + ' spec distribution', sorted(test_list, key=lambda x: x[1], reverse=True)):
            out_string = out_string + '\n' + line
        out_string = out_string + "\n ```"
        return(out_string)
            
    if 'roster_df' in globals(): # Ensure roster_df has been read in
        if class_type == '': # If no class is specified return all specs
            x = Counter(roster_df['Spec'].dropna())
            await ctx.send(get_info(x))
        elif class_type.lower() in (types.lower() for types in class_list): # If a class has been specified return specs of that clas
            x = Counter(roster_df[roster_df.Class == class_type.capitalize()]['Spec'].dropna())
            await ctx.send(get_info(x))
        elif class_type == 'Paladin' or class_type == 'paladin': # Ensure no alliance
            await ctx.send("We don't take kindly to alliance around here.")
        else:
            await ctx.send('Class argument not understood.') # If the class argument is not a valid class - return this message
    else:
        await ctx.send("Roster table not found. Use !updatetable to update it.") # If the roster table does not exist - return this message
        
        
@client.command()
async def roleinfo(ctx, class_type = ''):
    class_list = ['Mage', 'Rogue', 'Warlock', 'Warrior', 'Shaman', 'Priest', 'Hunter']
    
    def get_info(x, class_type=''):
        # Function that takes in a dictionary of counts of roles and returns a ASCII histogram
        test_list = []
        for key, val in x.items():
            test_list.append((key, int(val)))
            
        graph = Pyasciigraph()
        out_string = "```"
        
        # Sort the dictionary and append all results to a single string to be returned
        for line in  graph.graph(class_type + ' role distribution', sorted(test_list, key=lambda x: x[1], reverse=True)):
            out_string = out_string + '\n' + line
        out_string = out_string + "\n ```"
        return(out_string)
        
    if 'roster_df' in globals(): # Ensure roster_df has been read in
        
        if class_type == '': # If no class type has been specified return roles of all classes
            x = Counter(roster_df['Role'].dropna())
            await ctx.send(get_info(x))
                
        elif class_type.lower() in (type.lower() for type in class_list): # If a class has been specified, return only roles of that class
            x = Counter(roster_df[roster_df.Class == class_type.capitalize()]['Role'].dropna())
            await ctx.send(get_info(x, class_type))
                
        elif class_type == 'Paladin' or class_type == 'paladin': # Again, ensure no alliance 
            await ctx.send("We don't take kindly to alliance around here.")
        
        else:
            await ctx.send('Class argument not understood.') # If the class is not valid - display this message
    
    else:
        await ctx.send("Roster table not found. Use !updatetable to update it.") # If the roster_df does not exist - display this message

@client.command()
async def classinfo(ctx):
    def get_info(x):
        # Function that takes in a dictionary of counts and returns a histogram
        test_list = []
        for key, val in x.items():
            test_list.append((key, int(val)))
        
        graph = Pyasciigraph()
        out_string = "```"

        for line in graph.graph('class distribution', sorted(test_list, key=lambda x: x[1], reverse=True)):
            out_string = out_string + '\n' + line
        out_string = out_string + "\n ```"
        return(out_string)

    if 'roster_df' in globals(): # Ensure roster_df exists
        x = Counter(roster_df['Class'].dropna())
        await ctx.send(get_info(x))
    else:
        await ctx.send("Roster table not found. Use !updatetable to update it.")

@client.command()
async def profinfo(ctx, level='60', prof_name=''):
    def get_profs(col1, col2):
        # Counts the number of professions from 2 columns - either the level 60 or leveling columns
        prof_list = []
        for item in roster_df[col1].dropna():
            prof_list.append(item)
        for item in roster_df[col2].dropna():
            prof_list.append(item)
        
        x = Counter(prof_list) # Create count dictionary from the list created above
    
        test_list = []
        for key, val in x.items():
            test_list.append((key, int(val)))
        
        # Create the ASCII graph and output as a single string
        graph = Pyasciigraph()
        out_string = "```"
        for line in  graph.graph(col2, sorted(test_list, key=lambda x: x[1], reverse=True)):
            out_string = out_string + '\n' + line
        out_string = out_string + "\n ```"
        return(out_string)
        
    def get_players(col1, col2):
        # Return a list of players that have a certain profession at level 60 or while leveling
        player_list = []
        for player in list(roster_df[roster_df[col1]==prof_name.capitalize()]['Raider']):
            player_list.append(player)
        for player in list(roster_df[roster_df[col2]==prof_name.capitalize()]['Raider']):
            player_list.append(player)
        out_string = "```Players with " + prof_name + " " + col2.split(" ")[1] + " " + col2.split(" ")[2] + ":"
        for player in player_list:
            out_string = out_string + "\n" + player
        out_string = out_string + "```"
        return(out_string)
        
    if 'roster_df' in globals():
        if prof_name == '':
            if level == '60':
                await ctx.send(get_profs('Unnamed: 12', 'Professions at 60')) # Pass the 2 columns to be scanned to the function
            
            elif level == 'leveling' or level == 'Leveling':
                await ctx.send(get_profs('Unnamed: 15', 'Professions while leveling'))
                
            else:
                await ctx.send("Please enter either 'leveling' or '60'")
        else:
            # Output the player names with a certain profession.
            profession_list = ['Alchemy', 'Herbalism', 'Engineering', 'Tailoring', 'Enchanting', 'Mining', 'Blacksmithing', 'Skinning']
            if prof_name.lower() in (prof.lower() for prof in profession_list): 
                if level == '60':
                    await ctx.send(get_players('Unnamed: 12', 'Professions at 60'))

                elif level == 'leveling' or level == 'Leveling':
                    await ctx.send(get_players('Unnamed: 15', 'Professions while leveling'))

                else:
                    await ctx.send('<level> argument not understood')
            else:
                await ctx.send('<profession> argument not understood')
    
    else:
        await ctx.send("Roster table not found. Use !updatetable to update it.")

      
@client.command()
async def dkp(ctx, player_name=''):
    if 'roster_df' in globals():
        if player_name != '':
            if player_name.isdigit():
                dkp_dict = {}
                i = 0
                while i < int(len(roster_df)-1):
                    dkp_dict[roster_df['Raider'][i]] = roster_df['DKP'][i]
                    i += 1

                sorted_dkp = sorted(dkp_dict.items(), key=operator.itemgetter(1))
                outstring = "```NAME\t\t\t\t\t\t\t\t\t\tDKP\n"

                try:
                    i = 0
                    while i < int(player_name):
                        if str(sorted_dkp[i][0]) != "nan":
                            num_spaces = 44 - len(str(sorted_dkp[i][0]))
                            outstring = outstring + str(sorted_dkp[i][0]) + " " * num_spaces + str(sorted_dkp[i][1]) + "\n"
                        else:
                            pass
                        i += 1
                    outstring = outstring + "```"
                    await ctx.send(outstring)
                except:
                    await ctx.send("Number out of range of roster length.")

            else: # Add search for player name in this section
                try:
                    await ctx.send(player_name + ' has ' + str(int(roster_df[roster_df.Raider == player_name]['DKP'].dropna()[0])) + ' dkp.')
                except:
                    await ctx.send('Could not find DKP value for ' + player_name + '.')
        else:
            dkp_dict = {}
            i = 0
            while i < int(len(roster_df) - 1):
                dkp_dict[roster_df['Raider'][i]] = roster_df['DKP'][i]
                i += 1

            sorted_dkp = sorted(dkp_dict.items(), key=operator.itemgetter(1))
            outstring = "```NAME\t\t\t\t\t\t\t\t\t\tDKP\n-----------------------------------------------\n"

            i = 0
            while i < len(sorted_dkp):
                if str(sorted_dkp[i][0]) != "nan":
                    num_spaces = 44 - len(str(sorted_dkp[i][0]))
                    outstring = outstring + str(sorted_dkp[i][0]) + " " * num_spaces + str(sorted_dkp[i][1]) + "\n"
                else:
                    pass
                i += 1
            outstring = outstring + "```"
            await ctx.send(outstring)

    else:
        await ctx.send("Roster table not found. Use !updatetable to update it.")

        
@client.command()
async def attendance(ctx, player_name=''):
    if 'roster_df' in globals():
        if player_name != '':
            try:
                await ctx.send(player_name + ' has ' + str(roster_df[roster_df.Raider == player_name]['Attendance'].dropna()).split(' ')[4].split('%')[0] + '% attendance.')
            except:
                await ctx.send('Could not find attendance percentage for ' + player_name + '.')
        else:
            await ctx.send('Please type a player name after the command.')
    else:
        await ctx.send("Roster table not found. Use !updatetable to update it.")

@client.command()
async def news(ctx, number=3):
    outstring = ""
    newsfeed = feedparser.parse('https://classic.wowhead.com/news&rss')

    for post in newsfeed.entries[:number]:
        outstring = outstring + ("\n" + post.title + ": <" + post.link + ">")

    await ctx.send(outstring)

@client.command()
async def recruitment(ctx):
    await ctx.send('''
    Removed    
    ''')

@client.command()
async def raidtimes(ctx):
    await ctx.send("Removed")

@client.command()
async def phases(ctx):
    await ctx.send('''
    `Phase 1 (Classic Launch)` Molten Core, Onyxia
    `Phase 2` Dire Maul, Azuregos, Kazzak, Honor system, PvP rank rewards
    `Phase 3` Blackwing Lair, Darkmoon Faire, Darkmoon deck drops begin, AV & WSG battlegrounds
    `Phase 4` Zul'Gurub, Green Dragons, AB battleground
    `Phase 5` Ahn’Qiraj War Effort begins, Ahn’Qiraj raids open when the war effort dictates, Dungeon loot reconfiguration (Tier 0.5 Dungeon gear, Relics, drop rates and location changes)
    `Phase 6` Naxxramas, Scourge Invasion. World PvP objectives in Silithus and Eastern Plaguelands''')

@client.command()
async def blacklist(ctx, cmd="", name="", reason=""):
    outstring = "NAME\t\t   REASON\n-----------------------\n"
    if cmd == "":
        for key, val in black_list.items():
            num_spaces = 15 - len(key)
            outstring = outstring + key + " "*num_spaces + val + "\n"
        await ctx.send("```" + outstring + "```")
    elif cmd == "add":
        # Add name to blacklist
        if name == "":
            await ctx.send("Please specify a player name.")
        else:
            if name in black_list.keys():
                await ctx.send("Player already blacklisted.")
            else:
                black_list[name] = reason
                await ctx.send(name + " added to blacklist.")
    elif cmd == "rm":
        # Remove name from blacklist
        if name == "":
            await ctx.send("Please specify a player name.")
        else:
            try:
                del black_list[name]
                await ctx.send(name + " removed from blacklist.")
            except:
                await ctx.send("Name not found in blacklist.")

    with open('blacklist_file', 'wb') as fp:
        pickle.dump(black_list, fp)
        print("[" + datetime.now().strftime('%H:%M:%S') + "] " + "Wrote blacklist to file.")


@client.command()
async def bounties(ctx, cmd="", name="", reward="", setby=""):
    outstring = "NAME\t\t   BOUNTY\t\tSET BY\n----------------------------------------\n"
    if cmd == "":
        for key, val in bounty_list.items():
            num_spaces = 15 - len(key)
            num_spaces_2 = 14 - len(val[0])
            outstring = outstring + key + " "*num_spaces + val[0] + " "*num_spaces_2 + val[1] + "\n"
        await ctx.send("```" + outstring + "```")
    elif cmd == "add":
        # Add name to blacklist
        if name == "" and reward == "":
            await ctx.send("Please specify a player name and reward.")
        elif name != "" and reward == "":
            await ctx.send("Please specify a player name and reward.")
        else:
            if setby == "":
                if name not in bounty_list.keys():
                    bounty_list[name] = [reward, ctx.message.author.name]
                    await ctx.send(name + " added to bounty list.")
                else:
                    i = 2
                    while i < 25:
                        if name+"[" + str(i) + "]" not in bounty_list.keys():
                            name = name + "[" + str(i) + "]"
                            bounty_list[name] = [reward, ctx.message.author.name]
                            break
                        else:
                            i += 1
                    await ctx.send(name + " added to bounty list.")
            else:
                bounty_list[name] = [reward, setby]
                await ctx.send(name + " added to bounty list.")
    elif cmd == "rm":
        # Remove name from blacklist
        if name == "":
            await ctx.send("Please specify a player name.")
        else:
            try:
                del bounty_list[name]
                await ctx.send(name + " removed from bounty list.")
            except:
                await ctx.send("Name not found in bounty list.")


    with open('bounty_file', 'wb') as fp:
        pickle.dump(bounty_list, fp)
        print("[" + datetime.now().strftime('%H:%M:%S') + "] " + "Wrote bounty list to file.")

#################

@client.event
async def on_ready():
    #await client.change_presence(activity = discord.Game(name="Saving us all"))
    print("[" + datetime.now().strftime('%H:%M:%S') + "] " + "Logged in as " + client.user.name)
    

async def news_update():
    await client.wait_until_ready()
    while True:
        channel = client.get_channel('channel_num')
        feed = feedparser.parse('https://classic.wowhead.com/news&rss')

        if 'last_news' in locals():
            pass
        else:
            last_news = feed['entries'][0]['title']
            print("[" + datetime.now().strftime('%H:%M:%S') + "] " + 'last_news updated.')

        if len(feed['entries']) > 0:
            if feed['entries'][0]['title'] == last_news:
                print("[" + datetime.now().strftime('%H:%M:%S') + "] " + 'Checked news. No updates.')
            else:
                if "Guides" not in feed['entries'][0]['title'] and "Quests" not in feed['entries'][0]['title'] and "Most Popular" not in feed['entries'][0]['title'] and "Wowhead" not in feed['entries'][0]['title']:
                    #await channel.send(feed['entries'][0]['title'] + ": <" + feed['entries'][0]['link'] + ">")
                    last_news = feed['entries'][0]['title']
                else:
                    last_news = feed['entries'][0]['title']

                    print("[" + datetime.now().strftime('%H:%M:%S') + "] " + 'Checked news. There was one update.')
        else:
            print("[" + datetime.now().strftime('%H:%M:%S') + "] " + "No feed found, will retry in 5 minutes.")
        ################################################################################################################
        # Read the guild's Google Sheet into a Pandas dataframe and set it as a global variable
        r = requests.get('sheet link')
        data = r.content
        global roster_df
        roster_df = pd.read_csv(BytesIO(data), skiprows=3, )
        roster_df = roster_df[:130]  # Read only the first 130 rows (should be updated in the future - the later rows are for lurkers and have been excluded)
        print("[" + datetime.now().strftime('%H:%M:%S') + "] " + 'Updated roster table.')

        await asyncio.sleep(300)

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error

client.remove_command('help')
client.loop.create_task(news_update())

client.run(TOKEN)