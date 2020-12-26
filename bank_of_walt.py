import json

import discord
from discord.ext import commands
from settings import bot_token

description = '''A discord bot to keep track of fake internet points.'''

intents = discord.Intents.default()
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix='?', description=description, intents=intents)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.event
async def on_member_join(member):
    with open('users.json', 'r') as f:
        users = json.load(f)

    await update_data(users, member)

    with open('users.json', 'w') as f:
        json.dump(users, f)


async def update_data(users, user):
    if not f'{user.id}' in users:
        print(f"adding {user.id}")
        users[f'{user.id}'] = {}
        users[f'{user.id}']['bux'] = 100


@bot.command()
async def bal(ctx):
    """Check the balance of your waltbux account."""
    with open('users.json', 'r') as f:
        users = json.load(f)

    await update_data(users, ctx.author)

    with open('users.json', 'w') as f:
        json.dump(users, f)

    await ctx.send(f'{ctx.author} has {users[f"{ctx.author.id}"]["bux"]} bux in their walt vault')


@bot.command()
async def give(ctx, member: discord.Member, n: int):
    """Give your waltbux to another user."""
    if n > 0:
        with open('users.json', 'r') as f:
            users = json.load(f)

        await update_data(users, ctx.author)

        if ctx.author.id != member.id:
            if users[f"{ctx.author.id}"]['bux'] >= n:
                users[f"{ctx.author.id}"]['bux'] -= n
                users[f"{member.id}"]['bux'] += n
                await ctx.send(f'Gave {n} waltbux to {member}')
            else: await ctx.send("You don't have enough waltbux to make that gift!")
        else: await ctx.send("You can't give yourself waltbux!")
        with open('users.json', 'w') as f:
            json.dump(users, f)

@bot.command()
async def bet(ctx, arbiter: discord.Member, n: int, *condition: str):
    """Make bets to win more waltbux.
    Usage:  $bet [arbiter] [amount] [win condition]
    Arbiter should react with ✅ to affirm a win and ❌ to report a loss."""
    with open('users.json', 'r') as f:
        users = json.load(f)

    if ctx.author.id != arbiter.id:
        if users[f"{ctx.author.id}"]['bux'] >= n:
            # await ctx.
            await ctx.send(f"BET: {ctx.author} {n} {' '.join(condition)} awaiting judgement from {arbiter}")
        else: await ctx.send("You don't have enough waltbux to make that bet!")
    else: await ctx.send("You can't resolve your own bet!")


@bot.event
async def on_reaction_add(reaction, user):
    if reaction.message.content.startswith("BET:"):
        msg = reaction.message.content.split()
        arbiter = msg[-1]
        if user == reaction.message.guild.get_member_named(arbiter):

            if reaction.emoji == '✅':
                with open('users.json', 'r') as f:
                    users = json.load(f)
                bettor = reaction.message.guild.get_member_named(msg[1])
                amount = int(msg[2])
                users[f"{bettor.id}"]["bux"] += amount
                with open('users.json', 'w') as f:
                    json.dump(users, f)

            elif reaction.emoji == '❌':
                with open('users.json', 'r') as f:
                    users = json.load(f)
                bettor = reaction.message.guild.get_member_named(msg[1])
                amount = int(msg[2])
                users[f"{bettor.id}"]["bux"] -= amount
                with open('users.json', 'w') as f:
                    json.dump(users, f)

bot.run(bot_token)
