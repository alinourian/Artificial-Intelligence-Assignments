from random import *
from copy import deepcopy
from collections import defaultdict


class CSP(object):
    def __init__(self, variables = [], adjList = {}, domains = {}):
        self.variables = variables
        self.adjList = adjList
        self.domains = domains

    def restore_domains(self, removals):
        """ Undo a supposition and all inferences from it """
        for X in removals:
            self.domains[X] |= removals[X]

    # The following methods are used in min_conflict algorithm
    def nconflicts(self, X1, x, assignment):
        """
        Return the number of conflicts X1 = x has with other variables
        Subclasses may implement this more efficiently
        """
        def conflict(X2):
            return self.conflicts(X1, x, X2, assignment[X2])
        return sum(conflict(X2) for X2 in self.adjList[X1] if X2 in assignment)

    def conflicted_vars(self, current):
        """ Return a list of variables in conflict in current assignment """
        return [var for var in self.variables
                if self.nconflicts(var, current[var], current) > 0]


class SudokuCSP(CSP):
    def conflicts(self, i1, j1, x, i2, j2, y):
        k1 = i1 // 3 * 3 + j1 // 3
        k2 = i2 // 3 * 3 + j2 // 3
        return x == y and ( i1 == i2 or j1 == j2 or k1 == k2 )


class SudokuSolver(object):
    def __addEdge__(self, i, j, adjList):
        k = i // 3 * 3 + j // 3
        for num in range(9):
            if num != i:
                adjList[(i, j)].add((num, j))
            if num != j:
                adjList[(i, j)].add((i, num))
            row = num//3 + k//3 * 3
            col = num%3 + k%3 * 3
            if row != i or col != j:
                adjList[(i, j)].add((row, col))

    def buildCspProblem(self, board):
        adjList = defaultdict(set)
        # Build graph (contraints)
        for i in range(9):
            for j in range(9):
                self.__addEdge__(i, j, adjList)
        # Set domains
        variables = []
        assigned = []
        domains = {}
        for i in range(9):
            for j in range(9):
                if board[i][j] == '.':
                    domains[(i, j)] = set(range(9))
                    variables.append((i, j))
                else:
                    domains[(i, j)] = set([int(board[i][j]) - 1])
                    assigned.append((i, j))
        return SudokuCSP(variables, adjList, domains), assigned

    def solveSudoku(self, board):
        """
        :type board: List[List[str]]
        :rtype: void Do not return anything, modify board in-place instead.
        """
        pass


def AC3(csp, queue=None, removals=defaultdict(set)):
    # Return False if there is no consistent assignment
    if queue is None:
        queue = [(Xt, X) for Xt in csp.adjList for X in csp.adjList[Xt]]
    # Queue of arcs of our concern
    while queue:
        # Xt --> Xh Delete from domain of Xt
        (Xt, Xh) = queue.pop()
        if remove_inconsistent_values(csp, Xt, Xh, removals):
            if not csp.domains[Xt]:
                return False
            # NOTE: Next two lines only for binary "!=" constraint
            elif len(csp.domains[Xt]) > 1:
                continue
            for X in csp.adjList[Xt]:
                if X != Xt:
                    queue.append((X, Xt))
    return True

def remove_inconsistent_values(csp, Xt, Xh, removals):
    # Return True if we remove a value
    revised = False
    # If Xt=x conflicts with Xh=y for every possible y, eliminate Xt=x
    for x in csp.domains[Xt].copy():
        for y in csp.domains[Xh]:
            if not csp.conflicts(*Xt, x, *Xh, y):
                break
        else:
            csp.domains[Xt].remove(x)
            removals[Xt].add(x)
            revised = True
    return revised

def makeArcQue(csp, Xs):
    return [(Xt, Xh) for Xh in Xs for Xt in csp.adjList[Xh]]


class AC3SudokuSolver(SudokuSolver):
    def solveSudoku(self, board):
        """
        :type board: List[List[str]]
        :rtype: void Do not return anything, modify board in-place instead.
        """
        # Build CSP problem
        csp, assigned = self.buildCspProblem(board)
        # Enforce AC3 on initial assignments
        AC3(csp, makeArcQue(csp, assigned))
        # If there's still uncertain choices
        uncertain = []
        for i in range(9):
            for j in range(9):
                if len(csp.domains[(i, j)]) > 1:
                    uncertain.append((i, j))
        # Search with backtracking
        self.backtrack(csp, uncertain)
        # Fill answer back to input table
        for i in range(9):
            for j in range(9):
                if board[i][j] == '.':
                    try:
                        assert len(csp.domains[(i, j)]) == 1
                        board[i][j] = str( csp.domains[(i, j)].pop() + 1 )
                    except AssertionError:
                        print("Exception problem")
                        raise
    
    def backtrack(self, csp, uncertain):
        if not uncertain:
            return True
        X = uncertain.pop()
        removals = defaultdict(set)
        for x in csp.domains[X]:
            domainX = csp.domains[X]
            csp.domains[X] = set([x])
            if AC3(csp, makeArcQue(csp, [X]), removals):
                retval = self.backtrack(csp, uncertain)
                if retval:
                    return True
            csp.restore_domains(removals)
            csp.domains[X] = domainX
        uncertain.append(X)
        return False


class AC3MRVLCVSudokuSolver(AC3SudokuSolver):
    def count_conflict(self, csp, Xi, x):
        cnt = 0
        for X in csp.adjList[Xi]:
            if x in csp.domains[X]:
                cnt += 1
        return cnt

    def popMin(self, array, key):
        minimum, idx = float("inf"), 0
        for i in range(len(array)):
            if key(array[i]) < minimum:
                idx = i
                minimum = key(array[i])
        array[idx], array[-1] = array[-1], array[idx]
        return array.pop()

    def solveSudoku(self, board):
        """
        :type board: List[List[str]]
        :rtype: void Do not return anything, modify board in-place instead.
        """
        # Build CSP problem
        csp, assigned = self.buildCspProblem(board)
        # Enforce AC3 on initial assignments
        if not AC3(csp, makeArcQue(csp, assigned)):
            return False
        # If there's still uncertain choices
        uncertain = []
        for i in range(9):
            for j in range(9):
                if len(csp.domains[(i, j)]) > 1:
                    uncertain.append((i, j))
        # Search with backtracking
        if not self.backtrack(csp, uncertain):
            return False
        # Fill answer back to input table
        for i in range(9):
            for j in range(9):
                if board[i][j] == '.':
                    try:
                        assert len(csp.domains[(i, j)]) == 1
                        board[i][j] = str( csp.domains[(i, j)].pop() + 1 )
                    except AssertionError:
                        print("Exception problem")
                        raise
        return True

    def backtrack(self, csp, uncertain):
        if not uncertain:
            return True
        X = self.popMin(uncertain, key=lambda X: len(csp.domains[X]))
        removals = defaultdict(set)
        # Sort the values in domain in the order of LCV and loop in that order
        domainlist = list(csp.domains[X])
        domainlist.sort(key=lambda x: self.count_conflict(csp, X, x))
        for x in domainlist:
            domainX = csp.domains[X]
            csp.domains[X] = set([x])
            if AC3(csp, makeArcQue(csp, [X]), removals):
                retval = self.backtrack(csp, uncertain)
                if retval:
                    return True
            csp.restore_domains(removals)
            csp.domains[X] = domainX
        uncertain.append(X)
        return False


class SudokuGenerator:
    def __init__(self, solver, board):
        self.solver = solver
        self.board = board

    def generateSudoku(self):
        board = self.board
        solution = deepcopy(board)
        if self.solver.solveSudoku(solution):
            return board, solution
        return None, None


def show_results(gen):
    while True:
        board, solution = gen.generateSudoku()
        if board:
            print("\n".join(map(" ".join, solution)))
            break


if __name__ == "__main__":
    board = [['.'] * 9 for i in range(9)]
    for i in range(9):
            board[i] = input().split()
    gen = SudokuGenerator(AC3MRVLCVSudokuSolver(), board)
    show_results(gen)