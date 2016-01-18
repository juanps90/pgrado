import os
from node import Node
from aux import Aux
import random

MOV_DIAGONAL  = 1
MOV_IZQUIERDA = 2
MOV_ARRIBA   = 3

LINK_WEIGHT = 0.0001

# A partir de un grafo de una corrida, devuelve la tira
# En vez de retornar una tira de caracteres, me parecio mejor retornar una lista
# de nodos
# En definitiva igual tengo la "letra"
def flatten(curNode, revert = True):
    
    maxNodesNode = None # El nodo con mas aristas salientes
    maxNodesCount = -1 # La cantidad de aristas que tiene ese nodo
    
    if curNode.parentNodes:
        for p in curNode.parentNodes:
            if maxNodesCount < len(p.parentNodes):
                maxNodesCount = len(p.parentNodes)
                maxNodesNode = p

    #letra = "" if curNode.letra is None else curNode.letra
    
    
    if maxNodesNode is None:
        lista = [Node()]
    else:
        lista = flatten(maxNodesNode, False)
    lista.append(curNode)
    
    #if revert:
    #    lista.reverse()
        
    return lista
    
        
# Caso constructivo: Grafo + Palabra
def calcN(node, w, j, depth):
    tabs = ""
    i = 0
    while i < depth:
        tabs = tabs + "   "
        i += 1
    print tabs + "Calcula: Node ",node.letra, "(",w[j].letra,", pos: ",j,")"
       
    if node is None or j <= 0:
        print tabs + "* Out of bounds"
        return 0
    
    if node.values is None:
        node.values     = [-1]       * len(w)
        node.refNode    = [None]    * len(w)
        node.refNodePos = [0]       * len(w)
        
        print tabs + "[" + str(node.letra) + "] Creando node.values"
        
        #print node.values
        print tabs + "----"

    
    if(node.values[j] >= 0):
        # Si ya esta calculada lo retornamos
        print tabs + "[",node.letra,"]","Se reusa valor anterior: ", node.values[j]
        return node.values[j];
    
    #   <--- mismas letras ---->     <----------- ambos en init ------------->
    if  node.letra == w[j].letra or (node.letra is None and w[j].letra is None): # Iguales letras, o ambos init
        
        print tabs + "[",node.letra,"]","Caso diagonal con j=",j," y w[j]=",w[j].letra
        minimo = -1
        
        # Diagonal, entonces consumimos de cada uno y elegimos el mejor padre
        for p in node.parentNodes:
            val = 1 + 3* LINK_WEIGHT + calcN(p, w, j-1, depth+1)  # diagonal, se come uno de ambos
                                        # avanzamos en la palabra w y en el grafo
                                        # ( por eso vamos al parent )
            if minimo == -1 or val > minimo: # val siempre es mayor a cero, es al menos 1
                minimo = val
                node.values[j] = val
                node.refNode[j] = p
                node.refNodePos[j] = j-1
        
        # La comparacion no se hizo    <--SigJ-->
        if node.refNode[j] is None and ( j - 1 ) == 0:
            print tabs + "Encontre el origen"
            
            node.values[j] = 1
        elif node.refNode[j] is None or ( j - 1 ) == 0:
            print tabs + "Se acabo uno, dead end"
            node.values[j] = 0
        else:
            # La arista en el grafo que era el consolidado es node.letra -> node.refNode[j]
            print tabs + "[",node.letra,"]","Diagonal normal, con letra: ", node.refNode[j].letra,", valor: ",node.values[j]
            
            print "Por un lado tenia en el grafo: ",node.refNode[j].parentTypes #[node]
            print "Por el otro tengo en la nueva: ",w[j-1].parentTypes #[w[j-1]]
            
            #node.refNode[j].parentType[node] = min(node.refNode[j].parentType[node],
        
        print tabs , "[[[[" ,  node.values[j] , "]]]]]"
        return node.values[j]
        
    # Caso no diagonal
    
    print tabs + "[",node.letra,"]","Caso no diagonal (vs ",w[j].letra, ")"
    
    
    node.values     [j] = 2*LINK_WEIGHT + calcN(node, w, j-1, depth+1)
    node.refNode    [j] = node
    node.refNodePos [j] = j-1
    
    print tabs + "Consumir la letra de w nos deja en ", node.values[j]
    
    for p in node.parentNodes:
        val = LINK_WEIGHT + calcN(p, w, j, depth+1)  # vamos al nodo padre, pero mantenemos posicion horizontal
        print tabs + "Consumir del nodo me deja en ", val
        if val >0 and ( node.values[j] == 0 or val > node.values[j]):
            print tabs + "[",node.letra,"]","Voy prefiriendo ", p.letra
            # Hubo que poner esta condicion para que no prefiriera los 0s por default
            node.values[j] = val
            node.refNode[j] = p
            node.refNodePos[j] = j
    
    print tabs + "                            *********       [",node.letra,"]","Caso no diagonal ",node.letra,",",w[j].letra," queda con valor: ",node.values[j], "voy pa (", node.refNode[j].letra, w[node.refNodePos[j]].letra,")"
    
    print tabs , "[[[[" ,  node.values[j] , "]]]]]"
    return node.values[j]


# Sirve para consolidar el grafo luego de agregar otra demostracion
# Este algoritmo asume que las preferencias al momento de elegir el siguiente nodo en el calculo de calcN
# se realiza con el siguiente criterio:
# - Si ambos valores son iguales, es una diagonal
# - Sino
#      - Consumir de w
#      - Consumir del grafo
#   ** En particular, el diagonal y consumir de w no se intercalan (ninguno se intercala, pero ya eso alcanza)
def graphregen(node, w):
    # Cuando hay avances en w exclusivamente, o sea se mantiene el puntero
    # pero cambia la posicion
    # Entonces hay que agregar un nodo y arista
    
    j = len(w) - 1

    # Si este nodo ya se proceso, no seguimos
    curNode = node
    
    
    nodeOnHold = None
    
    lastCommonNode = None
    
    while not curNode is None:
        
        if curNode.values is None:
            break
        
        
        print "Estudiando: ", curNode.letra
        
        
        hasNextNode = not curNode.refNode[j] is None
        sameNode = curNode is curNode.refNode[j]
        diagonal = not sameNode and curNode.refNodePos[j] <> j
        
        print "has next node", hasNextNode
        print "sameNode", sameNode
        print "diagonal", diagonal
        
        if not nodeOnHold is None and diagonal: # Si volvio a una parte del grafo ( no necesariamente "comun", me estoy dando cuenta)
            # este es un link que sale de una parte comun del grafo a un nodo nuevo?
            if not curNode in nodeOnHold.parentTypes:
                nodeOnHold.parentNodes.append(curNode)
                #nodeOnHold.parentTypes[curNode]
                # en el grafo anterior el link iba desde w[j+1] al w[j], entonces
                nodeOnHold.parentTypes[curNode]  = w[j+1].parentTypes[w[j]]
                
                print "[1] ", str(curNode.letra) + "--->" + str(nodeOnHold.letra)
                print "w[j]: ",w[j].letra,"w[j+1]: ",w[j+1].letra, "link: ",
            else:
                nodeOnHold.parentTypes[curNode]  = min(nodeOnHold.parentTypes[curNode], w[j+1].parentTypes[w[j]])
                
                print "[1] NO LO AGREGO, pero lo debilito? ",str(curNode.letra) + "--->" + str(nodeOnHold.letra) 
                
            nodeOnHold = None
        
        if diagonal:
            nodeOnHold = curNode
        
        avanzo = False
        
        # Es un indice al nodo actual para generar el grafo
        #curGraphNode = curNode # quitamos la primer vez
        print "j:",j,  "refNodePos[j]:", curNode.refNodePos[j]
        curGraphNode = None
         
        
        while curNode is curNode.refNode[j] and curNode.refNodePos[j] <> j: # Caso en que consume una letra de w
           
            print "CONSUMIENDO LETRA"
            
            # curNode nos indica el nodo en el grafo con valores
            # que tiene los datos que necesitamos
            # Como ese nodo no cambia mientras avancemos en W
            # Usamos siempre esa misma referencia
            if not curGraphNode is None:
                print "Avanzo Horizontal a letra:", w[j].letra,", j=", j, "CurGraphNode:", curGraphNode.letra
            else:
                print "Avanzo Horizontal a letra:", w[j].letra,", j=", j, "CurGraphNode: NULL"
                
            nNode = Node() # Nuevo nodo a agregar en el grafo
            
            nNode.letra = w[j].letra
            
            
            if not avanzo and not nodeOnHold is None:
                print "[4]",nNode.letra + "--->" + str(nodeOnHold.letra)
                nodeOnHold.parentNodes.append(nNode)
                nodeOnHold.parentTypes[nNode]  = w[j+1].parentTypes[w[j]]
                
                # Hay que ver lo del permanente aca
                nodeOnHold = None
            
            # Ese nuevo nodo es padre del nodo actual
            # Pero del nodo que estamos usando para crear el grafo
            # Inicialmente curNode = curGraphNode
            if not curGraphNode is None:
                curGraphNode.parentNodes.append(nNode)
                print "[2] ", str(nNode.letra) + "--curGraphNode-->" + str(curGraphNode.letra)
            else:
                print "SALTEANDO LINK DE ", str(nNode.letra) + "-- a -->" + str(curNode.letra)
                
            j = curNode.refNodePos[j] # o de forma equivalente, j = j - 1
            curGraphNode = nNode
            avanzo = True
            
            nodeOnHold = nNode
        
        if avanzo:
            # Si realizo avances y termino puede haber pasado dos cosas:
            # 1. El camino alternativo ahora se unio con un camino comun
            # 2. Se termino la ejecucion
            curNode.values = None
            
            
            if not lastCommonNode is None:
                print "[3] ", "-- [",curNode.letra,"]","Apuntando a ",lastCommonNode.letra
                curNode.parentNodes.append(lastCommonNode)
                lastCommonNode = curNode
            
            curNode = curNode.refNode[j]
            
                
        # No hubieron avances exclusivos en la palabra
        # Fue una diagonal o un arriba
        else:
            print "CASO ELSE"
            
            if curNode <> curNode.refNode[j]:
                # Ya no necesitamos esos valores
                # Subimos de nodo
                curNode.values = None
            
            
            oldJ = j 
            j = curNode.refNodePos[j] # Puede ser igual o cambiar
            
            print "OLDJ: ", oldJ, ", j: ",j
            curNode = curNode.refNode[oldJ]
            
        
    return 0
    
def plot(node):
    
    file = open("test.dot", "w")
    file.write("digraph pcspec {\n\n");

    q = [node]
    addedNodes = {}
    curPos = 10
    

    addedNodes[node] = True
    
    
    while q:
        top = q.pop()
        for l in top.parentNodes:
            
            if not l in addedNodes:
                
                addedNodes[l] = True
                q.append(l)
           
            letra = "INIT" if top.letra is None else top.letra
            letra2 = "NULL" if l.letra is None else l.letra
            print str(top.letra) + "-------->" + str(l.letra)
            label = "n/a"
            if l in top.parentTypes:
                tipo = top.parentTypes[l]
                if(tipo == Node.LINK_ORD):
                    label = "ORD"
                elif(tipo == Node.LINK_ENA):
                    label = "ENA"
                elif(tipo == Node.LINK_PRM):
                    label = "PRM"
                
            file.write(letra2 + "->" + letra + ' [ label="' + label + '" ]; \n')
    file.write("}");
    file.close()
    os.system("dot test.dot -T jpg > out2.jpg && eog out2.jpg")
    
def printTreeValues(n, j):
    
    if n is None:
        print "---"
        return 0;
    
    
    #print n.letra, w[j]
    printTreeValues (n.refNode[j],n.refNodePos[j])
    
    
    print n.letra,
    print n.refNodePos
        
    return 0

a = Aux()

g1 = a.sampleGraph1() # G1 sera el acumulado hasta el momento
g2 = a.sampleGraph2() # G2 es una nueva corrida

w = flatten(g2)

# Aplanamos el nuevo grafo (queda una tira de nodos)

plot(g1)
plot(g2)

print "------------------------------------------------------------------------------------------------"
print ""
print ""
print ""
print ""
print ""

calcN(g1, w, len(w)-1, 0)

printTreeValues(g1,len(w)-1)


graphregen(g1, w)

plot(g1)
