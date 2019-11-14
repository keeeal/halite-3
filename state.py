
import copy
import numpy as np

from hashlib import sha1

class State(object):
    '''A state is a hashable wrapper of a halite game object.'''

    def __init__(self, game):
        super(State, self).__init__()
        self.game = game
        self.view = {}

    def __getattr__(self, attr):
        return getattr(self.game, attr)

    def __hash__(self):
        return hash(sha1(self.get_array()).hexdigest())

    def __copy__(self):
        return State(self.game)

    def __deepcopy__(self, memo):
        return State(copy.deepcopy(self.game, memo))

    def update_view(self):
        gmap = self.game_map

        for j in range(gmap.height):
            for i in range(gmap.width):
                self.view[-1] = np.array([[[cell.halite_amount/1000.
                        for cell in row] for row in gmap._cells]])

        for id, player in self.players.items():
            self.view[id] = np.zeros((4, gmap.height, gmap.width))

            shipyard = player.shipyard
            i, j = shipyard.position.x, shipyard.position.y
            self.view[id][0,j,i] = 1.

            for dropoff in self.me.get_dropoffs() + [shipyard]:
                i, j = dropoff.position.x, dropoff.position.y
                self.view[id][1,j,i] = 1.

            for ship in player.get_ships():
                i, j = ship.position.x, ship.position.y
                self.view[id][2:4,j,i] = 1., ship.halite_amount/1000.

        return self

    def get_array(self, view_as=None):
        ids = sorted(self.players)

        if view_as:
            if view_as.id in ids:
                ids = [view_as.id] + [id for id in ids if id != view_as.id]
            else:
                return ValueError('Viewer ID not found.')

        if not self.view:
            self.update_view()

        return np.concatenate([self.view[id] for id in [-1] + ids])
