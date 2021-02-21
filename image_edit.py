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

"""
Just some general pic editing stuff
"""


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


if __name__ == "__main__":
    battle_screen(0, 0, "gun1")