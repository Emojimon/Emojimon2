import pickle
import json
from emojimon import Emoji, move, Trainer


"""
This whole file is dedicated to changing values in the files
"""


def move_load(string: str):
    with open("move_data.json", "r") as f:
        data_dict = json.load(f)
    return data_dict[string]


def add_item():
    with open("CompleteMoveList.dat", "rb") as f:
        data_list = pickle.load(f)

    laser = move()
    laser.moveName = "Gentle Roast"
    laser.moveType = "Australian"
    laser.movePower = 15
    laser.moveAccuracy = 0.98
    laser.moveEffect = "Z0"
    laser.moveHitType = "Emotional"

    data_list.append(laser)

    with open("CompleteMoveList.dat", "wb") as f:
        pickle.dump(data_list, f)


def check_data():
    with open("CompleteEmojiDex.dat", "rb") as f:
        data_list = pickle.load(f)

    with open("CompleteMoveList.dat", "rb") as f:
        move_list = pickle.load(f)

    with open("TrainerList.dat", 'rb') as f:
        trainer_list = pickle.load(f)

    trainer_list = []

    with open("TrainerList.dat", "wb") as f:
        pickle.dump(trainer_list, f)


def pickle_2_json():
    with open("CompleteEmojiDex.dat", "rb") as f:
        data_dict = pickle.load(f)

    #with open("emoji_data.json", "w") as f:


if __name__ == '__main__':
    check_data()

