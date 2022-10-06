from contextlib import nullcontext
from random import randint
import string
from turtle import pos
from zipfile import ZIP_BZIP2
from state import State

import numpy as np
import sys
import math
import enum
import time

class Result:
    def __init__(self):
        self.type = 0
        self.directions = np.empty_like(8, State)

class RescuePlan:
    def __init__(self, maxRows, maxColumns, goal, initialState, timeLeft, result, name = "none", mesh = "square"):

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
        self.pathToVictim = []
        self.backPath = []
        self.timeLeft = timeLeft
        self.initialTime = timeLeft
        self.result = result
        
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

    def movePosition(self, currentState):
        
        movePos = { "N" : (-1, 0),
                "S" : (1, 0),
                "L" : (0, 1),
                "O" : (0, -1),
                "NE" : (-1, 1),
                "NO" : (-1, -1),
                "SE" : (1, 1),
                "SO" : (1, -1)}

        return State(currentState.row + movePos[self.a][0], currentState.col + movePos[self.a][1])

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

    def convertStateToPos(self, state):
        return state.row * self.maxRows + state.col

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

    def chooseAction(self, currentVictim):

        if (self.timeLeft <= (self.initialTime / 2)):
            if (self.createdBackPath == False):
                    for i in range(self.maxRows):
                        for j in range(self.maxColumns):
                            print(self.result[self.convertStateToPos(State(i, j))].type, end=" ")
                        print("")
                    self.backPath = self.star_a_search(self.result, self.maxRows, self.maxColumns, self.currentState, self.initialState)
                    self.createdBackPath = True
            elif(self.currentState.row == self.initialState.row and self.currentState.col == self.initialState.col):
                return -1, (-1, -1)

            state = self.backPath.pop()
            action = self.actionToDo(self.currentState, state)

            self.a = action
            self.s = self.currentState
            
            self.currentState = state

            return action, state

        else:

            if(len(self.pathToVictim) >= 1):

                if(self.s is not None):

                    if(self.s.row == self.currentState.row and self.s.col == self.currentState.col):
                        supposed = self.movePosition(self.currentState)
                        if(supposed.row >= 0 and supposed.col >= 0):
                            if(self.convertActionToNumber(self.a) > 3):
                                self.result[self.convertStateToPos(supposed)].type = -1
                        self.pathToVictim = self.star_a_search(self.result, self.maxRows, self.maxColumns, self.currentState, currentVictim)
                    elif(self.result[self.convertStateToPos(self.currentState)].type == 0):
                        self.result[self.convertStateToPos(self.currentState)].type = 5

                state = self.pathToVictim.pop()
                action = self.actionToDo(self.currentState, state)

                self.a = action
                self.s = self.currentState
                
                self.currentState = state

                return action, state

            else:
                self.pathToVictim = self.star_a_search(self.result, self.maxRows, self.maxColumns, self.currentState, currentVictim)
                for state in self.pathToVictim:
                    print(state)

        return None
    
