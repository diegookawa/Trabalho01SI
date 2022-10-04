import sys
import os
import time

## Importa as classes que serao usadas
sys.path.append(os.path.join("pkg"))
from model import Model
from agentRnd import AgentRnd


## Metodo utilizado para permitir que o usuario construa o labirindo clicando em cima
def buildMaze(model):
    model.drawToBuild()
    step = model.getStep()
    while step == "build":
        model.drawToBuild()
        step = model.getStep()
    ## Atualiza o labirinto
    model.updateMaze()

def main():
    # Lê arquivo config.txt
    arq = open(os.path.join("config_data","ambienteProfessor.txt"),"r")
    configDict = {} 
    for line in arq:
        ## O formato de cada linha é:var=valor
        ## As variáveis são 
        ##  maxLin, maxCol que definem o tamanho do labirinto
        ## Tv e Ts: tempo limite para vasculhar e tempo para salvar
        ## Bv e Bs: bateria inicial disponível ao agente vasculhador e ao socorrista
        ## Ks :capacidade de carregar suprimentos em número de pacotes (somente para o ag. socorrista)

        if 'XMax' in line:
            XMax = int(line.split(' ')[-1].strip())

        if 'YMax' in line:
            YMax = int(line.split(' ')[-1].strip())

        if 'Te' in line:
            configDict['Te'] = int(line.split(' ')[-1].strip())

        if 'Ts' in line:
            configDict['Ts'] = int(line.split(' ')[-1].strip())

        # values = line.split(" ")
        # configDict[values[0]] = int(values[1])

    # print("dicionario config: ", configDict)

    # Cria o ambiente (modelo) = Labirinto com suas paredes
    mesh = "square"

    ## nome do arquivo de configuracao do ambiente - deve estar na pasta <proj>/config_data
    loadMaze = "ambienteProfessor"

    model = Model(XMax, YMax, mesh, loadMaze)
    buildMaze(model)

    model.maze.board.posAgent
    model.maze.board.posGoal
    # Define a posição inicial do agente no ambiente - corresponde ao estado inicial
    model.setAgentPos(model.maze.board.posAgent[0],model.maze.board.posAgent[1])
    model.setGoalPos(model.maze.board.posGoal[0],model.maze.board.posGoal[1])  
    model.draw()
    
    # Cria um agente
    agent = AgentRnd(model,configDict)

    ## Ciclo de raciocínio do agente
    agent.deliberate()
    while agent.deliberate() != -1:
        model.draw()
        time.sleep(0) # para dar tempo de visualizar as movimentacoes do agente no labirinto
    model.draw()    

    for victim in agent.victims:
        print(victim)

if __name__ == '__main__':
    main()
