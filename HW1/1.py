
def djk(adjacency_list, initial_distances, destination, parents=None, coeff=1, compare_with=None):

    distances = initial_distances.copy()

    fringe = set()
    for i in range(len(initial_distances)):
        fringe.add((distances[i], i))

    while fringe:
        g, v = min(fringe)
        fringe.remove((g, v))

        if v == destination:
            break

        for u, w in adjacency_list[v]:
            if distances[v] + w * coeff < distances[u]:
                fringe.remove((distances[u], u))
                distances[u] = distances[v] + w * coeff
                if parents:
                    parents[u] = v
                fringe.add((distances[u], u))
                
                if compare_with and u == destination and distances[u] < compare_with:
                    return distances, parents, True

    return distances, parents, False


def main():
    K = int(input())
    for _ in range(K):
        n, m = map(int, input().split())

        adjacency_list = [[] for _ in range(n)]
        for i in range(m):
            u, v, g = map(int, input().split())
            u -= 1
            v -= 1
            adjacency_list[u].append((v, g))
            adjacency_list[v].append((u, g))


        T = int(input())
        temp = list(map(int, input().split()))
        criminals = [a-1 for a in temp]

        C = int(input())
        temp = list(map(int, input().split()))
        cars = [a-1 for a in temp]

        s, g = map(int, input().split())
        s -= 1
        g -= 1

        distances_from_tintin, parents, _ = djk(adjacency_list,
        							initial_distances=[0 if i == s else 1e18 for i in range(n)], 
        							parents=[-1 for _ in range(n)], 
        							destination=g)


        distances_from_criminals, _, found_tintin = djk(adjacency_list, 
        								initial_distances=[0 if i in criminals else 1e18 for i in range(n)], 
        								destination=g, 
        								compare_with=distances_from_tintin[g])
        
        if not found_tintin:
            initial_car_distnaces = [g if i in cars else 1e18 for i, g in enumerate(distances_from_criminals)]
            distances_from_bs, _, found_tintin = djk(adjacency_list,
            								initial_distances=initial_car_distnaces, 
        									coeff=1/2, 
        									destination=g, 
        									compare_with=distances_from_tintin[g])


        if found_tintin or distances_from_tintin[g] > min(distances_from_criminals[g], distances_from_bs[g]):
            print("Poor Tintin")
        else:
            print(distances_from_tintin[g])
            path = [g+1]
            while g != s:
                g = parents[g]
                path.append(g+1)
            
            print(len(path))
            print(*path[::-1])


if __name__ == '__main__':
    main()
