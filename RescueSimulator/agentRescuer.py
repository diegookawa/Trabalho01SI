import sys
import os
import numpy as np

from model import Model
from problem import Problem
from state import State

from rescuePlan import RescuePlan

##Importa o Planner
sys.path.append(os.path.join("pkg", "planner"))
from planner import Planner

## Classe que define o Agente
class AgentRescuer:

    def __init__(self, model, configDict, result, victims):
        """ 
        Construtor do agente random
        @param model referencia o ambiente onde o agente estah situado
        """

        self.victims = victims
        self.victimNumber = 0
        self.result = result
        self.model = model

        ## Obtem o tempo que tem para executar
        self.tl = configDict["Ts"]
        print("Tempo disponivel: ", self.tl)     
        self.mesh = self.model.mesh

        self.prob = Problem()
        self.prob.createMaze(model.rows, model.columns, model.maze)
    
        initial = self.positionSensor()
        self.prob.defInitialState(initial.row, initial.col)
        print("*** Estado inicial do agente: ", self.prob.initialState)
        
        self.currentState = self.prob.initialState
        self.costAll = 0

        ## Cria a instancia do plano para se movimentar aleatoriamente no labirinto (sem nenhuma acao) 
        self.plan = RescuePlan(model.rows, model.columns, self.prob.goalState, initial, self.tl, self.result, "goal", self.mesh)

        ## adicionar crencas sobre o estado do ambiente ao plano - neste exemplo, o agente faz uma copia do que existe no ambiente.
        ## Em situacoes de exploracao, o agente deve aprender em tempo de execucao onde estao as paredes
        self.plan.setWalls(model.maze.walls)
        
        ## Adiciona o(s) planos a biblioteca de planos do agente
        self.libPlan=[self.plan]

        ## inicializa acao do ciclo anterior com o estado esperado
        self.previousAction = "nop"    ## nenhuma (no operation)
        self.expectedState = self.currentState

    ## Metodo que define a deliberacao do agente 
    def deliberate(self):
        ## Verifica se há algum plano a ser executado
        if len(self.libPlan) == 0:
            return -1   ## fim da execucao do agente, acabaram os planos
        
        self.plan = self.libPlan[0]

        print("\n*** Inicio do ciclo raciocinio ***")
        print("Pos agente socorrista no amb.: ", self.positionSensor())

        ## Redefine o estado atual do agente de acordo com o resultado da execução da ação do ciclo anterior
        self.currentState = self.positionSensor()
        self.plan.updateCurrentState(self.currentState) # atualiza o current state no plano
        print("Ag cre que esta em: ", self.currentState)

        ## Verifica se a execução do acao do ciclo anterior funcionou ou nao
        if not (self.currentState == self.expectedState):
            print("---> erro na execucao da acao ", self.previousAction, ": esperava estar em ", self.expectedState, ", mas estou em ", self.currentState)

        ## Funcionou ou nao, vou somar o custo da acao com o total 
        self.costAll += self.prob.getActionCost(self.previousAction)
        print ("Custo até o momento (com a ação escolhida):", self.costAll) 

        ## consome o tempo gasto
        self.tl -= self.prob.getActionCost(self.previousAction)
        print("Tempo disponivel: ", self.tl)
        self.plan.updateTime(self.tl)

        ## Verifica se atingiu o estado objetivo
        ## Poderia ser outra condição, como atingiu o custo máximo de operação
        if self.prob.goalTest(self.currentState):
            print("!!! Objetivo atingido !!!")
            del self.libPlan[0]  ## retira plano da biblioteca

        ## Define a proxima acao a ser executada
        ## currentAction eh uma tupla na forma: <direcao>, <state>
        print(f"VITIMA {self.victims[self.victimNumber][0]}")
        result = self.plan.chooseAction(self.victims[self.victimNumber][0])

        try:
            print("Ag deliberou pela acao: ", result[0], " o estado resultado esperado é: ", result[1])

        except:
            print("Finished")

        ## Executa esse acao, atraves do metodo executeGo 
        try:
            self.executeGo(result[0])
            self.previousAction = result[0]
            self.expectedState = result[1]   

        except:
            print("Victim saved")    
            self.victimNumber = self.victimNumber + 1

        return 1

    ## Metodo que executa as acoes
    def executeGo(self, action):
        """Atuador: solicita ao agente físico para executar a acao.
        @param direction: Direcao da acao do agente {"N", "S", ...}
        @return 1 caso movimentacao tenha sido executada corretamente """

        ## Passa a acao para o modelo
        result = self.model.go(action)
        
        ## Se o resultado for True, significa que a acao foi completada com sucesso, e ja pode ser removida do plano
        ## if (result[1]): ## atingiu objetivo ## TACLA 20220311
        ##    del self.plan[0]
        ##    self.actionDo((2,1), True)
            

    ## Metodo que pega a posicao real do agente no ambiente
    def positionSensor(self):
        """Simula um sensor que realiza a leitura do posição atual no ambiente.
        @return instancia da classe Estado que representa a posição atual do agente no labirinto."""
        pos = self.model.agentPos
        return State(pos[0],pos[1])
    
    ## Metodo que atualiza a biblioteca de planos, de acordo com o estado atual do agente
    def updateLibPlan(self):
        for i in self.libPlan:
            i.updateCurrentState(self.currentState)

    def actionDo(self, posAction, action = True):
        self.model.do(posAction, action)

    def victimPresenceSensor(self):
        """Simula um sensor que realiza a deteccao de presenca de vitima na posicao onde o agente se encontra no ambiente
           @return retorna o id da vítima"""     
        return self.model.isThereVictim()