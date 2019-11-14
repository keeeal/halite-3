
from subprocess import run

class Halite(object):
    '''This object initiates halite games using the binary excecutable.'''

    def __init__(self, height, width, binary='./halite'):
        super(Halite, self).__init__()
        self.binary = binary
        self.size = self.height, self.width = height, width

    def play(self, bot_1, bot_2=None, bot_3=None, bot_4=None,
                    seed=None, replay_directory=None, timeout=False):
        bot_2 = bot_1 if bot_2 is None else bot_2

        command = [self.binary]
        command += '--height', str(self.height), '--width', str(self.width)

        if seed:
            command += '--seed',

        if replay_directory:
            command += '--replay-directory', replay_directory
        else:
            command += '--no-replay',

        if not timeout:
            command += '--no-timeout',

        for bot in bot_1, bot_2, bot_3, bot_4:
            if bot:
                bot = bot if bot.endswith('.py') else bot + '.py'
                command += 'python3 ' + str(bot),

        run(command)
