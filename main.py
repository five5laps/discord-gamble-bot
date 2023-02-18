from random import randint
import requests
import disnake
import sqlite3
import json
from disnake.ext import commands

bot = commands.Bot(command_prefix="v_", help_command=None, intents=disnake.Intents.all())

global db
global sql
db = sqlite3.connect('server.db')
sql = db.cursor()

sql.execute("""CREATE TABLE IF NOT EXISTS users (
    userid BIGINT,
    display_name TEXT,
    cash INT
)""")

db.commit()

g_is_owner_out = False

@bot.event
async def on_ready():
    for i in range (0,5):
        print(f'We have logged in as {bot.user}')
    
@bot.command()
async def profile(ctx):
    array = []
    sql.execute(f"SELECT userid FROM users WHERE userid = '{ctx.author.id}'")
    if sql.fetchone() is None:
        sql.execute(f"INSERT INTO users VALUES (?, ?, ?)", ( ctx.author.id, ctx.author.display_name, 1000))
        await ctx.send(f"{ctx.author.mention} Вам выдан стартовый баланс в 1000$!")
    else:
        for i in sql.execute(f"SELECT userid FROM users WHERE userid = '{ctx.author.id}'"):
            array.append(i[0])
        for i in sql.execute(f"SELECT cash FROM users WHERE userid = '{ctx.author.id}'"):
            array.append(i[0])
        await ctx.send(f"{ctx.author.mention}\n Ваш ID: ***{array[0]}***\n Баланс: ***{array[1]}***")
    db.commit()
        

@bot.command()
async def checkdball(ctx):
    for val in sql.execute("SELECT * FROM users"):
        await ctx.send(f"{val}")

@bot.command()
async def delete_db(ctx, id):
    sql.execute(f"DELETE FROM users WHERE userid = '{id}' ")
    db.commit()
    await ctx.send(f"{id} был удален из таблицы!")
    

@bot.command()
async def dice(ctx, value, bet):
    casharr = []

    for i in sql.execute(f"SELECT cash FROM users WHERE userid = '{ctx.author.id}'"):
        casharr.append(i[0])

    if casharr[0] == 0:
        await ctx.send(f"**{ctx.author.mention}, у вас закончился баланс!**")
        return

    if int(bet) > casharr[0] or int(bet) < 1:
        await ctx.send(f"**{ctx.author.mention}, у вас недостаточно баланса!**")
        return

    if int(value) < 1 or int(value) > 6:
        await ctx.send(f'{ctx.author.mention}, {value} не находится в диапазоне от 1 до 6!')
        return

    winNum = randint(1, 6)
    
    sql.execute(f'SELECT userid FROM users WHERE userid = "{ctx.author.id}"')
    if sql.fetchone() is None:
        await ctx.send(f"Вы еще не игрок, попробуйте ```v_profile```, если еще не пробовали!")
    else:      
        await ctx.send(f"{ctx.author.mention} Вы поставили {bet}$ на число {value}!")
        if int(value) != winNum:
            sql.execute(f'UPDATE users SET cash = cash-{bet} WHERE userid = "{ctx.author.id}"')
            await ctx.send(f"Поражение! {ctx.author.mention}, победное число было {winNum}")
        else: 
            await ctx.send(f"Победа! {ctx.author.mention}, вы выйграли {bet}$")
            sql.execute(f'UPDATE users SET cash = cash+{bet} WHERE userid = "{ctx.author.id}"')
    db.commit()
            

async def checkbalance(ctx, bet):
    casharr = []

    for i in sql.execute(f"SELECT cash FROM users WHERE userid = '{ctx.author.id}'"):
        casharr.append(i[0])

    if casharr[0] == 0:
        await ctx.send(f"**{ctx.author.mention}, у вас закончился баланс!**")
        return

    if int(bet) > casharr[0] or int(bet) < 1:
        await ctx.send(f"**{ctx.author.mention}, у вас недостаточно баланса!**")
        return


@bot.command()
async def coin(ctx, side, bet):
    casharr = []

    for i in sql.execute(f"SELECT cash FROM users WHERE userid = '{ctx.author.id}'"):
        casharr.append(i[0])

    if casharr[0] == 0:
        await ctx.send(f"**{ctx.author.mention}, у вас закончился баланс!**")
        return

    if int(bet) > casharr[0] or int(bet) < 1:
        await ctx.send(f"**{ctx.author.mention}, у вас недостаточно баланса!**")
        return
        
    winNum = randint(1, 2)
    sql.execute(f'SELECT userid FROM users WHERE userid = "{ctx.author.id}"')
    if sql.fetchone() is None:
        await ctx.send(f"Вы еще не игрок, попробуйте ```v_profile```, если еще не пробовали!")
    else:      
        if side not in "ОРЁЛ" and side not in "РЕШКА" and side not in "ОРЕЛ" and side not in "орёл" and side not in "орел" and side not in "решка":
            await ctx.send(f'{ctx.author.mention}, выберите между ***ОРЁЛ*** или ***РЕШКА***!')
            return
        else:
            sql.execute(f'SELECT cash FROM users')
            await ctx.send(f"{ctx.author.mention} Вы поставили {bet}$ на {side}!")
            if winNum == 1:
                sql.execute(f'UPDATE users SET cash = cash-{bet} WHERE userid = "{ctx.author.id}"')
                await ctx.send(f"Поражение! {ctx.author.mention}")
            else: 
                await ctx.send(f"Победа! {ctx.author.mention}, вы выйграли {bet}$")
                sql.execute(f'UPDATE users SET cash = cash+{bet} WHERE userid = "{ctx.author.id}"')
    db.commit()

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    global g_is_owner_out

    if message.content.startswith("!bottalk"):
        if g_is_owner_out == True:
            g_is_owner_out = False
            await message.channel.send("BotTalk is now OFF")
        elif g_is_owner_out == False:
            g_is_owner_out = True
            await message.channel.send("BotTalk is now ON")
        await message.delete()

    if message.author.id == 229200435401981953:
        if g_is_owner_out == True:
            await message.delete()
            await message.channel.send(message.content)
                
                

bot.run("MTA3MDY1NjM3NjI4NTcxMjM4Ng.G4cRVI.Dq4TmGRyLLn8yPzht9aWw38LMQ6_Y60gKsdJLU")
