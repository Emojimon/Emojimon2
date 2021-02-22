import random
from emojimon import Emoji, move
import pickle

with open("CompleteMoveList.dat", "rb") as f:
    moveListTemp = pickle.load(f)

with open("TypeChart2dArray.dat", "rb") as f:
    newData = pickle.load(f)


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
            moveType = moveListTemp[x].moveType
            moveDam = moveListTemp[x].movePower
            moveAcc = moveListTemp[x].moveAccuracy
            healType = moveListTemp[x].moveHitType[1]
    if healType is '1':  # Heal based on movePower alone
        heal = random.uniform(0.0, moveDam/100)*0.2*attackingEmoji.maxHp
        msg = f'healed {attackingEmoji.name} by {heal} hp'
        return msg, 0, heal, False
    if healType is '2':  # Like 1 but heals up to 50% and can only be used once
        heal = random.uniform(0.0, moveDam / 100) * 0.5 * attackingEmoji.maxHp
        msg = f'healed {attackingEmoji.name} by {heal} hp and disabled itself'
        return msg, 0, heal, True
    if healType is '3':  # Like 1 but only heals 10% max and also damages opponents by half of what it should be
        heal = random.uniform(0.0, moveDam / 100) * 0.1 * attackingEmoji.maxHp
        dmg = damage_calculation(attackingEmoji, defendingEmoji, movesName)/2
        msg = f'healed {attackingEmoji.name} by {heal} hp'
        return msg, dmg, heal, False
    if healType is '4':  # Gamble, either heal a flat rate of 50% (once) or get damaged based on what it would be by def
        heal = random.choice([0.5*attackingEmoji.maxHp, 0])
        if heal != 0:
            msg = f'healed {attackingEmoji.name} by {heal} hp and disabled itself'
            return msg, 0, heal, True
        else:
            dmg = damage_calculation(defendingEmoji, attackingEmoji, movesName)
            msg = f'failed to heal {attackingEmoji.name} and killed his dignity instead, reduced its health by {dmg}'
            return msg, 0, -dmg, False
    if healType is '5':  # For now it's like 1
        heal = random.uniform(0.0, moveDam / 100) * 0.2 * attackingEmoji.maxHp
        msg = f'healed {attackingEmoji.name} by {heal} hp'
        return msg, 0, heal, False


if __name__ == '__main__':
    with open("CompleteEmojiDex.dat", "rb") as f:
        emoji_list = pickle.load(f)

    print(damage_calculation(emoji_list[1411], emoji_list[1412], 'Legendary Sword')[1])