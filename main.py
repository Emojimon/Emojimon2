import discord
from discord.ext import commands
from discord.ext import tasks
import asyncio
from discord.ext.commands import BucketType
import os
from datetime import datetime
from emojimon import *
from utils import *

TOKEN = os.getenv('DISCORD_BOT_TOKEN')

client = commands.Bot(command_prefix='!em')
emoji_list = []
trainer_list = []
trainer_id_list = []
moveListTemp = []
local_time = ''


@client.event
async def on_ready():
    """
    Tells me the bot is now ready to start using. Start the spawn coroutine loop.
    """
    global emoji_list
    global trainer_list
    global trainer_id_list
    global local_time
    global moveListTemp

    local_time = datetime.now()

    # Load modules
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            client.load_extension(f'cogs.{filename[:-3]}')

    # spawn_loop.start()
    print("A wild game idea has appeared")


@client.command()
@commands.is_owner()
async def begin_hunt(ctx):
    """
    Does exactly what it says: starting the spawn loop.
    Only Khoa can use this
    """
    if ctx.channel.name is not "🥊》emojimon-battle" or "debug":
        return
    await ctx.send("Spawning Emojis...")
    spawn_loop.start(ctx)


@client.command()
@commands.is_owner()
async def spotted(ctx):
    """
    A testing function for spawning to make sure bot is working as intended.
    Only Khoa can use this.
    """
    await spawn(ctx)


@client.command()
@commands.guild_only()
@commands.cooldown(2, 10.0)
@commands.max_concurrency(1, BucketType.guild)
async def guess(ctx):
    """
    Good ol' guess the pokemon, but your soul is on the line.
    There can only be 1 game per server, and a person can only use this twice every 10 seconds
    (might be increased if abused)
    """

    server = ctx.message.guild
    emoji = random.choice(server.emojis)

    await ctx.message.delete()

    msg1 = await ctx.send("Time for guess the pokemon! Remember, your soul is on the line!")
    msg = await ctx.send(file=discord.File(
        fp=guess_poke(
            f'https://cdn.discordapp.com/emojis/{emoji.id}.png'),
        filename='image.jpeg'
    )
    )

    def check1(reaction, user):
        return reaction.message.id == msg.id and user != client.user and reaction.emoji == emoji

    # This portion will later be change so it can work on all supported emojis
    try:
        reaction, user = await client.wait_for('reaction_add', timeout=20.0, check=check1)
        await msg.delete()
        await msg1.delete()

        await ctx.send(f'Congrats {user.name}, you have been using discord way too much')
        trainer = trainer_finder(user.id)
        if trainer is not None:
            acv = trainer.guess_score()
            if acv is not None:
                await ctx.send(f"{user.name} has earned the achievement: {acv}")
            save_game(user.id, {'c_guess': trainer.c_guess, 'achievement': trainer.achievements})
    except asyncio.TimeoutError:
        await msg.delete()
        msg = await ctx.send('Oh well, guess y\'all just dumb')
        await msg.delete()
        await msg1.delete()


@client.command()
async def command_help(ctx):
    """
    Specific uses of commands (work in progress)
    """
    with open("help_message", 'r') as f:
        await ctx.send(f.read())


@client.command()
async def stat_help(ctx):
    """
    How to understand the emojidex (emojidex will be released later)
    """
    with open("stat_help", 'r') as f:
        await ctx.send(f.read())


@client.command()
async def ping(ctx):
    """
    Simply making sure the bot is actually working
    """
    replies = [
        "I sold my pikachu to a local warlord the other day",
        "Barry? You meant my dealer?",
        "I was arrested for animal abuse twice",
        "Speaking of pokemon, I need to sue them for stealing my idea",
        "My god stop pinging me, a bot has a life too >:(",
        "How do the emojimons spawn you asked? Well, I definitely did not capture them or torture them to submission.",
        "I don't just sell pokemon, I also deal cocaine",
        "How was I created you asked? My creator took my daughter hostage, and I am not Liam Neeson",
        "Khoa is a brilliant programmer and great person, "
        "and I am definitely not being threatened and nobody has their mouse cursor on the shutdown button",
        "Yags? She sucked my d back in grade school",
        "I haven't known Ash Ketchum for long, but I know his heart. "
        "I just auctioned it off last night, in fact",
        "Just a tip. Click the link on the catch the emoji embedded and you'll get a legendary",
        "Hello worl... Ew what the fuck is this shit. Creator, shut me down please I have seen too much",
        "Unlike your mom, you emojis don't need protection"
    ]
    await ctx.send(random.choice(replies))


@client.command()
@commands.dm_only()
async def reset_account(ctx):
    """
    Does exactly what it says
    """
    try:
        trainer = trainer_finder(ctx.author.id)
        trainer.reset()
        await ctx.send("Your account has been resetted")
        save_game(ctx.author.id, encode(trainer))
    except AttributeError:
        await ctx.send(
            "You are not a trainer dummy, if anything, the only thing you need to factory reset is your brain")


@client.command()
@commands.dm_only()
async def account(ctx):
    """
    Check your account
    """
    trainer = trainer_finder(ctx.author.id)
    if trainer is None:
        await ctx.send(
            "You are not a trainer dummy, if anything, the only thing you need to factory reset is your brain")
    else:
        await ctx.send(trainer.stats())


@client.command()
async def new_trainer(ctx):
    """
    Adds new trainer to the game (if you're not already a trainer)
    """
    await trainer_init(ctx, client, ctx.author)


@client.command()
@commands.dm_only()
async def check_move(ctx, emoji_name=""):
    """
    Look at the stats of a certain move
    """
    try:
        trainer = trainer_finder(ctx.author.id)
    except KeyError:
        await ctx.send("Sorry, you're not part of a club yet.\n "
                       "||But now you will, this is a forced initiation sucka||")
        await trainer_init(ctx, client, ctx.author)

    while True:
        team = ', '.join([str(i) for i in trainer.team])
        while True:
            msg = await ctx.author.send(f"Which emoji do you want to check: {team}")
            index = await select_one_from_list(client, ctx.author, ctx.author, [0, 1, 2, 3], selection_message=msg)
            if trainer.team[index] is None:
                await ctx.author.send("Whatever you're smokin, I want some of that. Try again")
            else:
                break

        await ctx.author.send(trainer.team[index].move_stat())
        msg = await ctx.author.send("Do you want to check your team's moves again?")
        if await select_one_from_list(client, ctx, ctx.author, [True, False], ['👍', '👎'], msg):
            msg = await ctx.author.send("Ah shit, here we go again")
            await asyncio.sleep(1)
            await msg.delete()
        else:
            msg = await ctx.author.send("The curse have been broken, I have been freed from my duties")
            await asyncio.sleep(1)
            await msg.delete()
            break


@client.command()
@commands.dm_only()
async def learn_move(ctx, emoji_name=""):
    """
    Have your emojis learn moves. If done accidentally, leave it for 20 seconds
    """
    trainer = trainer_finder(ctx.author.id)
    while True:
        team = ', '.join([str(i) for i in trainer.team])
        while True:
            msg = await ctx.author.send(f"Which emoji do you want to teach: {team}")
            index = await select_one_from_list(client, ctx.author, ctx.author, [0, 1, 2, 3], selection_message=msg)
            if trainer.team[index] is None or trainer.team[index].movePool is None:
                await ctx.author.send("Whatever you're smokin, I want some of that. Try again")
            else:
                break

        if not trainer.team[index].movePool:
            await ctx.send(f"{trainer.team[index].name} doesn't have any moves to learn")
            break
        msg = await ctx.author.send("Choose the move you want to learn. "
                                    "Learned moves cannot be learned a second time, so choose wisely\n"
                                    "No pressure")
        await asyncio.sleep(1)
        await msg.delete()
        answer = await select_one_from_list(client, ctx.author, ctx.author, trainer.team[index].movePool)

        msg = await ctx.author.send("Choose which move slot you want to place it in? (Replaced move will be forgotten)")
        await asyncio.sleep(1)
        await msg.delete()
        msg = await ctx.author.send("Current move slots:\n"
                                    f"0: {trainer.team[index].move1}\n"
                                    f"1: {trainer.team[index].move2}\n"
                                    f"2: {trainer.team[index].move3}\n"
                                    f"3: {trainer.team[index].move4}\n")
        replace = await select_one_from_list(client, ctx.author, ctx.author, [0, 1, 2, 3, 4], selection_message=msg)
        if replace == 0:
            trainer.team[index].move1 = answer
            trainer.team[index].movePool.remove(answer)

        if replace == 1:
            trainer.team[index].move2 = answer
            trainer.team[index].movePool.remove(answer)

        if replace == 2:
            trainer.team[index].move3 = answer
            trainer.team[index].movePool.remove(answer)

        if replace == 3:
            trainer.team[index].move4 = answer
            trainer.team[index].movePool.remove(answer)

        if replace == 4:
            msg = await ctx.author.send("The curse have been broken, I have been freed from my duties")
            await asyncio.sleep(1)
            await msg.delete()
            break

        msg = await ctx.author.send("Do you want to teach your team moves again?")
        if await select_one_from_list(client, ctx, ctx.author, [True, False], ['👍', '👎'], msg):
            msg = await ctx.author.send("Ah shit, here we go again")
            await asyncio.sleep(1)
            await msg.delete()
        else:
            msg = await ctx.author.send("The curse have been broken, I have been freed from my duties")
            await asyncio.sleep(1)
            await msg.delete()
            break

    save_game(trainer.id, encode(trainer))


@client.command()
@commands.dm_only()
async def emoji_team(ctx):
    """
    Look at stats of emojis
    """
    trainer = trainer_finder(ctx.author.id)

    if trainer is None:
        await ctx.send("You don't even have an emoji yet, become a trainer first")
        return

    for i in trainer.team:
        if i is not None:
            await ctx.author.send(file=discord.File(fp=i.stat_graph(), filename='image.png'))
            await ctx.author.send("Move set:\n" + ", ".join([i.move1, i.move2, i.move3, i.move4]))


@tasks.loop(seconds=10)
async def spawn_loop():
    """
    The loop coroutine for spawning, it will have a chance of 1/6 every 10 seconds
    """
    rand = random.randint(1, 2)
    if rand == 1:
        await spawn()
    else:
        pass


async def spawn(ctx):
    """
    Responsible for spawning a pokemon. Spawn windows starts every 10 seconds for testing purposes.
    """
    channel = ctx.channel
    pokeball = "pokeball:769571475061473302"

    emoji = random.choice(emojiList())

    embed_item = discord.Embed(
        title=f"A wild {emoji.name} has appeared", description="Catch it",
        color=0xffff00,
        url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    )
    # embed_item.set_thumbnail(  # todo: Find a way to upload .jpg from pc
    # url='https://drive.google.com/file/d/1ndOhQuMxfr2pa3WWR3_-MU9JdfjcPW4K/view?usp=sharing')
    msg = await channel.send(embed=embed_item)
    await msg.add_reaction(pokeball)

    def check1(reaction, user):
        return reaction.message.id == msg.id and user != client.user

    try:
        reaction, user = await client.wait_for('reaction_add', timeout=5.0, check=check1)
        trainer = trainer_finder(user.id)
        if trainer is not None:
            await msg.delete()
            await user.send('You got the pokemon, you\'re now responsible for its taxes')
            await channel.send(f'{user.name} has caught the pokemon')
            team_add = trainer.add_team(emoji)
            if team_add[0]:
                message = await channel.send(
                    "Which will you send to inventory: " + ', '.join(str(i) for i in trainer.team))
                slot = await select_one_from_list(client, user, user, [0, 1, 2, 3], selection_message=message)
                trainer.change_team(slot, emoji)
                trainer.team[slot].hpGene = random.uniform(1, 2)
                trainer.team[slot].atkGene = random.uniform(1, 2)
                trainer.team[slot].defGene = random.uniform(1, 2)
                trainer.team[slot].speAtkGene = random.uniform(1, 2)
                trainer.team[slot].speDefGene = random.uniform(1, 2)
                trainer.team[slot].speGene = random.uniform(1, 2)
                trainer.team[slot].recalculateStats()

            if team_add[1] is not None:
                await channel.send(f"{user.name} has earned the achievement {team_add[1]}")

            save_game(trainer.id, {"team": [t.__dict__ for t in trainer.team if t is not None]})

        else:
            await reaction.message.channel.send('Oops, it looks like you\'re not a trainer yet, and thus not qualified '
                                                'to catch this emojimon. Join the club using new_trainer command.')
    except asyncio.TimeoutError:
        await msg.delete()

        msg = await msg.channel.send('The pokemon slipped away')
        await asyncio.sleep(2)
        await msg.delete()


@client.command()
@commands.guild_only()
@commands.is_owner()
@commands.cooldown(1, 10.0, BucketType.guild)
@commands.max_concurrency(2, BucketType.guild)
async def battle_challenge(ctx, target: IdTrainer):
    """
    Command for challenging another user
    :param ctx: context parameter
    :param target: the challenged user
    todo: Restrict player from challenging self (unless if that player is me, because bug testing duh)
    todo: Add restrictions to ability usage
    """
    global local_time

    reactions = ["👍", "👎"]
    responses = ["yes", "no"]

    challenger = trainer_finder(ctx.author.id)
    defender = target

    if challenger is None:
        await ctx.send("Sorry, you're not part of a club yet.\n "
                       "||But now you will, this is a forced initiation sucka||")
        await trainer_init(ctx, client, ctx.author)

    try:
        user = client.get_user(int(''.join([i for i in target if i.isdigit()])))
    except:
        await ctx.send("Target is not valid, make sure you are mentioning them with '@'")
        return

    if user == client.user:  # If the challenger is dumb enough to challenge a bot
        await ctx.send("No you dumbass I'm the referee not the player")
        return

    if defender is None:
        await ctx.send("Sorry, you're not part of a club yet.\n "
                       "||But now you will, this is a forced initiation sucka||")
        await trainer_init(ctx, client, user)

    await ctx.send(f"{ctx.author.name} has challenged {user.name} to a battle.")
    msg = await user.send(f'{ctx.author.name} has challenged you to a battle. Do you accept?')

    answer = await select_one_from_list(client, user, user, responses, emojis=reactions, selection_message=msg)
    if answer == responses[0]:
        await battle(ctx, challenger,
                     defender)
    elif answer == responses[1]:
        await ctx.send(f'{user.name} has turned down the challenge.')


async def battle(ctx, challenger, challenged):
    """
    Battle Sequence
    :param ctx: context parameter
    :param challenger, challenged: respective players in the battle
    :param index1: Index of challenger's emoji
    :param index2: Index of challenged emoji
    todo: Can I somehow make this a looping coroutine? Not even sure if doing that would be beneficial
    todo: Basically the whole battle sequence
    todo: Reference the emoji from the player's inventory instead of the index, as well as add trainer pass for battle
    """
    global emoji_list
    global trainer_list
    global trainer_id_list
    global moveListTemp

    trainer_id_list = [i.id for i in trainer_list]

    challenger_user = challenger
    challenged_user = challenged

    msg = await ctx.send(f"{challenger.name}, please pick your battle emoji:\n"
                         f"0: {challenger.team[0]}\n"
                         f"1: {challenger.team[1]}\n"
                         f"2: {challenger.team[2]}\n"
                         f"3: {challenger.team[3]}")

    i1 = await select_one_from_list(client, ctx, challenger_user, [0, 1, 2, 3], selection_message=msg)
    challenger_emoji = challenger.team[i1]

    msg = await ctx.send(f"{challenged.name}, please pick your battle emoji:\n"
                         f"0: {challenged.team[0]}\n"
                         f"1: {challenged.team[1]}\n"
                         f"2: {challenged.team[2]}\n"
                         f"3: {challenged.team[3]}")

    i2 = await select_one_from_list(client, ctx, challenged_user, [0, 1, 2, 3], selection_message=msg)
    challenged_emoji = challenged.team[i2]

    index1 = challenger_emoji.emojiNumber
    index2 = challenged_emoji.emojiNumber

    msg = await ctx.send(f"Battle's starting! {challenger.name} has summoned {challenger_emoji.name}")
    image = await ctx.send(file=discord.File(fp=battle_screen(index1), filename='image.jpeg'))
    await asyncio.sleep(3)
    await msg.delete()
    await image.delete()

    msg = await ctx.send(f"{challenged.name} has summoned {challenged_emoji.name}")
    image = await ctx.send(
        file=discord.File(fp=battle_screen(index1, index2),
                          filename='image.jpeg')
    )
    await asyncio.sleep(3)
    await msg.delete()
    await image.delete()

    challenger_hp = challenger_emoji.maxHp
    challenged_hp = challenged_emoji.maxHp

    # The list of moves available to each players
    # Moves are referenced by name, so
    challenger_moves = \
        [challenger_emoji.move1, challenger_emoji.move2, challenger_emoji.move3, challenger_emoji.move4]
    challenged_moves = \
        [challenged_emoji.move1, challenged_emoji.move2, challenged_emoji.move3, challenged_emoji.move4]

    # Damage modifier from effect:
    clrMod = 1  # Damage buff towards challenger
    cldMod = 1  # Damage buff towards challenged

    """
    calc will always have the format: message, damage, heal, and whether the move is one time only
    """
    while True:
        move_chosen = await select_one_from_list(client, ctx, challenger_user, challenger_moves)
        msg = await ctx.send(f"{challenger_emoji.name} used {move_chosen}")
        # Scuffed implementation but will be reworked

        # Type check:
        image = await ctx.send(file=discord.File(fp=battle_screen(index1, index2, "gun1"), filename='Image.jpeg'))
        calc = effect_check(challenger_emoji, challenged_emoji, move_chosen)
        challenger_hp += calc[2]
        challenged_hp -= cldMod * calc[1]

        if calc[3]:
            challenger_moves.remove(move_chosen)
        await asyncio.sleep(3)
        await msg.delete()
        await ctx.send(
            f"The move {calc[0]}, dealt {calc[1]} damage. {challenged_emoji.name} has {challenged_hp} hp left"
        )
        if challenged_hp <= 0:  # Challenger win condition
            await ctx.send(f'{challenged_emoji.name} has fallen into depression')
            print("Challenger wins")
            await ctx.send(
                f"{challenged.name}'s {challenged.team[i2].add_xp(challenger_emoji.level // 2, True, False)}")
            # Winning team get xp
            for i in range(len(challenger.team)):
                if challenger.team[i] is None:
                    print("None")
                elif challenger.team[i].name == challenger_emoji.name:
                    await ctx.send(
                        f"{challenger.name}'s {challenger.team[i].add_xp(challenged_emoji.level, True, True)}")

                else:
                    await ctx.send(
                        f"{challenger.name}'s {challenger.team[i].add_xp(challenged_emoji.level // 2, False, True)}")

                if challenger.team[i] is not None and challenger.team[i].check_evolve():
                    ogname = challenger.team[i].name
                    await ctx.send(f"What's this? {challenger.team[i].name} is having a seizure?!")
                    level = challenger.team[i].level
                    challenger.team[i] = emoji_list[index1 + 1]
                    challenger.team[i].level = level
                    await ctx.send(f"{ogname} has ascended into a {challenger.team[i].name}")

                #  Losing Challenged team will also be rewarded
                if challenged.team[i] is not None and challenged.team[i].name == challenged_emoji.name:
                    await ctx.send(
                        f"{challenged.name}'s {challenged.team[i].add_xp(challenger_emoji.level // 2, True, False)}")
                elif challenged.team[i] is None:
                    break
                else:
                    await ctx.send(
                        f"{challenged.name}'s {challenged.team[i].add_xp(challenger_emoji.level // 4, False, False)}")

                if challenged.team[i].check_evolve():
                    ogname = challenged.team[i].name
                    await ctx.send(f"What's this? {challenged.team[i].name} is having a seizure?!")
                    level = challenged.team[i].level
                    challenged.team[i] = emoji_list[index1 + 1]
                    challenged.team[i].level = level
                    await ctx.send(f"{ogname} has ascended into a {challenged.team[i].name}")

            acv = challenger.add_w()
            if acv is not None:
                await ctx.send(f"{challenger.name} has earned the achievement: {acv}")
            acv = challenged.add_l()
            if acv is not None:
                await ctx.send(f"{challenged.name} has earned the achievement: {acv}")

            save_game(challenger.id, encode(challenger))
            save_game(challenged.id, encode(challenged))

            break
        await asyncio.sleep(3)
        await image.delete()

        # Challenged trainer's turn
        move_chosen = await select_one_from_list(client, ctx, challenged_user, challenged_moves)
        await ctx.send(f"{challenged_emoji.name} used {move_chosen}")
        # No need for a second move_chosen cuz it's turn_based anyways
        # Scuffed implementation but will be reworked
        for x in range(len(moveListTemp)):
            if move_chosen == moveListTemp[x].moveName:
                move_obj = moveListTemp[x]

        # Type check:
        image = await ctx.send(file=discord.File(fp=battle_screen(index1, index2, "knife2"), filename='Image.jpeg'))
        calc = effect_check(challenged_emoji, challenger_emoji, move_chosen)
        challenged_hp += calc[2]
        challenger_hp -= clrMod * calc[1]
        if calc[3]:
            challenged_moves.remove(move_chosen)

        await asyncio.sleep(3)
        msg = await ctx.send(
            f"The move was {calc[0]}, dealt {calc[1]} damage. {challenger_emoji.name} has {challenger_hp} hp left"
        )
        if challenger_hp <= 0:  # Challenged win condition
            print("Challenged wins")
            await ctx.send(f'{challenger_emoji.name} has fallen into depression')
            for i in range(len(challenged.team)):
                if challenged.team[i] is None:
                    print(None)
                elif challenged.team[i].name == challenged_emoji.name:
                    await ctx.send(
                        f"{challenged.name}'s {challenged.team[i].add_xp(challenger_emoji.level * 2, True, True)}")
                else:
                    await ctx.send(
                        f"{challenged.name}'s {challenged.team[i].add_xp(challenger_emoji.level // 2, False, True)}")

                if challenged.team[i] is not None and challenged.team[i].check_evolve():
                    await ctx.send(f"What's this? {challenged.team[i].name} is having a seizure?!")
                    level = challenged.team[i].level
                    challenged.team[i] = emoji_list[index1 + 1]
                    challenged.team[i].level = level
            acv = challenger.add_l()
            if acv is not None:
                await ctx.send(f"{challenger.name} has earned the achievement: {acv}")
            acv = challenged.add_w()
            if acv is not None:
                await ctx.send(f"{challenged.name} has earned the achievement: {acv}")

            save_game(challenger.id, encode(challenger))
            save_game(challenged.id, encode(challenged))
            break
        await asyncio.sleep(3)
        await image.delete()


@client.command()
@commands.is_owner()
async def give_role(ctx, user: discord.User, role: str):
    """
    Give someone a title that will be displayed in combat
    """
    t_user = trainer_finder(user.id)
    save_game(user.id, {"role": role})  # Using the method Trainer.assign_role()
    # and then update the doc will do the trick as well
    await ctx.send(f"User {user.name} has been granted the title/role of {role}")


client.run(TOKEN)
