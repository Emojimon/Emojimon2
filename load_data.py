from emojimon import *
import copy
import pickle
import json

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

    with open("emoji_data.json", "w") as f:
        json.dump([i.__dict__ for i in data_dict], f, indent=4)

def trainer_update():
    with open('trainers_data.json', 'w') as f:
        json.dump([encode(i) for i in trainerList()], f, indent=4)


if __name__ == '__main__':
    def encode(obj: Trainer):
        cls_dict = copy.deepcopy(obj.__dict__)
        for key, value in cls_dict.items():
            if isinstance(value, Emoji):
                cls_dict[key] = copy.deepcopy(value.__dict__)
            elif isinstance(value, list) and not not value:
                if isinstance(value[0], Emoji):
                    cls_dict[key] = [copy.deepcopy(i.__dict__) for i in value if isinstance(i, Emoji)]
        return cls_dict

    clsdict = encode(trainerList()[0])
    trainer = Trainer(clsdict)
    print(type(trainer.beginner_emoji))

