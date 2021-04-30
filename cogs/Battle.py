import asyncio
from discord.ext import commands
from emojimon import *
from utils import *
from image_edit import *


class Battle(commands.Cog):
    """
    Cogs module responsible for the main loop of the battle system
    """

    def __init__(self, client):
        self.client = client
        self.challenger = Trainer
        self.defender = Trainer
        self.challengeEmoji = Emoji
        self.defendEmoji = Emoji

    @commands.command()
    async def battle(self, ctx, challenger: IdTrainer, defender: IdTrainer):
        self.challenger = challenger
        self.defender = defender

        # Setup for battle
        msg = await ctx.send(f" {challenger.name}, please pick your battle emoji:\n"
                             f"0: {challenger.team[0]}\n"
                             f"1: {challenger.team[1]}\n"
                             f"2: {challenger.team[2]}\n"
                             f"3: {challenger.team[3]}")

        i1 = await select_one_from_list(self.client, ctx, self.client.get_user(challenger.id), [0, 1, 2, 3], selection_message=msg)
        self.challengeEmoji = copy.deepcopy(challenger.team[i1])

        msg = await ctx.send(f"{defender.name}, please pick your battle emoji:\n"
                             f"0: {challenger.team[0]}\n"
                             f"1: {challenger.team[1]}\n"
                             f"2: {challenger.team[2]}\n"
                             f"3: {challenger.team[3]}")

        i2 = await select_one_from_list(self.client, ctx, self.client.get_user(defender.id), [0, 1, 2, 3], selection_message=msg)
        self.defendEmoji = copy.deepcopy(defender.team[i2])

        # Reset emojis' hp
        self.challengeEmoji.currentHp = self.challengeEmoji.maxHp
        self.defendEmoji.currentHp = self.defendEmoji.maxHp

        # Introductions
        msg = await ctx.send(f"Battle's starting!{str(self.challenger)} has summoned {self.challengeEmoji.name}")
        image = await ctx.send(
            file=discord.File(fp=battle_screen(self.challengeEmoji.emojiNumber), filename='image.jpeg'))
        await asyncio.sleep(3)
        await msg.delete()
        await image.delete()

        msg = await ctx.send(f"{str(self.defender)} has summoned {self.defendEmoji.name}")
        image = await ctx.send(
            file=discord.File(fp=battle_screen(self.challengeEmoji.emojiNumber, self.defendEmoji.emojiNumber),
                              filename='image.jpeg')
        )
        await asyncio.sleep(3)
        await msg.delete()
        await image.delete()

        while not self.gameOver():
            # Index num of the emojis
            index1 = i1
            index2 = i2

            # The move chosen by the emojis, the order will be changed based on speed
            move_1 = await select_one_from_list(
                self.client, ctx, self.client.get_user(challenger.id), self.challengeEmoji.move_list())
            move_2 = await select_one_from_list(
                self.client, ctx, self.client.get_user(challenger.id), self.challengeEmoji.move_list())
            if self.challengeEmoji.speedStat < self.defendEmoji.speedStat:
                move_temp = move_1
                move_1 = move_2
                move_2 = move_temp
                index_temp = index1
                index1 = index2
                index2 = index_temp
            image = await ctx.send(file=discord.File(fp=battle_screen(index1, index2, "gun1"), filename='Image.jpeg'))
            calc = effect_check(challenger_emoji, challenged_emoji, move_chosen)

    async def battle_loop(self, player):
        """
        The main battle loop of the game
        """
        pass

    async def reward(self, emoji: Emoji):
        pass

    def gameOver(self):
        return self.defendEmoji.currentHp == 0 or self.challengeEmoji.currentHp == 0


def setup(client):
    client.add_cog(Battle(client))
    print("Battle Extension Loaded")
