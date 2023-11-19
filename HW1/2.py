from __future__ import annotations
from mimetypes import init
from typing import List

TILES = []
DJK = False

class Tile:
    def __init__(self, u, r, d, l, i):
        self.u = u
        self.r = r
        self.d = d
        self.l = l
        self.index = i

    def __str__(self) -> str:
        return f"{self.index}: {self.u} {self.r} {self.d} {self.l}"

    def get_min(self):
        return min(self.u, self.r, self.d, self.l)


class State:
    def __init__(self, n, m, prev_state:State=None, x=None, y=None, tile:Tile=None):
        self.n = n
        self.m = m

        if not prev_state:
            self.table = [[None for _ in range(m)] for _ in range(n)]
            self.tile_counts = 0
            self.dist = 0
            self.unused_tiles = TILES
        else:
            self.table = [[t for t in row] for row in prev_state.table]
            self.table[x][y] = tile
            self.tile_counts = prev_state.tile_counts + 1
            self.dist = 1e18
            self.unused_tiles = [t for t in prev_state.unused_tiles if t != tile]

        self.all_tiles = [item for sublist in self.table for item in sublist]

        h = 0
        for tile in self.unused_tiles:
            h += tile.get_min()

        if not prev_state:
            h -= TILES[0].get_min()
    
        self.heuristic = h


        self.hash = hash(tuple(self.all_tiles))
    
    def is_table_empty(self):
        return not bool(self.tile_counts)

    def get_tiles(self):
        return self.all_tiles

    def get_heuristic(self):
        return self.heuristic

    def get_f(self):
        if DJK: # djk
            return self.dist
        else: # a*
            return self.get_heuristic() + self.dist

    def is_goal(self):
        return self.tile_counts == self.n * self.m

    def get_unused_tiles(self):
        return self.unused_tiles

    def get_insertion_cost(self, x, y, tile):
        if self.table[x][y]:
            return None, False
        
        ok_edges = []
        if x > 0: # up
            next_tile = self.table[x-1][y]
            if next_tile and next_tile.d == tile.u:
                ok_edges.append(tile.u)

        if y > 0: # left
            next_tile = self.table[x][y-1]
            if next_tile and next_tile.r == tile.l:
                ok_edges.append(tile.l)

        if x+1 < self.n: # down
            next_tile = self.table[x+1][y]
            if next_tile and next_tile.u == tile.d:
                ok_edges.append(tile.d)

        if y+1 < self.m: # right
            next_tile = self.table[x][y+1]
            if next_tile and next_tile.l == tile.r:
                ok_edges.append(tile.r)

        if not ok_edges:
            return None, False
        
        return min(ok_edges), True

    def __eq__(self, other) -> bool:
        return self.hash == other.hash
    
    def __lt__(self, other):
        return self.get_f() < other.get_f()

    def __str__(self) -> str:
        s = "-------------\n"
        for i in range(self.n):
            for j in range(self.m):
                s += f"{'-' if not self.table[i][j] else self.table[i][j].index} "
            s += "\n"
        s += "-------------\n"
        return s
        

class Game:
    def __init__(self, n, m, tiles, initial_tile):
        self.n = n
        self.m = m
        self.tiles = tiles
        self.initial_tile = initial_tile
        self.best_state = None
    
    def get_neighs(self, state: State):
        neighs = []
        if state.is_table_empty():
            for i in range(self.n):
                for j in range(self.m):
                    neighs.append((State(self.n, self.m, state, i, j, self.initial_tile), 0))
        else:
            not_used_tiles = state.get_unused_tiles()
            for tile in not_used_tiles:
                for i, row in enumerate(state.table):
                    for j, cell in enumerate(row):
                        if not cell:
                            cost, ok = state.get_insertion_cost(i, j, tile)
                            if ok:
                                s = State(self.n, self.m, state, i, j, tile)
                                neighs.append((s, cost))

        return neighs


    def search(self):
        st: List[State] = [State(self.n, self.m)]
        explored = []

        c = 0
        while st:
            state = min(st)
            st.remove(state)
            explored.append(state)
            c += 1

            # print("State" ,state.get_f(), "\n", state)

            if state.is_goal():
                self.best_state = state
                return state, c

            for neigh, weight in self.get_neighs(state):
                if neigh in st:
                    for a in st:
                        if a == neigh:
                            neigh.dist = a.dist

                if neigh in explored:
                    continue
                if state.dist + weight < neigh.dist:
                    if neigh in st:
                        st.remove(neigh)
                    neigh.dist = state.dist + weight
                    st.append(neigh)

        return None


if __name__ == "__main__":
    n, m = map(int, input().split())

    TILES = []
    for i in range(n*m):
        u, r, d, l = map(int, input().split())
        TILES.append(Tile(u, r, d, l, i))

    game = Game(n, m, TILES, TILES[0])
    game.search()
    goal =game.best_state
    print(goal.get_f())
    # print(goal)
    # print(goal.get_heuristic())
    # print(goal.dist)

