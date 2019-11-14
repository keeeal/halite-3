#!/usr/bin/env python3
# Python 3.6

import hlt, logging, os
import numpy as np

#from model import Model
from state import State
from tree import Tree
from sim import Sim

tree = Tree()
game = hlt.Game()
sim = Sim(hlt.constants)
game.ready('train_bot')
me = game.me

n_search = 25
next = None

while True:
    game.update_frame()
    gmap, me = game.game_map, game.me
    state = State(game)
    commands = []

    #for _ in range(n_search):
    #    tree.search(sim, state, model)

    #n = tree[tree.state_key(state)]['n']
    #pi = n/np.sum(n, axis=0)
    #examples.append([state, pi, None])

    if next:
        state_array = state.get_array(view_as=me)
        next_array = next.get_array(view_as=me)
        match = np.all(state_array == next_array)
        logging.info(match)

        if not match:
            for k in range(state_array.shape[0]):
                for j in range(state_array.shape[1]):
                    for i in range(state_array.shape[2]):
                        if state_array[k,j,i] != next_array[k,j,i]:
                            logging.info(('Error at ', (i,j,k)))
                            logging.info(('... Expected ', next_array[k,j,i]))
                            logging.info(('... Got      ', state_array[k,j,i]))

    action = np.random.randint(0, 7, (gmap.height, gmap.width))

    logging.info('--------------- ACTIONS -----------------')

    for ship in me.get_ships():
        i, j = ship.position.x, ship.position.y
        a = action[j,i]
        logging.info((i, j, a))

        if a < 4:
            mv = hlt.Direction.get_all_cardinals()[a]
            commands.append(ship.move(mv))
        elif a == 4 and not gmap[ship].structure:
            commands.append(ship.make_dropoff())
        else:
            commands.append(ship.stay_still())

    if action[me.shipyard.position.y, me.shipyard.position.x] == 6:
        commands.append(me.shipyard.spawn())

    next = sim.next_state(state, action)

    game.end_turn(commands)
