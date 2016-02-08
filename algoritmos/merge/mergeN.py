import os
from node import Node, LinkPoint
from aux import Aux
import random

MOV_DIAGONAL  = 1
MOV_IZQUIERDA = 2
MOV_ARRIBA   = 3

        
# Caso constructivo: Grafo + Palabra
def calcN(nodePoint, curNodePoint, largoPalabra):
    
    if nodePoint is None or curNodePoint is None:
        print "* Out of bounds"
        return 0

    
    
    node    = nodePoint.thisNode
    curNode = curNodePoint.thisNode
    
    j = curNodePoint.length - 1
    
    
    print "Calcula: Node ",nodePoint.thisNode.letra, "(",curNodePoint.thisNode.letra,", pos: ",j,")"
    
    
    if nodePoint.values is None:
        nodePoint.values     = [-1]      * largoPalabra
        nodePoint.refNode    = [None]    * largoPalabra
        nodePoint.refNodePos = [0]       * largoPalabra
        
        print "[" + str(node.letra) + "] Creando node.values"
        
        #print node.values
        print  "----"

    
    if(nodePoint.values[j] >= 0):
        # Si ya esta calculada lo retornamos
        return nodePoint.values[j];
    
    sigPa = nodePoint.lpoint
    sigPb = curNodePoint.lpoint
    
    #   <------------------- ambos terminan ---------------->    <------------------------------- coinciden ------------------------->
    if  (sigPa is None and sigPb is None) or (not sigPa is None and not sigPb is None and sigPa.thisNode.letra == sigPb.thisNode.letra):
        
        print  "[",node.letra,"]","Caso diagonal con j=",j," y w[j]=",curNode.letra
        
        # --- Tres posibles casos --- #
        
        # 1 - Hay una diagonal (ambas letras iguales)
        if not sigPa is None and not sigPb is None:
            val = 1 + calcN(sigPa, sigPb, largoPalabra)  # diagonal, se come uno de ambos

            nodePoint.values[j] = val
            nodePoint.refNode[j] = sigPa
            nodePoint.refNodePos[j] = j-1
            
        # 2 - Es "diagonal" porque se acabaron los dos a la vez.
        elif sigPa is None and sigPb is None:
            # Ambos se acabaron
            print  "Encontre el origen"
            nodePoint.values[j] = 1
                
        return nodePoint.values[j]
        
    # Caso no diagonal
    
    print "[",node.letra,"]","Caso no diagonal (vs ",curNode.letra, ")"
    
    
    # Calculamos el valor horizontal (consumir de la ejecucion nueva)
    nodePoint.values     [j] = calcN(nodePoint, sigPb, largoPalabra)
    nodePoint.refNode    [j] = nodePoint
    nodePoint.refNodePos [j] = j-1
    
    print "Consumir la letra de w nos deja en ", nodePoint.values[j]
    
    # Comparamos con consumir de la corrida existente
    val = calcN(sigPa, curNodePoint, largoPalabra)  # vamos al nodo padre, pero mantenemos posicion horizontal
    print "Consumir del nodo me deja en ", val
    
    if val >0 and ( nodePoint.values[j] == 0 or val > nodePoint.values[j]):
        
        # Hubo que poner esta condicion para que no prefiriera los 0s por default
        nodePoint.values[j] = val
        nodePoint.refNode[j] = sigPa
        nodePoint.refNodePos[j] = j

    
    
    print "[[[[" ,  nodePoint.values[j] , "]]]]]"
    return nodePoint.values[j]


# Sirve para consolidar el grafo luego de agregar otra demostracion
# Este algoritmo asume que las preferencias al momento de elegir el siguiente nodo en el calculo de calcN
# se realiza con el siguiente criterio:
# - Si ambos valores son iguales, es una diagonal
# - Sino
#      - Consumir de nodeW
#      - Consumir del grafo
#   ** En particular, el diagonal y consumir de w no se intercalan (ninguno se intercala, pero ya eso alcanza)
def graphregen(curNodePa, nodeW):
    # Cuando hay avances en w exclusivamente, o sea se mantiene el puntero
    # pero cambia la posicion
    # Entonces hay que agregar un nodo y arista
    
    j = nodeW.length - 1

    # Agregamos el nuevo camino al grafo generalizado.
    curNodePb = LinkPoint(curNodePa.thisNode)
    # El nuevo camino queda registrado en el INIT del generalizado
    
    # Vamos a mergear los caminos que empiezan por estos
    # curNodePa
    # curNodePb
    
    revertirA = None
    
    while not curNodePa is None:
        
        print "Estudiando: ", curNodePa.thisNode.letra
        
        hasNextNode = not curNodePa.refNode[j] is None
        sameNode = curNodePa is curNodePa.refNode[j]
        diagonal = not sameNode and curNodePa.refNodePos[j] <> j
            
        
        print "has next node", hasNextNode
        print "sameNode", sameNode
        print "diagonal", diagonal
        
        
        if sameNode:
            
            # Avances exclusivos de la nueva corrida
            print "SAME NODE"
            while sameNode:
                
                # Estos avances generan nodos independientes
                nNode = Node()
                #             <--------- Node -------->
                nNode.letra = nodeW.lpoint.thisNode.letra
                
                print "Agregamos con letra ", nNode.letra, " desde ", str(curNodePb.thisNode.letra)
                
                nPoint = LinkPoint(nNode)
                
                # Enlazamos al anterior con el nuevo
                
                curNodePb.lpoint = nPoint
                
                # Continuamos la ejecucion desde el nuevo nodo
                
                revertirA = curNodePb
                
                curNodePb = nPoint
                nodeW = nodeW.lpoint
                
                
                sameNode = curNodePa is curNodePa.refNode[j]
                
                j = curNodePa.refNodePos[j]
            
        else:
            
            
            # Podemos ignorar los casos no diagonales, o sea, en los que se consume solo
            # del grafo generalizado
            
            if diagonal:
                
                # Para evitar desfasajes, es necesario retroceder el nodo para el correcto mezclado
                if not revertirA is None:
                    curNodePb = revertirA
                    revertirA = None
                
                print "DIAGONAL ", curNodePa.thisNode.letra
                print "HAS NEXT NODE: ",hasNextNode
                print "B LETRA: ", curNodePb.thisNode.letra
                
                if hasNextNode:

                    # Agregamos el nuevo punto de camino en el nodo siguiente
                    nPoint = LinkPoint(curNodePa.lpoint.thisNode)

                    curNodePb.lpoint = nPoint
                    
                    print curNodePb.thisNode.letra, "--->", nPoint.thisNode.letra
                    nodeW = nodeW.lpoint
                    curNodePb = nPoint

            oldJ = j            
            j = curNodePa.refNodePos[j]
            curNodePa = curNodePa.refNode[oldJ]
            
        
    return 0
    
def plot(node):
    
    file = open("test.dot", "w")
    file.write("digraph pcspec {\n\n");

    i = 1
    for lnode in node.n:
        curNode = lnode
        while not curNode is None:
            if not curNode.lpoint is None:
                    
                letra = "INIT" if curNode.thisNode.letra is None else curNode.thisNode.letra
                letra2 = curNode.lpoint.thisNode.letra
                
                label = letra + " a " + letra2
                
                file.write(letra2 + "->" + letra + ' [ label="(' + str(i) + ')' + label + '" ]; \n')
            
            curNode = curNode.lpoint
        i += 1
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

plot(g1)
plot(g2)



maxVal   = 0
maxRatio = 0

# La    rgo de la nueva palabra
seqLen = g2.n[0].length
    
for p in g1.n:
    
    nVal = calcN(p, g2.n[0], seqLen)
    
    nRatio = nVal / p.length
    
    # Determinamos si es el mas parecido hasta el momento o no
    if  nVal > maxVal and nRatio > maxRatio:
        maxRatio = nRatio
        maxVal = nVal
        
        caminoMasSimilar = p

print "RATIO: ", nRatio
# Si hay diferencias, combinamos
#if nRatio < 1:
graphregen(caminoMasSimilar, g2.n[0])

plot(g1)

exit
