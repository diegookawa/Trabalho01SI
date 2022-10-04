from contextlib import nullcontext
from random import randint
from turtle import pos
from zipfile import ZIP_BZIP2
from state import State

import numpy as np
import enum

class DfsPlan:
    def __init__(self, maxRows, maxColumns, goal, initialState, name = "none", mesh = "square"):

        self.walls = []
        self.maxRows = maxRows
        self.maxColumns = maxColumns
        self.initialState = initialState
        self.currentState = initialState
        self.goalPos = goal
        self.actions = []

        self.s = None
        self.a = None
        self.result = self.create_result_table()
        self.untried = self.create_untried_table()
        self.unbacktracked = self.create_unbacktracked_table()

    def create_result_table(self):
        result = np.empty((self.maxRows * self.maxColumns, 8), State)

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

    def online_dfs_agent(self, currentState):
        movePos = { "N" : (-1, 0),
                "S" : (1, 0),
                "L" : (0, 1),
                "O" : (0, -1),
                "NE" : (-1, 1),
                "NO" : (-1, -1),
                "SE" : (1, 1),
                "SO" : (1, -1)}

        # if (goal_test(currentState)):
        #     return

        #if (self.convertStateToPos(currentState) > len(self.untried)):
            #self.untried.append(["N", "S", "L", "O", "NE", "NO", "SE", "SO"])

        if (self.s is not None):
            if(self.result[self.convertStateToPos(self.s)][self.convertActionToNumber(self.a)] is None):
                self.unbacktracked[self.convertStateToPos(currentState)].append(self.s)
                self.result[self.convertStateToPos(self.s)][self.convertActionToNumber(self.a)] = currentState

        if (len(self.untried[self.convertStateToPos(currentState)]) == 0):

            if (len(self.unbacktracked[self.convertStateToPos(currentState)]) == 0):
                return
            
            else:
                state_to_go_back = self.unbacktracked[self.convertStateToPos(currentState)].pop()
                action_number = -1
                for number, state in enumerate(self.result[self.convertStateToPos(currentState)]):
                    if (state.row == state_to_go_back.row and state.col == state_to_go_back.col):
                        action_number = number
                        break
                
                if (action_number == -1):
                    action_number = 0

                self.a = self.convertNumberToAction(action_number)
                
        else:
            self.a = self.untried[self.convertStateToPos(currentState)].pop()

        self.s = currentState
        state = State(currentState.row + movePos[self.a][0], currentState.col + movePos[self.a][1])

        return self.a, state

    def chooseAction(self):
        result = self.online_dfs_agent(self.currentState)
        
        try:
            while not self.isPossibleToMove(result[1]):
                result = self.online_dfs_agent(self.currentState)

        except:
            print("Finished")

        return result



        
       
        
        
