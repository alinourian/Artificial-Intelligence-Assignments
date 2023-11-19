import sys
import json
import re


def get_paths(answers, graph, start, end, path, visited):
    path.append(start)
    if start == end:
        answers.append(path)
        return
    visited[start] = True
    for i in graph[start]:
        if not visited[i]:
            get_paths(answers, graph, i, end, list(path), list(visited))
    return answers


def check_type(temp, graph):
    v1 = None
    v2 = None
    if temp[1] in graph[temp[0]]:
        v1 = 1
    else:
        v1 = 0
    if temp[2] in graph[temp[1]]:
        v2 = 1
    else:
        v2 = 0
    if v1 == 1 and v2 == 1:
        return "causal_chain"
    if v1 == 1 and v2 == 0:
        return "common_effect"
    if v1 == 0 and v2 == 0:
        return "causal_chain"
    if v1 == 0 and v2 == 1:
        return "common_cause"


def check_descendents(index, graph, evidence, visited):
    visited[index] = True
    if index in evidence:
        return True
    for i in graph[index]:
        if check_descendents(i, graph, evidence, list(visited)):
            return True
    return False


def check_path(path, graph, evidence, checked):
    if len(path) < 3:
        return "active"
    for i in range(len(path) - 2):
        temp = path[i:i + 3]
        if str(temp) in checked.keys():
            if checked.get(str(temp)) == 'inactive':
                return checked.get(str(temp))
        state = check_type(temp, graph)

        # print(temp)
        # print('temp:', temp[1], evidences)
        if state == "causal_chain" and temp[1] in evidence:
            checked[str(temp)] = "inactive"
            return "inactive"
        if state == "common_cause" and temp[1] in evidence:
            checked[str(temp)] = "inactive"
            return "inactive"
        if state == "common_effect" and not check_descendents(temp[1], graph, evidence, [False] * len(graph)):
            checked[str(temp)] = "inactive"
            return "inactive"
        checked[str(temp)] = "active"
    return "active"


def my_replace(input):
    if re.match("\\d+", input.group(0)):
        return input.group(0)
    return "\"" + input.group(0) + "\""


def true_false(number, length):
    def binary_to_tf(input):
        temp = input.group(0)
        if temp == '0':
            return 't'
        else:
            return 'f'

    return re.sub("\\d", binary_to_tf, ("{0:0" + str(length) + "b}").format(number))


def are_matched(prob1: str, prob2: str, indexes1, indexes2):
    for i in range(len(indexes1)):
        if prob1[indexes1[i]] != prob2[indexes2[i]]:
            return False
    return True


def get_tables(tables, var):
    answer = []
    for i, j in enumerate(tables):
        if var in j.variables:
            answer.append(i)
    return answer


def join_tables(tables, indexes, hidden=""):
    if len(indexes) == 1 and hidden != "":
        tables[indexes[0]].eliminate(hidden)
    while len(indexes) > 1:
        temp_table = Table.join(tables[indexes[0]], tables[indexes[1]])
        tables.append(temp_table)
        indexes.append(len(tables) - 1)
        delete_table1 = tables[indexes[0]]
        delete_table2 = tables[indexes[1]]
        tables.remove(delete_table1)
        tables.remove(delete_table2)
        indexes.remove(indexes[0])
        indexes.remove(indexes[0])
        for i in range(len(indexes)):
            indexes[i] = indexes[i] - 2

    if hidden != "":
        tables[len(tables) - 1].eliminate(hidden)


def query(input, tables, variables):
    temp_tables = [i.copy() for i in tables]
    a = input
    evidence = a[1]
    evidence_value = a[2]
    unknown = a[0]
    hidden = [i for i in variables if i not in evidence + unknown]
    for i in hidden:
        to_be_joined = get_tables(temp_tables, i)
        join_tables(temp_tables, to_be_joined, i)
    # print([i.variables for i in temp_tables])
    join_tables(temp_tables, list(range(len(temp_tables))))
    # print([i.variables for i in temp_tables])
    return temp_tables[0].get_value(unknown, evidence, evidence_value)


class Table:
    @staticmethod
    def join(t1, t2):
        temp_variables = list(set(t1.variables) & set(t2.variables))
        indexs_t1 = t1.get_indexes(temp_variables)
        indexs_t2 = t2.get_indexes(temp_variables)
        new_table = Table()
        new_table.set_variables(t1.variables, t2.variables, temp_variables)
        for i in t1.probs.keys():
            for j in t2.probs.keys():
                if are_matched(i, j, indexs_t1, indexs_t2):
                    new_table.join_probs(i, j, t1.probs.get(i), t2.probs.get(j), indexs_t1, indexs_t2)
        return new_table

    @staticmethod
    def are_matched(prob, evidence, evidence_index):
        for i, j in enumerate(evidence):
            if j != prob[evidence_index[i]]:
                return False
        return True

    def get_value(self, variables, evidence, evidence_value):
        def tf_from_01(input):
            if input == 1:
                return "t"
            return "f"

        answer = []
        evidence_indexes = [self.variables.index(i) for i in evidence]
        evidence_values = "".join([tf_from_01(i) for i in evidence_value])
        indexes_unknown = [self.variables.index(i) for i in variables]
        for k, v in self.probs.items():
            if Table.are_matched(k, evidence_values, evidence_indexes):
                answer.append(("".join([k[i] for i in indexes_unknown]), v))
        return answer

    def eliminate(self, var):
        if var not in self.variables:
            return
        index = self.variables.index(var)
        new_probs = dict()
        for i in self.probs.keys():
            temp = list(i)
            del temp[index]
            temp = "".join(temp)
            if temp in new_probs.keys():
                new_probs[temp] += self.probs.get(i)
            else:
                new_probs[temp] = self.probs.get(i)
        self.probs = new_probs
        del self.variables[index]

    def get_indexes(self, variables):
        ansewer = []
        for i in variables:
            ansewer.append(self.variables.index(i))
        return ansewer

    def join_probs(self, probs1, probs2, value1, value2, indexes1, indexes2):
        new_prob = [probs1[i] for i in indexes1]
        new_prob += [probs1[i] for i in range(len(probs1)) if i not in indexes1]
        new_prob += [probs2[i] for i in range(len(probs2)) if i not in indexes2]
        self.probs["".join(new_prob)] = value1 * value2

    def set_variables(self, variables1, variables2, intersection_variables):
        self.variables = [x for x in intersection_variables]
        self.variables += [x for x in variables1 if x not in intersection_variables]
        self.variables += [x for x in variables2 if x not in intersection_variables]

    def __init__(self, input=""):
        if input == "":
            self.variables = []
            self.probs = dict()
            return
        a = json.loads(re.sub("\\w+", my_replace, input))
        self.variables = [a[0]] + a[1]
        self.probs = dict()
        for i in range(2 * len(a[2])):
            if i in range(len(a[2])):
                self.probs[true_false(i, len(a[1]) + 1)] = a[2][i]
            else:
                self.probs[true_false(i, len(a[1]) + 1)] = 1 - a[2][i - len(a[2])]

    def copy(self):
        temp = Table()
        temp.variables = list(self.variables)
        temp.probs = dict(self.probs)
        return temp

    def __str__(self):
        return str(self.variables)


def print_result(answer):
    sum = 0
    for i in answer:
        sum += i[1]
    final_answer = []
    for i in range(len(answer) // 2):
        final_answer.append((answer[i][0], answer[i][1] / sum))
    for i in range(len(answer) // 2, len(answer)):
        final_answer.append((answer[i][0], 1 - final_answer[i - len(answer) // 2][1]))
    for i in final_answer:
        if i[0] == 't':
            print("{value:.2f}".format(value=i[1]))


n = int(input())
directed_graph = [[] for _ in range(n)]
undirected_graph = [[] for _ in range(n)]
parent_graph = [[] for _ in range(n)]
cpts = []
for i in range(n):
    x = input().split(' ')
    if x[0] == '':
        x = []
    for j in x:
        e2, e1 = i, int(j)
        e1 -= 1
        directed_graph[e1].append(e2)
        parent_graph[e2].append(e1)
        undirected_graph[e1].append(e2)
        undirected_graph[e2].append(e1)
    inn = input().split(' ')
    cpt = list(map(float, inn))
    cpts.append(cpt)
evidences = []
ev_vals = []
for x in input().split(','):
    matcher = re.match('(\d+)->(\d+)', x)
    evidences.append(int(matcher.group(1)) - 1)
    ev_vals.append(int(matcher.group(2)))
start, end = map(int, input().split(' '))
start -= 1
end -= 1
temp = get_paths([], undirected_graph, start, end, [], [False] * n)
checked = dict()
for i in temp:
    state = check_path(i, directed_graph, evidences, checked)
    if state == "active":
        print('dependent')
        break
else:
    print("independent")
tables = []
variables = []
for i in range(n):
    tempp = f'[{i}, {str(parent_graph[i])}, {str(cpts[i])}]'
    tables.append(Table(tempp))
    variables.append(i)
answer = query([[start], evidences, ev_vals], tables, variables)
print_result(answer)
answer = query([[end], evidences, ev_vals], tables, variables)
print_result(answer)
