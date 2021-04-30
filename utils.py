import discord
from emojimon import *
from datetime import datetime
from PIL import Image, ImageEnhance
from io import BytesIO
import requests
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, RegularPolygon
from matplotlib.path import Path
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D


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


def effect_check(attackingEmoji: Emoji, defendingEmoji: Emoji, movesName):
    global moveListTemp
    effectType = ''

    for x in range(len(moveListTemp)):
        if movesName == moveListTemp[x].moveName:
            effectType = moveListTemp[x].moveEffect[0]

    if effectType == "K" or effectType == "H":
        return heal_calc(attackingEmoji, defendingEmoji, movesName)
    else:
        return damage_calculation(attackingEmoji, defendingEmoji, movesName)


def damage_calculation(attackingEmoji: Emoji, defendingEmoji: Emoji, movesName):
    """
    Calculate damage for a battle
    :param attackingEmoji:
    :param defendingEmoji:
    :param movesName:
    :return: the effectiveness of the attack, as well as damage output
    todo: rebalance
    """
    global moveListTemp
    global newData

    for y in range(1, len(newData)):
        for x in range(1, len(newData)):
            if newData[y][0] == attackingEmoji.type and newData[0][x] == defendingEmoji.type:
                typeEffectiveness = newData[y][x]

    moveType = ""
    moveDam = 0
    moveAcc = 0.0
    hitType = ""
    effective = ''
    if typeEffectiveness >= 2.5:
        effective = "was super effective"
    elif typeEffectiveness >= 1:
        effective = "was effective"
    else:
        effective = "was not very effective"

    universalDamageMod = 1.2

    for x in range(len(moveListTemp)):
        if movesName == moveListTemp[x].moveName:
            moveType = moveListTemp[x].moveType
            moveDam = moveListTemp[x].movePower
            moveAcc = moveListTemp[x].moveAccuracy
            hitType = moveListTemp[x].moveHitType

    stabMod = 1.0

    if moveType == attackingEmoji.type:
        stabMod = 1.2

    hit = random.uniform(0.0, 1.0) + defendingEmoji.dodgeChance/25

    if hit > moveAcc:
        print("WHIFF!")
        return 'very far off, you should try prescription glasses', 0, 0, False

    if attackingEmoji.speedStat < 210:
        damageSway = random.uniform(0.8, 1.2)
    else:
        damageSway = random.uniform(0.7, attackingEmoji.speedStat/175)

    if hitType == "Physical":
        return effective, int((((moveDam * (
                attackingEmoji.atkStat / defendingEmoji.defStat)) ** universalDamageMod) / 5) * typeEffectiveness * stabMod * damageSway), 0, False
    else:
        return effective, int((((moveDam * (
                attackingEmoji.specialAtkStat / defendingEmoji.specialDefStat)) ** universalDamageMod) / 5) * typeEffectiveness * stabMod * damageSway), 0, False


def heal_calc(attackingEmoji: Emoji, defendingEmoji: Emoji, movesName):
    """
    Heal the emoji and may deal some damage to the other emoji
    :param attackingEmoji:
    :param defendingEmoji:
    :param movesName:
    :return: message, how much it heals, how much damage, and whether the move will be disabled
    """
    global moveListTemp
    moveType = ""
    moveDam = 0
    moveAcc = 0.0
    healType = ''
    for x in range(len(moveListTemp)):
        if movesName == moveListTemp[x].moveName:
            moveDam = moveListTemp[x].movePower
            moveAcc = moveListTemp[x].moveAccuracy
            healType = moveListTemp[x].moveEffect[1]

    if healType is '1':  # Heal based on movePower alone
        heal = random.uniform(0.0, moveDam/100)*0.2*attackingEmoji.maxHp
        msg = f'healed {attackingEmoji.name} by {round(heal)} hp'
        return msg, 0, round(heal), False
    if healType is '2':  # Like 1 but heals up to 50% and can only be used once
        heal = random.uniform(0.0, moveDam / 100) * 0.5 * attackingEmoji.maxHp
        msg = f'healed {attackingEmoji.name} by {round(heal)} hp and disabled itself'
        return msg, 0, round(heal), True
    if healType is '3':  # Like 1 but only heals 10% max and also damages opponents by half of what it should be
        heal = random.uniform(0.0, moveDam / 100) * 0.1 * attackingEmoji.maxHp
        dmg = damage_calculation(attackingEmoji, defendingEmoji, movesName)/2
        msg = f'healed {attackingEmoji.name} by {round(heal)} hp'
        return msg, dmg, round(heal), False
    if healType is '4':  # Gamble, either heal a flat rate of 50% (once) or get damaged based on what it would be by def
        heal = random.choice([0.5*attackingEmoji.maxHp, 0])
        if heal != 0:
            msg = f'healed {attackingEmoji.name} by {round(heal)} hp and disabled itself'
            return msg, 0, round(heal), True
        else:
            dmg = damage_calculation(defendingEmoji, attackingEmoji, movesName)
            msg = f'failed to heal {attackingEmoji.name} and killed his dignity instead, reduced its health by {dmg}'
            return msg, 0, -dmg, False
    if healType is '5':  # For now it's like 1
        heal = random.uniform(0.0, moveDam / 100) * 0.2 * attackingEmoji.maxHp
        msg = f'healed {attackingEmoji.name} by {round(heal)} hp'
        return msg, 0, round(heal), False


def battle_screen(index1, index2=None, effect=None):
    b = BytesIO()
    path1 = f'Emojis/Emoji{index1}.png'
    stadium = Image.open('poke_stadium.jpg')
    img1 = Image.open(path1)
    img1 = img1.resize((400, 400))
    background = stadium.copy()
    background.paste(img1, (300, 300), img1)

    try:
        path2 = f'Emojis/Emoji{index2}.png'
        img2 = Image.open(path2)
        img2 = img2.resize((400, 400))
        background.paste(img2, (1250, 300), img2)
    except:
        pass

    # Check if there are any effects, rn they include: knife, squirt and gun.
    # If the number after is 1, the challenger on the left is carrying out the attack.
    try:
        effect_img = Image.open(f'Emojis/{effect[:-1]}.png')
        if effect[-1:] == "2":
            print('reversed')
            effect_img = effect_img.transpose(method=Image.FLIP_LEFT_RIGHT)

        effect_img = effect_img.resize((400, 400))
        background.paste(effect_img, (800, 300), effect_img)
    except:  # Since this will be used a controlled environment, I don't have to worry much about this
        pass

    background.save(b, format='jpeg')
    b.seek(0)
    return b


def guess_poke(url: str):
    b = BytesIO()
    response = requests.get(url)

    img = Image.open(BytesIO(response.content))
    img = img.resize((500, 500))

    img_guess = Image.open('guess the pokemon.png')
    img_backup = img_guess.copy()

    enhancer = ImageEnhance.Brightness(img)
    img_dark = enhancer.enhance(0)
    layer = img_dark
    img_backup.paste(layer, (350, 300), mask=layer)
    img_backup.save(b, format='jpeg')
    b.seek(0)
    return b