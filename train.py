
import random, pickle
import numpy as np

from itertools import count

from halite import Halite
from model import Model

def main():
    halite = Halite(32, 32)
    model = Model(Halite)

    n_episodes = 100
    examples = []

    for iteration in count():
        for episode in range(n_episodes):
            examples += halite.play('train_bot')

if __name__ == '__main__':
    main()
