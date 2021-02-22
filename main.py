import discord
from discord.ext import commands
from discord.ext import tasks
from discord.utils import get
import asyncio
import random
from image_edit import guess_poke, battle_screen
from battle_calc import damage_calculation, heal_calc
import pickle
import os
from datetime import datetime
from emojimon import Emoji, move, Trainer
import json

TOKEN = 'NzY5NTUxMTc3NjAzNzQzNzU0.X5QqYg.dg_eX083mMvUqU2XGErEzHX6Wn4'

client = commands.Bot(command_prefix='!em')
emoji_list = []
trainer_list = []
trainer_id_list = []
local_time = ''


@client.event
async def on_ready():
    """Tells me the bot is now ready to start using. Start the spawn coroutine loop.
    """
    global emoji_list
    global trainer_list
    global trainer_id_list
    global local_time

    print("A wild game idea has appeared")
    with open("CompleteEmojiDex.dat", "rb") as f:
        emoji_list = pickle.load(f)

    with open("TrainerList.dat", "rb") as f:
        trainer_list = pickle.load(f)

    trainer_id_list = [i.id for i in trainer_list]
    local_time = datetime.now()


@client.command()
async def begin_hunt(ctx):
    """Does exactly what it says: starting the spawn loop
    """
    spawn_loop.start()


@client.command()
async def spotted(ctx):
    """A testing function for spawning to make sure bot is working as intended
    """
    await spawn()


@client.command()
async def guess(ctx):
    """
    Good ol' guess the pokemon, but your soul is on the line
    """

    if await check(ctx, "Sorry but I am a sucker for crowds, your DM won't work. Move to an emojimon channel instead"):
        return

    server = ctx.message.guild
    emoji = random.choice(server.emojis)

    await ctx.message.delete()

    msg1 = await ctx.send("Time for guess the pokemon!")
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
    except asyncio.TimeoutError:
        await msg.delete()
        msg = await ctx.send('Oh well, guess y\'all just dumb')
        await msg.delete()
        await msg1.delete()


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
        "I haven't known Ash Ketchum for long, but I know his heart."
        "I just auctioned it off last night, in fact",
        "Just a tip. Click the link on the catch the emoji embedded and you'll get a legendary",
        "Hello worl... Ew what the fuck is this shit. Creator, shut me down please I have seen too much",
        "Unlike your mom, you emojis don't need protection"
    ]
    await ctx.send(random.choice(replies))


@client.command()
async def new_trainer(ctx):
    """
    Adds new trainer to the game
    """
    await trainer_init(ctx, ctx.author)


@client.command()
async def check_move(ctx, emoji_name=""):
    global trainer_list
    global trainer_id_list

    trainer_id_list = [i.id for i in trainer_list]  # Updates trainer_id_list
    try:
        trainer = trainer_list[trainer_id_list.index(ctx.author.id)]
    except KeyError:
        await ctx.send("Sorry, you're not part of a club yet.\n "
                        "||But now you will, this is a forced initiation sucka||")
        await trainer_init(ctx, ctx.author)

    while True:
        team = ', '.join([str(i) for i in trainer.team])
        while True:
            msg = await ctx.author.send(f"Which emoji do you want to teach: {team}")
            index = await select_one_from_list(ctx.author, ctx.author, [0, 1, 2, 3], selection_message=msg)
            if trainer.team[index] is None:
                await ctx.author.send("Whatever you're smokin, I want some of that. Try again")
            else:
                break

        await ctx.author.send(trainer.team[index].move_stat())


@client.command()
async def learn_move(ctx, emoji_name=""):
    global trainer_list
    global trainer_id_list

    trainer_id_list = [i.id for i in trainer_list]  # Updates trainer_id_list
    trainer = trainer_list[trainer_id_list.index(ctx.author.id)]
    while True:
        team = ', '.join([str(i) for i in trainer.team])
        while True:
            msg = await ctx.author.send(f"Which emoji do you want to teach: {team}")
            index = await select_one_from_list(ctx.author, ctx.author, [0, 1, 2, 3], selection_message=msg)
            if trainer.team[index] is None or trainer.team[index].movePool is None:
                await ctx.author.send("Whatever you're smokin, I want some of that. Try again")
            else:
                break

        msg = await ctx.author.send("Choose the move you want to learn. "
                                    "Learned moves cannot be learned a second time, so choose wisely\n"
                                    "No pressure")
        await asyncio.sleep(1)
        await msg.delete()
        answer = await select_one_from_list(ctx.author, ctx.author, trainer.team[index].movePool)

        msg = await ctx.author.send("Choose which move slot you want to place it in? (Replaced move will be forgotten)")
        await asyncio.sleep(1)
        await msg.delete()
        msg = await ctx.author.send("Current move slots:\n"
                                    f"0: {trainer.team[index].move1}\n"
                                    f"1: {trainer.team[index].move2}\n"
                                    f"2: {trainer.team[index].move3}\n"
                                    f"3: {trainer.team[index].move4}\n")
        replace = await select_one_from_list(ctx.author, ctx.author, [0, 1, 2, 3], selection_message=msg)
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

        msg = await ctx.author.send("Do you want to teach your team moves again?")
        if await select_one_from_list(ctx, ctx.author, [True, False], ['👍', '👎'], msg):
            msg = await ctx.author.send("Ah shit, here we go again")
            await asyncio.sleep(1)
            await msg.delete()
        else:
            msg = await ctx.author.send("The curse have been broken, I have been freed from my duties")
            await asyncio.sleep(1)
            await msg.delete()
            break

    with open('TrainerList.dat', 'wb') as f:  # AUTOSAVES!!!
        pickle.dump(trainer_list, f)


@client.command()
async def emoji_team(ctx):
    global trainer_list
    global trainer_id_list

    if await check(ctx, "Sorry but I am a sucker for crowds, your DM won't work. Move to an emojimon channel instead"):
        return

    if ctx.author.id not in trainer_id_list:
        await ctx.send("You don't even have an emoji yet, become a trainer first")
        return

    trainer = trainer_list[trainer_id_list.index(ctx.author.id)]
    for i in trainer.team:
        if i is not None:
            await ctx.author.send(file=discord.File(fp=i.stat_graph(), filename='image.png'))
            await ctx.author.send("Move set:\n"+", ".join([i.move1, i.move2, i.move3, i.move4]))


@tasks.loop(seconds=10)
async def spawn_loop():
    """
    The loop coroutine for spawning, it will have a chance of 1/6 every 10 seconds
    """
    rand = random.randint(1, 6)
    if rand == 6:
        await spawn()
    else:
        pass


async def spawn():
    """
    Responsible for spawning a pokemon. Spawn windows starts every 10 seconds for testing purposes.
    """
    global trainer_list
    global trainer_id_list
    global emoji_list

    channel = client.get_channel(746939037297934426)
    pokeball = client.get_emoji(769571475061473302)

    trainer_id_list = [i.id for i in trainer_list]

    emoji = random.choice(emoji_list)

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
        reaction, user = await client.wait_for('reaction_add', timeout=5.0, check=check)
        trainer = trainer_list[trainer_id_list.index(user.id)]
        if user.id in trainer_id_list:
            await msg.delete()
            await user.send('You got the pokemon, you\'re now responsible for its taxes')
            await channel.send(f'{user.name} has caught the pokemon')
            team_add = trainer.add_team(emoji)
            if team_add[0]:
                message = await channel.send(
                    "Which will you send to inventory: " + ', '.join(str(i) for i in trainer.team))
                slot = await select_one_from_list(user, user, [0, 1, 2, 3], selection_message=message)
                trainer.change_team(slot, emoji)
                trainer.team[slot].hpGene = random.uniform(1, 2)
                trainer.team[slot].atkGene = random.uniform(1, 2)
                trainer.team[slot].defGene = random.uniform(1, 2)
                trainer.team[slot].speAtkGene = random.uniform(1, 2)
                trainer.team[slot].speDefGene = random.uniform(1, 2)
                trainer.team[slot].speGene = random.uniform(1, 2)
                trainer.team[slot].recalculateStats()

            if team_add[1] is not None:
                channel.send(f"{user.name} has earned the achievement {team_add[1]}")

            with open('TrainerList.dat', 'wb') as f:  # AUTOSAVES!!!
                pickle.dump(trainer_list, f)

        else:
            await reaction.message.channel.send('Oops, it looks like you\'re not a trainer yet, and thus not qualified '
                                                'to catch this emojimon. Join the club using new_trainer command.')
    except asyncio.TimeoutError:
        await msg.delete()
        msg = await msg.channel.send('The pokemon slipped away')
        await asyncio.sleep(2)
        await msg.delete()


@client.command()
async def battle_challenge(ctx, target):
    """
    Command for challenging another user
    :param ctx: context parameter
    :param target: the challenged user
    todo: Restrict player from challenging self (unless if that player is me, because bug testing duh)
    todo: Add restrictions to ability usage
    """
    global trainer_id_list
    global trainer_list
    global emoji_list
    global local_time

    if await check(ctx, "Sorry but I am a sucker for crowds, your DM won't work. Move to an emojimon channel instead"):
        return

    reactions = ["👍", "👎"]
    responses = ["yes", "no"]

    if ctx.author.id not in trainer_id_list:
        await ctx.send("Sorry, you're not part of a club yet.\n "
                       "||But now you will, this is a forced initiation sucka||")
        await trainer_init(ctx, ctx.author)

    try:
        user = client.get_user(int(''.join([i for i in target if i.isdigit()])))
    except:
        await ctx.send("Target is not valid, make sure you are mentioning them with '@'")
        return

    if user == client.user:  # If the challenger is dumb enough to challenge a bot
        await ctx.send("No you dumbass I'm the referee not the player")
        return

    if user.id not in trainer_id_list:
        await ctx.send("Sorry, you're not part of a club yet.\n "
                       "||But now you will, this is a forced initiation sucka||")
        await trainer_init(ctx, user)

    await ctx.send(f"{ctx.author.name} has challenged {user.name} to a battle.")
    msg = await user.send(f'{ctx.author.name} has challenged you to a battle. Do you accept?')

    answer = await select_one_from_list(user, user, responses, emojis=reactions, selection_message=msg)
    if answer == responses[0]:
        await battle(ctx, trainer_list[trainer_id_list.index(ctx.author.id)],
                     trainer_list[trainer_id_list.index(user.id)])
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

    challenger_user = client.get_user(challenger.id)
    challenged_user = client.get_user(challenged.id)

    msg = await ctx.send(f"{challenger.name}, please pick your battle emoji:\n"
                         f"0: {challenger.team[0]}\n"
                         f"1: {challenger.team[1]}\n"
                         f"2: {challenger.team[2]}\n"
                         f"3: {challenger.team[3]}")

    i1 = await select_one_from_list(ctx, challenger_user, [0, 1, 2, 3], selection_message=msg)
    challenger_emoji = challenger.team[i1]

    msg = await ctx.send(f"{challenged.name}, please pick your battle emoji:\n"
                         f"0: {challenged.team[0]}\n"
                         f"1: {challenged.team[1]}\n"
                         f"2: {challenged.team[2]}\n"
                         f"3: {challenged.team[3]}")

    i2 = await select_one_from_list(ctx, challenged_user, [0, 1, 2, 3], selection_message=msg)
    challenged_emoji = challenged.team[i2]

    index1 = challenger_emoji.emojiNumber
    index2 = challenged_emoji.emojiNumber

    msg = await ctx.send(f"Battle's starting! {challenger.name} has summoned {challenger_emoji.name}")
    image = await ctx.send(file=discord.File(fp=battle_screen(index1), filename='image.jpeg'))
    await asyncio.sleep(3)
    await msg.delete()
    await image.delete()

    msg = await ctx.send(f"{challenged.name} has summoned {challenged_emoji.name}")  # Referencing emoji from index
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
    # Moves are referenced by name, so todo: reference moves in emoji class as actual move object
    challenger_moves = \
        [challenger_emoji.move1, challenger_emoji.move2, challenger_emoji.move3, challenger_emoji.move4]
    challenged_moves = \
        [challenged_emoji.move1, challenged_emoji.move2, challenged_emoji.move3, challenged_emoji.move4]

    # Damage modifier from effect:
    clrMod = 1
    cldMod = 1

    """
    calc will always have the format: message, damage, heal, and whether the move is one time only
    """
    while True:
        move_chosen = await select_one_from_list(ctx, challenger_user, challenger_moves)
        msg = await ctx.send(f"{challenger_emoji.name} used {move_chosen}")
        # Type check:
        if move_chosen.moveEffect[0] is not "H":  # Normal attack
            image = await ctx.send(file=discord.File(fp=battle_screen(index1, index2, "gun1"), filename='Image.jpeg'))
            calc = clrMod*damage_calculation(challenger_emoji, challenged_emoji, move_chosen)
            challenged_hp -= calc[1]  # This is the damage dealt
        elif move_chosen.moveEffect[0] is "H":  # Healing attack
            calc = heal_calc(challenger_emoji, challenged_emoji, move_chosen)
            challenger_hp += calc[2]
            challenged_hp -= calc[1]
        if calc[3]:
            challenger_moves.remove(move_chosen)
        await asyncio.sleep(3)
        await msg.delete()
        msg = await ctx.send(
            f"The move {calc[0]}, dealt {calc[2]} damage. {challenged_emoji.name} has {challenged_hp} hp left"
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
                    break
                elif challenger.team[i].name == challenger_emoji.name:
                    await ctx.send(
                        f"{challenger.name}'s {challenger.team[i].add_xp(challenged_emoji.level, True, True)}")

                else:
                    await ctx.send(
                        f"{challenger.name}'s {challenger.team[i].add_xp(challenged_emoji.level // 2, False, True)}")

                if challenger.team[i].check_evolve():
                    ogname = challenger.team[i].name
                    await ctx.send(f"What's this? {challenger.team[i].name} is having a seizure?!")
                    level = challenger.team[i].level
                    challenger.team[i] = emoji_list[index1 + 1]
                    challenger.team[i].level = level
                    await ctx.send(f"{ogname} has ascended into a {challenger.team[i].name}")

                #  Losing Challenged team will also be rewarded
                if challenged.team[i].name == challenged_emoji.name:
                    await ctx.send(
                        f"{challenged.name}'s {challenged.team[i].add_xp(challenger_emoji.level // 2, True, True)}")
                elif challenged.team[i] is None:
                    break
                else:
                    await ctx.send(
                        f"{challenged.name}'s {challenged.team[i].add_xp(challenger_emoji.level // 4, False, True)}")

                if challenged.team[i].check_evolve():
                    ogname = challenged.team[i].name
                    await ctx.send(f"What's this? {challenged.team[i].name} is having a seizure?!")
                    level = challenged.team[i].level
                    challenged.team[i] = emoji_list[index1 + 1]
                    challenged.team[i].level = level
                    await ctx.send(f"{ogname} has ascended into a {challenged.team[i].name}")

            challenger.add_w()
            challenged.add_l()

            with open('TrainerList.dat', 'wb') as f:  # AUTOSAVES!!!
                pickle.dump(trainer_list, f)

            break
        await asyncio.sleep(3)
        await image.delete()

        # Challenged trainer's turn
        move_chosen = await select_one_from_list(ctx, challenged_user, challenged_moves)
        msg = await ctx.send(f"{challenged_emoji.name} used {move_chosen}")
        # No need for a second move_chosen cuz it's turn_based anyways

        # Type check:
        if move_chosen.moveEffect[0] is not "H":  # Normal attack for now
            image = await ctx.send(file=discord.File(fp=battle_screen(index1, index2, "knife2"), filename='Image.jpeg'))
            calc = cldMod * damage_calculation(challenged_emoji, challenger_emoji, move_chosen)
            challenger_hp -= calc[1]
        elif move_chosen.moveEffect[0] is "H":  # Healing attack
            calc = heal_calc(challenged_emoji, challenger_emoji, move_chosen)
            challenged_hp += calc[2]
            challenger_hp -= calc[1]
        if calc[3]:
            challenger_moves.remove(move_chosen)

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
                    break
                elif challenged.team[i].name == challenged_emoji.name:
                    await ctx.send(
                        f"{challenged.name}'s {challenged.team[i].add_xp(challenger_emoji.level*2, True, True)}")
                else:
                    await ctx.send(
                        f"{challenged.name}'s {challenged.team[i].add_xp(challenger_emoji.level // 2, False, True)}")

                if challenged.team[i].check_evolve():
                    await ctx.send(f"What's this? {challenged.team[i].name} is having a seizure?!")
                    level = challenged.team[i].level
                    challenged.team[i] = emoji_list[index1 + 1]
                    challenged.team[i].level = level
            challenger.add_l()
            challenged.add_w()
            with open('TrainerList.dat', 'wb') as f:  # AUTOSAVES!!!
                pickle.dump(trainer_list, f)
            break
        await asyncio.sleep(3)
        await image.delete()


async def trainer_init(ctx, user, message=None):
    """
    Handles trainer sign up
    :param ctx: the context parameter (this is the discord server, not the user's dm)
    :param user: the user we want to subject to a lifetime of animal abuse
    :param message: rn it's nothing, todo: make the message sent customizable, just in case
    :return:
    """
    global trainer_list
    global trainer_id_list
    global emoji_list

    if user.id in trainer_id_list:
        user.send("You already are a trainer, how much cocaine did you smoke today? Shoo! Get the fuck out.")
        return

    reactions = ["👍", "👎"]
    responses = ["yes", "no"]
    starter_emojis = [emoji_list[1], emoji_list[4], emoji_list[809]]
    # 4 will become an absolute powerhouse at level 50
    # 809 is a great glass cannon for early game, however evolves into an ultra powerful emoji (2nd evo is trash tho),
    # however you will def die if you are challenged by a strong emoji
    # 1 is a great tank wizard, best for punishing glass cannons challenger, however, it evolves into shit

    msg = await user.send(f"{user.name}, you are not currently a trainer, do you want to join?")
    answer = await select_one_from_list(user, user, responses, reactions, selection_message=msg)
    if answer == "yes":
        msg = await user.send(f"Please pick your starter emoji:\n"
                              f"0: {starter_emojis[0]}\n"
                              f"1: {starter_emojis[1]}\n"
                              f"2: {starter_emojis[2]}\n")
        emoji_picked = await select_one_from_list(user, user, starter_emojis, selection_message=msg)
        trainer_list.append(Trainer(user.name, user.id, emoji_picked, local_time.strftime("%x")))
        trainer_id_list.append(user.id)

        trainer = trainer_list[trainer_id_list.index(user.id)]
        trainer.team[0].hpGene = random.uniform(1, 2)
        trainer.team[0].atkGene = random.uniform(1, 2)
        trainer.team[0].defGene = random.uniform(1, 2)
        trainer.team[0].speAtkGene = random.uniform(1, 2)
        trainer.team[0].speDefGene = random.uniform(1, 2)
        trainer.team[0].speGene = random.uniform(1, 2)
        trainer.team[0].recalculateStats()

        with open('TrainerList.dat', 'wb') as f:  # AUTOSAVES!!!
            pickle.dump(trainer_list, f)

        await user.send(f"Welcome to the club {user.name}.")
        await ctx.send(f"Welcome to the club {user.name}.")
    else:
        await user.send(f'Alright then, guess not')
        await ctx.send(f'{user.name} did not become a trainer as he/she/they/pronoun did not give consent.')
        return


async def check(ctx, msg=None):
    """
    Check if channel is a DM
    :param ctx: context variable
    :param msg: message sent if it is in fact DM
    :return:
    """
    if isinstance(ctx.channel, discord.channel.DMChannel):
        if msg is not None:
            await ctx.send(msg)
        return True

    return False


async def select_one_from_list(messageable, author, lst, emojis=None, selection_message=None):
    """
    Lets a discord user select an item from a list using reactions.
    Returns the selected item.
    Can raise ValueError and asyncio.TimeoutError.
    """
    if emojis is None:
        emojis = ['0️⃣',
                  '1️⃣',
                  '2️⃣',
                  '3️⃣',
                  '4️⃣',
                  '5️⃣',
                  '6️⃣',
                  '7️⃣',
                  '8️⃣',
                  '9️⃣']
        emojis = emojis[:len(lst)]

    if len(lst) != len(emojis):
        raise ValueError(f'Lengths of lst and emojis are not equal ({len(lst)} != {len(emojis)})')

    if selection_message is None:
        # concatenate each line into a single message before sending
        messages = [f"{author.name}, choose the following:"]
        for emoji, item in zip(emojis, lst):
            messages.append(f'{emoji} {item}')
        selection_message = await messageable.send('\n'.join(messages))

    # react with one emoji for each item
    for emoji in emojis:
        await selection_message.add_reaction(emoji)

    # wait for confirmation from author
    def check1(reaction, user):
        return user == author and reaction.message.id == selection_message.id and str(reaction.emoji) in emojis

    reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check1)

    selected = lst[emojis.index(str(reaction.emoji))]
    await selection_message.delete()  # Delete Spam
    return selected


client.run(TOKEN)
