from contextlib import nullcontext
from random import randint
import string
from time import sleep
from turtle import pos
from zipfile import ZIP_BZIP2
from state import State

import numpy as np
import sys
import math
import time

class Result:
    def __init__(self):
        self.type = 0
        self.directions = np.empty_like(8, State)

class DfsPlan:
    def __init__(self, maxRows, maxColumns, goal, initialState, timeLeft, name = "none", mesh = "square"):

        self.walls = []
        self.maxRows = maxRows
        self.maxColumns = maxColumns
        self.initialState = initialState
        self.currentState = initialState
        self.goalPos = goal
        self.actions = []

        self.s = None
        self.a = None
        self.createdBackPath = False
        self.backPath = []
        self.timeLeft = timeLeft
        self.initialTime = timeLeft
        self.result = self.create_result_table()
        self.untried = self.create_untried_table()
        self.unbacktracked = self.create_unbacktracked_table()
            
    def create_result_table(self):
        result = []
        for i in range(self.maxColumns*self.maxRows):
            result.append(Result())
            result[i].directions = np.empty(8, State)
        return result

    def create_untried_table(self):
        untried = []
        for state in range(self.maxRows * self.maxColumns):
            actions = ["SO", "SE", "NO", "NE", "O", "L", "S", "N"]
            untried.append(actions)

        return untried

    def create_unbacktracked_table(self):
        unbacktracked = []

        for state in range(self.maxRows * self.maxColumns):
            unbacktracked.append([])

        return unbacktracked

    def setWalls(self, walls):
        row = 0
        col = 0
        for i in walls:
            col = 0
            for j in i:
                if j == 1:
                    self.walls.append((row, col))
                col += 1
            row += 1

    def updateCurrentState(self, state):
         self.currentState = state

    def isPossibleToMove(self, toState):
        if (toState.col < 0 or toState.row < 0):
            return False

        if (toState.col >= self.maxColumns or toState.row >= self.maxRows):
            return False
        
        if len(self.walls) == 0:
            return True
        
        if (toState.row, toState.col) in self.walls:
            return False

        delta_row = toState.row - self.currentState.row
        delta_col = toState.col - self.currentState.col

        if (delta_row !=0 and delta_col != 0):
            if (self.currentState.row + delta_row, self.currentState.col) in self.walls and (self.currentState.row, self.currentState.col + delta_col) in self.walls:
                return False
        
        return True

    def updateTime(self, timeLeft):
        self.timeLeft = timeLeft

    def convertStateToPos(self, state):
        return state.row * self.maxRows + state.col

    def convertActionToNumber(self, action):
        if (action == "SO"):
            return 0

        elif (action == "SE"):
            return 1

        elif (action == "NO"):
            return 2

        elif (action == "NE"):
            return 3

        elif (action == "O"):
            return 4

        elif (action == "L"):
            return 5

        elif (action == "S"):
            return 6

        else:
            return 7

    def convertNumberToAction(self, number):
        if (number == 0):
            return "SO"

        elif (number == 1):
            return "SE"

        elif (number == 2):
            return "NO"

        elif (number == 3):
            return "NE"

        elif (number == 4):
            return "O"

        elif (number == 5):
            return "L"

        elif (number == 6):
            return "S"

        else:
            return "N"

    def returnOppositeAction(self, action):
        if (action == "SO"):
            return "NE"

        elif (action == "SE"):
            return "NO"

        elif (action == "NO"):
            return "SE"

        elif (action == "NE"):
            return "SO"

        elif (action == "O"):
            return "L"

        elif (action == "L"):
            return "O"

        elif (action == "S"):
            return "N"

        else:
            return "S"

    def movePosition(self, currentState, action=None):
        if(action is None):
            action = self.a
        movePos = { "N" : (-1, 0),
                "S" : (1, 0),
                "L" : (0, 1),
                "O" : (0, -1),
                "NE" : (-1, 1),
                "NO" : (-1, -1),
                "SE" : (1, 1),
                "SO" : (1, -1)}
        s = State(currentState.row + movePos[action][0], currentState.col + movePos[action][1])
        return s if s.row < self.maxRows and s.col < self.maxColumns else State(-1, -1) 
    
    def getActionCost(self, action):
        """Retorna o custo da ação.
        @param action:
        @return custo da ação"""
        if (action=="nop"):
            return 0

        if (action == "N" or action == "L" or action == "O" or action == "S"):   
            return 1.0
        
        return 1.5

    def getTimePath(self, path):
        total = 0
        for i in reversed(range(len(path))):
            if(i == (len(path) - 1)):
                total += self.getActionCost(self.actionToDo(self.currentState, path[i]))
            else:
                total += self.getActionCost(self.actionToDo(path[i + 1], path[i]))
        return total

        
    def online_dfs_agent(self, currentState):
        movePos = { "N" : (-1, 0),
                "S" : (1, 0),
                "L" : (0, 1),
                "O" : (0, -1),
                "NE" : (-1, 1),
                "NO" : (-1, -1),
                "SE" : (1, 1),
                "SO" : (1, -1)}
        self.backPath = self.star_a_search(self.result, self.maxRows, self.maxColumns, currentState, self.initialState)
        timeToGoBack = self.getTimePath(self.backPath)
        print(f"Time to Go Back: {timeToGoBack}")

        if (self.timeLeft <= timeToGoBack + 10):
            if (currentState.row == 0 and currentState.col == 0):
                return
            else:
                if (self.createdBackPath == False):
                    self.createdBackPath = True
                    return

        else:

            if (self.s is not None):
                if (self.result[self.convertStateToPos(self.s)].directions[self.convertActionToNumber(self.a)] is None):
                    self.result[self.convertStateToPos(self.s)].directions[self.convertActionToNumber(self.a)] = currentState
                    for action in movePos:
                        try:
                            self.untried[self.convertStateToPos(self.movePosition(currentState, action))].pop(self.untried[self.convertStateToPos(self.movePosition(currentState, action))].index(self.returnOppositeAction(action)))
                        except:
                            pass
                    if(self.s.row != currentState.row or self.s.col != currentState.col):
                        self.result[self.convertStateToPos(currentState)].directions[self.convertActionToNumber(self.returnOppositeAction(self.a))] = self.s
                        try:
                            self.untried[self.convertStateToPos(currentState)].pop(self.untried[self.convertStateToPos(currentState)].index(self.returnOppositeAction(self.a)))
                        except:
                            print("Already tried")
                    if (self.isPossibleToMove(self.result[self.convertStateToPos(self.s)].directions[self.convertActionToNumber(self.a)])):
                        self.unbacktracked[self.convertStateToPos(currentState)].append(self.s)

            if (len(self.untried[self.convertStateToPos(currentState)]) == 0):

                if (len(self.unbacktracked[self.convertStateToPos(currentState)]) == 0):
                    return
                
                else:
                    print("Backtracking")
                    state_to_go_back = self.unbacktracked[self.convertStateToPos(currentState)].pop()
                    current = self.result[self.convertStateToPos(currentState)]
                    # for i in range(8):
                    #     if (current.directions[i].row == state_to_go_back.row and current.directions[i].col == state_to_go_back.col):
                    #         action_number = i
                    #         break
                    
                    # if (action_number == -1):
                    #     action_number = 0

                    # self.a = self.convertNumberToAction(action_number)
                    while(state_to_go_back.row == currentState.row and state_to_go_back.col == currentState.col):
                        state_to_go_back = self.unbacktracked[self.convertStateToPos(currentState)].pop()
                    self.a = self.actionToDo(currentState, state_to_go_back)
                    
            else:
                self.a = self.untried[self.convertStateToPos(currentState)].pop()

        self.s = currentState
        if(self.result[self.convertStateToPos(currentState)].type <= 0):
            self.result[self.convertStateToPos(currentState)].type = 5

        state = self.movePosition(currentState)

        return self.a, state

    def isInList(self, list, state):
        for i in range(len(list)):
            if(list[i].row == state.row and list[i].col == state.col):
                return True
        return False

    def star_a_search (self, map, rows, columns, initialState, finalState):
        euclideanDistance = {}
        travelledDistance = {}
        heuristic = {}
        parents = {}
        neighborStates = []
        foundSolution = False

        travelledDistance[initialState] = 0
        euclideanDistance[initialState] = self.returnEuclideanDistance(initialState, finalState)
        heuristic[initialState] = travelledDistance[initialState] + euclideanDistance[initialState]
        parents[initialState] = None

        fringe = []
        fringe.append(initialState)
        while (len (fringe) != 0):

            bestIndex = self.findBestState(fringe, heuristic)
            state = fringe.pop(bestIndex)

            if (state.row == finalState.row and state.col == finalState.col):
                foundSolution = True
                if(foundSolution):
                    print("Found")
                break

            nextStates = self.findNextStates(map, rows, columns, state)
            neighborStates.append(state)

            for i in range(len(nextStates)):

                next = nextStates[i]

                if (not self.isInList(neighborStates, next) and not self.isInList(fringe, state)):
                    fringe.append(next)

                    if next not in heuristic.keys():
                        euclideanDistance[next] = self.returnEuclideanDistance(next, finalState)
                        travelledDistance[next] = travelledDistance[state] + 1
                        heuristic[next] = euclideanDistance[next] + travelledDistance[next]
                        parents[next] = state

        if foundSolution == True:
            return self.createPath(state, parents)

        else:
            return None

    def createPath(self, state, parents):
        path = []
        path.append(state)

        while parents[state] != None:
            path.append(parents[state])
            state = parents[state]

        # path = path[::-1]
        path.pop()
        
        return path

    def findNextStates(self, map, rows, columns, state):
        i = state.row
        j = state.col
        nextStates = []

        if i > 0 and map[self.convertStateToPos(State(i - 1, j))].type != -1:
            nextStates.append(State(i - 1, j))

        if i + 1 < rows and map[self.convertStateToPos(State(i + 1, j))].type != -1:
            nextStates.append(State(i + 1, j))

        if j > 0 and map[self.convertStateToPos(State(i, j - 1))].type != -1:
            nextStates.append(State(i, j - 1))

        if j + 1 < columns and map[self.convertStateToPos(State(i, j + 1))].type != -1:
            nextStates.append(State(i, j + 1))

        if j > 0 and i > 0 and map[self.convertStateToPos(State(i - 1, j - 1))].type != -1 and map[self.convertStateToPos(State(i - 1, j))].type != -1 and map[self.convertStateToPos(State(i, j - 1))].type != -1:
            nextStates.append(State(i - 1, j - 1))

        if j > 0 and i + 1 < rows and map[self.convertStateToPos(State(i + 1, j - 1))].type != -1 and map[self.convertStateToPos(State(i + 1, j))].type != -1 and map[self.convertStateToPos(State(i, j - 1))].type != -1:
            nextStates.append(State(i + 1, j - 1))

        if j + 1 < columns and i > 0 and map[self.convertStateToPos(State(i - 1, j + 1))].type != -1 and map[self.convertStateToPos(State(i - 1, j))].type != -1 and map[self.convertStateToPos(State(i, j + 1))].type != -1:
            nextStates.append(State(i - 1, j + 1))

        if j + 1 < columns and i + 1 < rows and map[self.convertStateToPos(State(i + 1, j + 1))].type != -1 and map[self.convertStateToPos(State(i + 1, j))].type != -1 and map[self.convertStateToPos(State(i, j + 1))].type != -1:
            nextStates.append(State(i + 1, j + 1))

        return nextStates

    def findBestState(self, fringe, heuristic):
        bestValue = sys.float_info.max
        bestIndex = 0
        index = 0

        for state in fringe:
            if (heuristic[state] < bestValue):
                bestValue = heuristic[state]
                bestIndex = index

            index = index + 1

        return bestIndex

    def returnEuclideanDistance(self, initialState, finalState):
        return math.sqrt((pow(initialState.row - finalState.row, 2) + pow(initialState.col - finalState.col, 2)))

    def actionToDo(self, state01, state02):
        movePos = { (-1, 0) : "N",
                (1, 0) : "S",
                (0, 1) : "L",
                (0, -1) : "O",
                (-1, 1) : "NE",
                (-1, -1) : "NO",
                (1, 1) : "SE",
                (1, -1) : "SO"}

        stateResult = (state02.row - state01.row, state02.col - state01.col)

        return movePos[stateResult]

    def chooseAction(self):

        if (self.createdBackPath is False):

            result = self.online_dfs_agent(self.currentState)
            if(self.createdBackPath):
                for state in self.backPath:
                    print(state)

                if(len(self.backPath) > 1):
                    state = self.backPath.pop()
                    action = self.actionToDo(self.currentState, state)

                    self.currentState = state
                    return action, state
            
            try:
                while not self.isPossibleToMove(result[1]):
                    if(self.convertActionToNumber(result[0]) > 3):
                        if(result[1].row >= 0 and result[1].col >= 0):
                            self.result[self.convertStateToPos(result[1])].type = -1
                    result = self.online_dfs_agent(self.currentState)

            except:

                print("Finished")
                
                for state in self.backPath:
                    print(state)

                if(len(self.backPath) > 1):
                    state = self.backPath.pop()
                    action = self.actionToDo(self.currentState, state)

                    self.currentState = state
                    return action, state

            return result

        else:
            
            for state in self.backPath:
                print(state)

            if(len(self.backPath) > 1):
                if(self.s.row == self.currentState.row and self.s.col == self.currentState.col):
                    supposed = self.movePosition(self.currentState)
                    if(supposed.row >= 0 and supposed.col >= 0):
                        if(self.convertActionToNumber(self.a) > 3):
                            self.result[self.convertStateToPos(supposed)].type = -1
                    self.backPath = self.star_a_search(self.result, self.maxRows, self.maxColumns, self.currentState, self.initialState)
                elif(self.result[self.convertStateToPos(self.currentState)].type == 0):
                    self.result[self.convertStateToPos(self.currentState)].type = 5

                state = self.backPath.pop()
                action = self.actionToDo(self.currentState, state)
                
                self.a = action
                self.s = self.currentState
                
                self.currentState = state
                return action, state

        return None
    
