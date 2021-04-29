import discord
from emojimon import *
from datetime import datetime

async def select_one_from_list(client, messageable, author, lst, emojis=None, selection_message=None):
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


async def trainer_init(ctx, user, trainer_list, trainer_id_list, emoji_list):
    """
    Handles trainer sign up
    :param ctx: the context parameter (this is the discord server, not the user's dm)
    :param user: the user we want to subject to a lifetime of animal abuse
    :param message: rn it's nothing, todo: make the message sent customizable, just in case
    :return:
    """

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
        trainer_list.append(Trainer(user.name, user.id, emoji_picked, datetime.now().strftime("%x")))
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
