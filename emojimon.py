import random
import pickle
import matplotlib.pyplot as plt
from math import pi
import io
from PIL import Image, ImageEnhance


class move:
    moveName = ""
    moveType = ""
    movePower = 0
    moveAccuracy = 0
    moveEffect = ""
    moveHitType = ""


class Emoji:
    # basic information
    name = ""
    type = ""
    emojiNumber = 0
    imageReference = ""
    level = 0
    evolution = ""  # Name of evolved emoji
    evolutionLevel = 0

    # xp and leveling
    currentXp = 0
    neededXp = 0
    levelingMod = 1.0

    # Genes and stats gained upon level up, range from 0.2 to 5 naturally, stats are calculated with this and genes
    hpGain = 1.0;
    atkGain = 1.0
    defGain = 1.0
    speAtkGain = 1.0
    speDefGain = 1.0
    speGain = 1.0

    hpGene = 1.0  # range of 1 to 2
    atkGene = 1.0
    defGene = 1.0
    speAtkGene = 1.0
    speDefGene = 1.0
    speGene = 1.0

    # stats
    currentHp = 0
    attackMod = 1.0
    defenseMod = 1.0
    specialAttackMod = 1.0
    specialDefenseMod = 1.0
    speedMod = 1.0
    dodgeMod = 1.0

    # stat calc and genes, these are used in conjunction with the above
    maxHp = 0
    atkStat = 0
    defStat = 0
    specialAtkStat = 0
    specialDefStat = 0
    speedStat = 0
    dodgeChance = 1.0

    # moves
    move1 = ""
    move2 = ""
    move3 = ""
    move4 = ""

    def __init__(self, indexNum):
        self.emojiNumber = indexNum
        self.imageReference = "Emoji" + indexNum.__str__()
        self.name = RandomWord()
        self.type = RandomType()
        self.level = random.randint(1, 50)
        # Evolutions will be handled out of initialization
        self.evolution = ""
        self.evolutionLevel = 0

        self.levelingMod = random.uniform(1.0, 3.0)
        self.neededXp = int(self.level * 100 * self.levelingMod)

        self.hpGain = random.uniform(0.2, 5)
        self.atkGain = random.uniform(0.2, 5)
        self.defGain = random.uniform(0.2, 5)
        self.speAtkGain = random.uniform(0.2, 5)
        self.speDefGain = random.uniform(0.2, 5)
        self.speGain = random.uniform(0.2, 5)

        self.hpGene = random.uniform(1, 2)
        self.atkGene = random.uniform(1, 2)
        self.defGene = random.uniform(1, 2)
        self.speAtkGene = random.uniform(1, 2)
        self.speDefGene = random.uniform(1, 2)
        self.speGene = random.uniform(1, 2)

        self.maxHp = int(self.level * self.hpGain * self.hpGene)
        self.atkStat = int(self.level * self.atkGain * self.atkGene)
        self.defStat = int(self.level * self.defGain * self.defGene)
        self.specialAtkStat = int(self.level * self.speAtkGain * self.speAtkGene)
        self.specialDefStat = int(self.level * self.speDefGain * self.speDefGene)
        self.speedStat = int(self.level * self.speGain * self.speGene)
        self.dodgeChance = random.uniform(1.0, 5.0)

        self.moveLearnDictionary = {}
        self.movePool = []

        self.xp = [0, int(self.level**1.2)]

    def __str__(self):
        return self.name

    def recalculateStats(self):

        self.maxHp = int(self.level * self.hpGain * self.hpGene)
        self.atkStat = int(self.level * self.atkGain * self.atkGene)
        self.defStat = int(self.level * self.defGain * self.defGene)
        self.specialAtkStat = int(self.level * self.speAtkGain * self.speAtkGene)
        self.specialDefStat = int(self.level * self.speDefGain * self.speDefGene)
        self.speedStat = int(self.level * self.speGain * self.speGene)

    def add_xp(self, exp, battle: bool, win: bool):
        self.xp[0] += exp
        if self.xp[0] >= self.xp[1]:
            while True:
                self.level_up()
                self.xp = [self.xp[0] - self.xp[1], int(self.level**1.2)]
                if self.xp[0] < self.xp[1]:
                    break
            return f'{self.name} has leveled up to level {self.level}!'
        if not battle:
            return None
        if win:
            return f'{self.name} has won the fight and escaped PTSD, *for now*'
        else:
            return f'{self.name} has gained XP'

    def level_up(self):
        """
        Deals with leveling up the emoji, involving raise level by one, as well as maybe improve stats
        and learn new moves
        todo: implement stat change
        """
        self.level += 1
        for move_name in self.moveLearnDictionary.items():
            if move_name[0] not in self.movePool:
                if move_name[1] <= self.level:
                    self.movePool.append(move_name[0])

        self.recalculateStats()

    def check_evolve(self):
        if self.level >= self.evolutionLevel and self.evolution is not None:
            return True
        return False

    def stat_graph(self):
        """
        Return a spider graph that visualizes the stats of the emoji
        """
        # number of variable
        categories = ["HP", "ATK", "DEF", "SATK", "SDEF", "SPD", "DGE"]
        N = len(categories)

        # we need to repeat the first value to close the circular graph:
        values = [self.maxHp/10,self.atkStat/10, self.defStat/10,
                  self.specialAtkStat/10, self.specialDefStat/10, self.speedStat*40/350,
                  self.dodgeChance*40/5, self.maxHp/10]

        # What will be the angle of each axis in the plot? (we divide the plot / number of variable)
        angles = [n / float(N) * 2 * pi for n in range(N)]
        angles += angles[:1]

        # Initialise the spider plot
        ax = plt.subplot(111, polar=True)

        # Draw one axe per variable + add labels labels yet
        plt.xticks(angles[:-1], categories, color='black', size=15)
        # Draw ylabels
        ax.set_rlabel_position(0)
        plt.yticks([10, 20, 30], ["10", "20", "30"], color="black", size=10)
        plt.ylim(0, 40)
        # Plot data
        ax.plot(angles, values, linewidth=2, linestyle='solid')
        # Fill area
        ax.fill(angles, values, 'b', alpha=0.5)
        plt.title(f"Level {self.level} {self.name}'s Stats:", color="white", size=10)
        output = io.BytesIO()
        b = io.BytesIO()
        plt.savefig(output, format='png', transparent=True)
        plt.clf()

        # Adding background
        plot = Image.open(output)
        emojipic = Image.open(f'Emojis/Emoji{self.emojiNumber}.png')
        background = ImageEnhance.Color(emojipic.copy())
        background = background.enhance(0.7)

        background = background.resize(plot.size)
        background.paste(plot, mask=plot)
        background.save(b, format='png')

        output.seek(0)
        b.seek(0)
        return b


class Trainer:
    """
    Basically the class for trainer, allows for much better data storage and access.
    It also makes things cleaner
    todo: Integrate discord user in here
    """
    def __init__(self, name, discord_id: int, beginner_emoji: Emoji, date_started: str):
        """
        The Trainer class constructor
        :param name: self-explanatory
        :param discord_id: todo: change this to Discord user class object instead to make room for expansions
        :param beginner_emoji: The first emoji to be used (starter pick wont take place here to allow for dev usage)
        :param date_started: Why not, might be necessary later
        """
        self.name = name
        self.beginner_emoji = beginner_emoji
        self.team = [self.beginner_emoji, None, None, None]
        self.achievements = []
        self.gym_badges = []
        self.wins = 0
        self.losses = 0
        self.emojis_caught = 0
        self.date_started = date_started
        self.id = discord_id
        self.role = 'player'  # If it is the name of one of the emoji type, the person is a gym leader
        self.inventory = []

    def __str__(self):
        return self.name

    def add_w(self):
        """
        Any win adds should be through this method to check for achievements
        :returns achievement if you earned any, if not it returns None
        """
        achievement = None
        self.wins += 1
        if self.wins == 10:
            self.achievements.append("All that Ws")
            achievement = "All that Ws"
        if self.wins == 50:
            self.achievements.append("Apex Emoji")
            achievement = "Apex Emoji"
        return achievement

    def add_l(self):
        """
        Any loss adds should be through this method to check for achievements
        :returns achievement if you earned any, if not it returns None
        """
        achievement = None
        self.losses += 1
        if self.losses == 10:
            self.achievements.append("The bane of emojis")
            achievement = "The bane of emojis"
        if self.losses == 50:
            self.achievements.append("Did it for the achievement")
            achievement = "Did it for the achievement"

        return achievement

    def add_team(self, new_emoji: Emoji):
        """
        Add an emoji to team
        :returns True if team is full, False if it isn't, as well as achievement if it was achieved
        """
        achievement = None
        self.emojis_caught += 1

        if self.emojis_caught == 10:
            self.achievements.append("Emoji Collector")
            achievement = "Emoji Collector"
        if self.emojis_caught == 20:
            self.achievements.append("Emoji Hoarder")
            achievement = "Emoji Hoarder"
        if self.emojis_caught == 50:
            self.achievements.append("Emoji Trafficking")
            achievement = "Emoji Trafficking"

        for i in range(len(self.team)):
            if self.team[i] is None:
                self.team[i] = new_emoji
                self.team[i].hpGene = random.uniform(1, 2)
                self.team[i].atkGene = random.uniform(1, 2)
                self.team[i].defGene = random.uniform(1, 2)
                self.team[i].speAtkGene = random.uniform(1, 2)
                self.team[i].speDefGene = random.uniform(1, 2)
                self.team[i].speGene = random.uniform(1, 2)
                self.team[i].recalculateStats()
                return False, achievement

        return True, achievement  # Team is full and one has to be replaced

    def change_team(self, slot, emoji):
        self.inventory.append(self.team[slot])
        self.team[slot] = emoji


if __name__ == '__main__':
    with open('CompleteEmojiDex.dat', 'rb') as f:
        data_list = pickle.load(f)

    im = Image.open(data_list[1412].stat_graph())
    im.show()