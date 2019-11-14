
import hlt, math, copy

from halite import Halite

class Sim(object):
    def __init__(self, constants):
        super(Sim, self).__init__()
        self.constants = constants

    def next_state(self, state, action):
        state = copy.deepcopy(state)
        gmap = state.game_map

        def idx(entity):
            return entity.position.y, entity.position.x

        def delete(ship):
            gmap[ship].ship = None
            ship.owner._ships.pop(ship.id)

        def mine(ship, inspired=False):
            if inspired:
                ratio = self.constants.INSPIRED_EXTRACT_RATIO
            else:
                ratio = self.constants.EXTRACT_RATIO

            cell = gmap[ship]
            gained = extracted = math.ceil(cell.halite_amount/ratio)

            if extracted == 0 and cell.halite_amount > 0:
                gained = extracted = cell.halite_amount

            if extracted + ship.halite_amount > self.constants.MAX_HALITE:
                extracted = self.constants.MAX_HALITE - ship.halite_amount

            if inspired:
                gained += gained*self.constants.INSPIRED_BONUS_MULTIPLIER

            if self.constants.MAX_HALITE - ship.halite_amount < gained:
                gained = self.constants.MAX_HALITE - ship.halite_amount

            ship.halite_amount += gained
            cell.halite_amount -= extracted

        def move(ship, direction, inspired=False):
            if inspired:
                ratio = self.constants.INSPIRED_MOVE_COST_RATIO
            else:
                ratio = self.constants.MOVE_COST_RATIO

            cell = gmap[ship]
            cost = round(cell.halite_amount/ratio)

            if ship.halite_amount >= cost:
                ship.position = gmap.normalize(ship.position + direction)
                cell.ship, gmap[ship].ship = None, ship
                ship.halite_amount -= cost
                return True

            return False

        def convert(ship):
            cell = gmap[ship]
            cost = self.constants.DROPOFF_COST

            if me.halite_amount >= cost and not cell.structure:
                id = max(me._dropoffs) + 1 if len(me._dropoffs) else 0
                pos = hlt.Position(ship.position.x, ship.position.y)
                me._dropoffs[id] = hlt.entity.Dropoff(me, id, pos)
                cell.structure = me._dropoffs[id]
                me.halite_amount -= cost
                delete(ship)
                return True

            return False

        def spawn(yard):
            cost = self.constants.SHIP_COST

            if me.halite_amount >= cost:
                id = max(me._ships) + 1 if len(me._ships) else 0
                pos = hlt.Position(yard.position.x, yard.position.y)
                me._ships[id] = hlt.entity.Ship(me, id, pos, 0)
                gmap[yard].ship = me._ships[id]
                me.halite_amount -= cost
                return True

            return False

        def is_inspired(ship):
            enemies = 0
            open, closed = [], set()
            open.append((0, ship.position.y, ship.position.x))

            while len(open):
                dist, j, i = open[0]
                cell = gmap._cells[j][i]
                closed.add((j, i))
                open = open[1:]

                if cell.ship and cell.ship.owner is not ship.owner:
                    enemies += 1
                    if enemies >= self.constants.INSPIRATION_SHIP_COUNT:
                        return True

                if dist < self.constants.INSPIRATION_RADIUS:
                    for dj, di in hlt.Direction.get_all_cardinals():
                        _j, _i = (j + dj) % gmap.height, (i + di) % gmap.width
                        if (_j, _i) not in closed:
                            open.append((dist + 1, _j, _i))

            return False

        # ==== MY ACTIONS ==== #

        me = state.me

        for ship in me.get_ships():
            a = action[idx(ship)]

            if a < 4: # move
                mv = hlt.Direction.get_all_cardinals()[a]
                if move(ship, hlt.Position(*mv), inspired=is_inspired(ship)):
                    continue

            if a == 4: # make dropoff
                if convert(ship):
                    continue

            mine(ship, inspired=is_inspired(ship)) # stay still

        if action[idx(me.shipyard)] == 6: # new ship
            spawn(me.shipyard)

        # ==== ENEMIES ==== #

        for id in state.players:
            if id != me.id:
                for ship in state.players[id].get_ships():
                    mine(ship, inspired=is_inspired(ship)) # stay still

        # ==== COLLISIONS ==== #

        collisions = {}
        all_ships = (s for p in state.players.values() for s in p.get_ships())

        for ship in all_ships: # detect
            key, other = idx(ship), gmap[ship].ship

            if other and other is not ship:
                if key in collisions:
                    collisions[key].append(ship)
                else:
                    collisions[key] = [other, ship]

        for (j, i), collision in collisions.items(): # resolve
            cell = gmap._cells[j][i]
            h = cell.halite_amount + sum(s.halite_amount for s in collision)
            cell.halite_amount = min(h, hlt.constants.MAX_HALITE)

            for ship in collision:
                delete(ship)

        # ==== DROP HALITE ==== #

        for dropoff in me.get_dropoffs() + [me.shipyard]: # get halite
            cell = gmap[dropoff]
            me.halite_amount += cell.halite_amount
            cell.halite_amount = 0

            if cell.ship:
                me.halite_amount += cell.ship.halite_amount
                cell.ship.halite_amount = 0

        return state
