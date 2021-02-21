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
        effective = "super effective"
    elif typeEffectiveness >= 1:
        effective = "effective"
    else:
        effective = "not very effective"

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

    hit = random.uniform(0.0, 1.0)

    if hit > moveAcc:
        print("WHIFF!")
        return 'very far off, you should try prescription glasses', 0

    damageSway = random.uniform(0.8, 1.2)

    if hitType == "Physical":
        return effective, int((((moveDam * (
                attackingEmoji.atkStat / defendingEmoji.defStat)) ** universalDamageMod) / 5) * typeEffectiveness * stabMod * damageSway)
    else:
        return effective, int((((moveDam * (
                attackingEmoji.specialAtkStat / defendingEmoji.specialDefStat)) ** universalDamageMod) / 5) * typeEffectiveness * stabMod * damageSway)


if __name__ == '__main__':
    with open("CompleteEmojiDex.dat", "rb") as f:
        emoji_list = pickle.load(f)

    print(damage_calculation(emoji_list[1411], emoji_list[1412], 'Legendary Sword')[1])