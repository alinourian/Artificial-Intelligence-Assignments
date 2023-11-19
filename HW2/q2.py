import random
from math import sqrt

import hardest_game


def play_game_AI(str, map_name='map1.txt'):
    game = hardest_game.Game(map_name=map_name, game_type='AI').run_AI_moves_graphic(moves=str)
    return game


def simulate(str, map_name='map1.txt'):
    game = hardest_game.Game(map_name=map_name, game_type='AI').run_AI_moves_no_graphic(moves=str)
    return game


def run_whole_generation(list_of_strs, N, map_name='map1.txt'):
    game = hardest_game.Game(map_name=map_name, game_type='AIS').run_generation(list_of_moves=list_of_strs, move_len=N)
    return game


def play_human_mode(map_name='map1.txt'):
    hardest_game.Game(map_name=map_name, game_type='player').run_player_mode()


length = 10
max_pop = 1000
mutation_rate = 0.1
ngen = 3000
gene_pool = ['w', 'a', 's', 'd', 'x']


def init_population(max_population, gene_pool, length):
    g = len(gene_pool)
    population = []
    for i in range(max_population):
        new_individual = [gene_pool[random.randrange(0, g)] for j in range(length)]
        population.append(new_individual)

    return population


population = init_population(max_pop, gene_pool, length * 2)


def mutate(x, gene_pool, pmut):
    if random.uniform(0, 1) >= pmut:
        return x

    n = len(x)
    g = len(gene_pool)
    c = random.randrange(0, n)
    r = random.randrange(0, g)

    new_gene = gene_pool[r]
    return x[:c] + [new_gene] + x[c + 1:]


def recombine(x, y):
    n = len(x)
    c = random.randrange(0, n)
    return x[:c] + y[c:]


def get_dist(x1, y1, x2, y2):
    return sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))


def get_min_dist(player, a):
    return a[1009 * player.x + player.y]


def fn(game, i, a):
    player = game.players[i][0]
    has_died = game.players[i][1]
    has_won = game.players[i][2]
    end = game.end
    dist_to_end = get_min_dist(player, a)
    point = 0
    point -= dist_to_end * 10
    goals = game.goals
    for j in range(len(goals)):
        if game.goal_player[j][i]:
            point += 400
        else:
            point -= get_dist(game.goals[j][0].x, game.goals[j][0].y, player.x + player.width / 2,
                              player.y + player.height / 2) * 5
    for j in range(len(game.enemies)):
        dist = get_dist(game.enemies[j].x, game.enemies[j].y, player.x + player.width / 2,
                 player.y + player.height / 2)
        if dist < 25:
            point -= 50
    if has_won:
        point += 100000000000
    if has_died != -1:
        point -= 30000
    return point


def sf(a):
    return a[0]


def select(r, population, fitnesses):
    selected = list()
    min_fitness = fitnesses[-1]
    fitnesses_sum = sum(fitnesses) - min_fitness * len(fitnesses)
    diff = fitnesses[0] - min_fitness
    for i in range(r):
        if fitnesses_sum == 0:
            selected.append(random.choice(population))
            continue
        prob = random.random()
        t = False
        for j in range(len(fitnesses)):
            if prob < diff / fitnesses_sum:
                selected.append(population[j])
                t = True
                break
            diff += (fitnesses[j] - min_fitness)
        if not t:
            selected.append(population[-1])
    return tuple(selected)


def bfs(game):
    a = dict()
    q = list()
    q.append([game.end.x, game.end.y])
    a[1009 * game.end.x + game.end.y] = 0
    end = game.end
    player = game.player
    while len(q) > 0:
        s = q.pop(0)
        t1 = False
        for l in game.Mlines:
            if s[1] + player.height > l.y1 and s[1] < l.y2 and s[0] + player.width <= l.x1 < s[
                0] + player.vel + player.width:
                t1 = True
                break
        if not t1:
            new_x = s[0] + player.vel
            new_y = s[1]
            new = new_x * 1009 + new_y
            if new not in a.keys():
                q.append([new_x, new_y])
                a[new] = a[1009 * s[0] + s[1]] + 1
        t1 = False
        for l in game.Mlines:
            if s[1] + player.height > l.y1 and s[1] < l.y2 and s[0] >= l.x1 > s[0] - player.vel:
                t1 = True
                break
        if not t1:
            new_x = s[0] - player.vel
            new_y = s[1]
            new = new_x * 1009 + new_y
            if new not in a.keys():
                q.append([new_x, new_y])
                a[new] = a[1009 * s[0] + s[1]] + 1
        t1 = False
        for l in game.Vlines:
            if s[0] + player.width > l.x1 and s[0] < l.x2 and s[1] + player.height <= l.y1 < s[
                1] + player.vel + player.height:
                t1 = True
                break
        if not t1:
            new_x = s[0]
            new_y = s[1] + player.vel
            new = new_x * 1009 + new_y
            if new not in a.keys():
                q.append([new_x, new_y])
                a[new] = a[1009 * s[0] + s[1]] + 1
        t1 = False
        for l in game.Vlines:
            if s[0] + player.width > l.x1 and s[0] < l.x2 and s[1] >= l.y1 > s[1] - player.vel:
                t1 = True
                break
        if not t1:
            new_x = s[0]
            new_y = s[1] - player.vel
            new = new_x * 1009 + new_y
            if new not in a.keys():
                q.append([new_x, new_y])
                a[new] = a[1009 * s[0] + s[1]] + 1
    return a


def genetic_algorithm_stepwise(population):
    best_gens = []
    best_scores = []
    l = length * 2
    for generation in range(ngen):
        print(generation)
        if generation % 4 == 3:
            pop2 = init_population(max_pop, gene_pool, length)
            for i in range(max_pop):
                population[i] = population[i] + pop2[i]
            l += length
        game = run_whole_generation(population, l)
        a = bfs(game)
        scores = list()
        for i in range(max_pop):
            scores.append([fn(game, i, a), i])
        scores = sorted(scores, reverse=True)
        population_sorted = list()
        fitnesses = list()
        for i in range(max_pop):
            population_sorted.append(population[scores[i][1]])
            fitnesses.append(scores[i][0])

        population = population_sorted
        population = [
            mutate(recombine(*select(2, population, fitnesses)), gene_pool, mutation_rate) for i
            in range(len(population))]
        members = [''.join(x) for x in population][:48]


# play_human_mode()
genetic_algorithm_stepwise(population)
