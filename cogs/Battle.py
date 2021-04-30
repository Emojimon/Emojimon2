import asyncio
from discord.ext import commands
from emojimon import *
from utils import *


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

        if challenger is None or defender is None:
            await ctx.send("Sorry, you're not part of a club yet.\n "
                           "||But now you will, this is a forced initiation sucka||")
            await trainer_init(ctx, ctx.author, trainer_list, trainer_id_list, emoji_list)

        # Setup for battle
        msg = await ctx.send(f" {challenger.name}, please pick your battle emoji:\n"
                             f"0: {challenger.team[0]}\n"
                             f"1: {challenger.team[1]}\n"
                             f"2: {challenger.team[2]}\n"
                             f"3: {challenger.team[3]}")

        i1 = await select_one_from_list(self.client, ctx, self.client.get_user(challenger.id), [0, 1, 2, 3],
                                        selection_message=msg)
        self.challengeEmoji = copy.deepcopy(challenger.team[i1])

        msg = await ctx.send(f"{defender.name}, please pick your battle emoji:\n"
                             f"0: {challenger.team[0]}\n"
                             f"1: {challenger.team[1]}\n"
                             f"2: {challenger.team[2]}\n"
                             f"3: {challenger.team[3]}")

        i2 = await select_one_from_list(self.client, ctx, self.client.get_user(defender.id), [0, 1, 2, 3],
                                        selection_message=msg)
        self.defendEmoji = copy.deepcopy(defender.team[i2])

        # Reset emojis' hp
        self.challengeEmoji.currentHp = self.challengeEmoji.maxHp
        self.defendEmoji.currentHp = self.defendEmoji.maxHp

        # Introductions
        msg = await ctx.send(f"Battle's starting! {str(self.challenger)} has summoned {self.challengeEmoji.name}")
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
        await self.battle_loop(ctx)

    async def battle_loop(self, ctx):
        """
        The main battle loop of the game
        """
        while not await self.gameOver(ctx):
            # Index num of the emojis
            emoji_order = [self.challengeEmoji, self.defendEmoji]

            # The move chosen by the emojis, the order will be changed based on speed
            move_c = await select_one_from_list(
                self.client, ctx, self.client.get_user(self.challenger.id), self.challengeEmoji.move_list())
            move_d = await select_one_from_list(
                self.client, ctx, self.client.get_user(self.defender.id), self.defendEmoji.move_list())

            move_order = [move_c, move_d]

            if self.challengeEmoji.speedStat < self.defendEmoji.speedStat:
                move_order.reverse()
                emoji_order.reverse()

            for i in range(2):
                if await self.gameOver(ctx):
                    return
                msg = await ctx.send(f"{emoji_order[i]} used {move_order[i]}")
                # Shows the image
                image = await ctx.send(file=discord.File(
                    fp=battle_screen(emoji_order[i].emojiNumber, emoji_order[(i + 1) % 2].emojiNumber, "gun1"),
                    filename='Image.jpeg')
                )
                await asyncio.sleep(3)
                await msg.delete()

                # Calculate and do damage
                calc = effect_check(emoji_order[i], emoji_order[(i + 1) % 2], move_order[i])
                emoji_order[(i + 1) % 2].currentHp -= calc[1]
                await ctx.send(
                    f"The move {calc[0]}, dealt {calc[1]} damage. {emoji_order[(i + 1) % 2].name} has "
                    f"{emoji_order[(i + 1) % 2].currentHp} hp left"
                )

    async def reward(self, emoji: Emoji):
        pass

    async def gameOver(self, ctx):
        if self.defendEmoji.currentHp <= 0:
            await ctx.send(f"{self.defendEmoji.name} has fallen into depression.\n"
                           f"{str(self.challenger)} wins the battle.")
            return True
        if self.challengeEmoji.currentHp <= 0:
            await ctx.send(f"{self.challengeEmoji.name} has fallen into depression.\n"
                           f"{str(self.defender)} wins the battle.")
            return True
        else:
            return False


def setup(client):
    client.add_cog(Battle(client))
    print("Battle Extension Loaded")
