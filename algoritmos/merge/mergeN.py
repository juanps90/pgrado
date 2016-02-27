import os
from node import Node, LinkPoint
from aux import Aux
import random

MOV_IZQUIERDA = 1
MOV_ARRIBA   = 2
MOV_DIAGONAL  = 3

def get_nodos_padre(node):
    visitados = {}
    padres = []
    
    get_nodos_padre_iter(node, padres, visitados)
    return padres
    
def get_nodos_padre_iter(node, padres, visitados):
    if node in visitados:
        return 0
    visitados[node] = 1
    
    if not node.parentNodes:
        # es un padre
        padres.append(node)
    else:
        # no es padre
        for p in node.parentNodes:
            get_nodos_padre_iter(p, padres, visitados)
        

# start_nodes es una lista de nodos iniciales
# largo_nueva_corrida es el largo de la nueva corrida a incorporar
# Es necesaria para inicializar los arreglos de valores

def obtener_caminos(start_nodes, largo_nueva_corrida):
    for s in start_nodes:
        obtener_caminos_iter(s, None, largo_nueva_corrida)

# Genera todas las filas de valores enganchadas, respetando prefijos        
def obtener_caminos_iter(node, prevPoint, largo_nueva_corrida):
    l = LinkPoint(node)
    l.lpoint = prevPoint                    # Enganchamos esta fila con la fila anterior
    
    l.values     = [-1] * largo_nueva_corrida    # Inicializamos la fila con el largo correcto
    l.mov        = [0]       * largo_nueva_corrida
    
    for sNode in node.childNodes:
        obtener_caminos_iter(sNode, l, largo_nueva_corrida)


# Toma un grafo y le agrega las estructuras para el LCS
def preparar_grafo_lcs(grafo, largo):
    padres = get_nodos_padre(grafo)
    obtener_caminos(padres, largo)


# Comparacion de iguales, aca deberian tomarse en cuenta los parametros, etc
def equals(nodeA, nodeB):
    
    if nodeA is None <> nodeB is None:
        return False
    
    if nodeA.letra is None <> nodeB.letra is None:
        return False
     
    return nodeA.letra == nodeB.letra

def get_first(iterable, default=None):
    if iterable:
        for item in iterable:
            return item
    return default

def calcN(nodePoint, curNode, j):
    
    if nodePoint is None or curNode is None:
        return 0
    
    node = nodePoint.thisNode
    
    if(nodePoint.values[j] >= 0):
        # Si ya esta calculada lo retornamos
        return nodePoint.values[j]
    
    if  equals(node, curNode):
        res = calcN(nodePoint.lpoint, get_first(curNode.parentNodes), j -1 )
        
        nodePoint.values[j] = 1 + res
        
        nodePoint.mov[j] = MOV_DIAGONAL
        
        return nodePoint.values[j]
        
    # Caso no diagonal
    nodePoint.values     [j] = calcN(nodePoint, get_first(curNode.parentNodes), j-1)
    nodePoint.mov        [j] = MOV_IZQUIERDA
    
    val = calcN(nodePoint.lpoint, curNode, j)  # vamos al nodo padre, pero mantenemos posicion horizontal
    print "Consumir del nodo me deja en ", val
    
    if val >0 and ( nodePoint.values[j] == 0 or val > nodePoint.values[j]):
        nodePoint.values[j] = val
        nodePoint.mov   [j] = MOV_ARRIBA
    
    return nodePoint.values[j]


def enlazar(nodoAnterior, nNode, tipoEnlaceAnterior):
    if nNode in nodoAnterior.parentNodes:
        return 0 # ya estaba
    print "ENLAZO ", str(nNode.letra)," con ", str(nodoAnterior.letra)
    nodoAnterior.parentNodes.append(nNode)
    nodoAnterior.parentTypes.append(tipoEnlaceAnterior)
    nNode.childNodes.append(nodoAnterior)

def desenlazar(nodoAnterior, nNode):
    if nNode in nodoAnterior.parentNodes:
        i1 = nodoAnterior.parentNodes.index(nNode)
        
        nodoAnterior.parentTypes.pop(i1)
        nodoAnterior.parentNodes.pop(i1)
        
        #try:
        nNode.childNodes.remove(nodoAnterior)
        #except ValueError:
        #    print "No estaba en childNodes. Grafo mal?"
        
    

# Debilita una arista en hasta maxNodeType
# La arista es desde fromNode->toNode
def debilitar(toNode, fromNode,maxNodeType):
    print fromNode.letra, " a ", toNode.letra
    i = 0
    for n in fromNode.parentNodes:
        print "I ES ", i
        if n is toNode:
            fromNode.parentTypes[i] = min(fromNode.parentTypes[i], maxNodeType)
            return 0
        i+=1
            
    

# Sirve para consolidar el grafo luego de agregar otra demostracion
# Este algoritmo asume que las preferencias al momento de elegir el siguiente nodo en el calculo de calcN
# se realiza con el siguiente criterio:
# - Si ambos valores son iguales, es una diagonal
# - Sino
#      - Consumir de nodeW
#      - Consumir del grafo
#   ** En particular, el diagonal y consumir de w no se intercalan (ninguno se intercala, pero ya eso alcanza)
def graphregen(curNodePa, curNode, wordlen):
    print "REGENERANDO EL GRAFO----"
    
    j = wordlen - 1

    nodoAnterior = None
    tipoEnlaceAnterior = None
    primerUp = False
    nodoSinUnir = None
    
    while not curNodePa is None:
        
        print "Estudiando: ", curNodePa.thisNode.letra, " vs ", 
        
        if not curNode is None:
            print curNode.letra
        else:
            print " CURNODE SE ACABO"
            
        print curNodePa.mov[j]
        
        
        if curNodePa.mov[j] == MOV_IZQUIERDA:
            print "IZQ"
            primerUp = False
                        
            while curNodePa.mov[j] == MOV_IZQUIERDA:
                print "CURNODE ES ", curNode.letra
                # Se crea el nuevo nodo
                nNode = Node()
                nNode.letra = curNode.letra
                
                if not nodoAnterior is None:
                    enlazar(nodoAnterior, nNode, tipoEnlaceAnterior)
                
                nodoAnterior = nNode
                nodoSinUnir = nNode
                
                tipoEnlaceAnterior = get_first(curNode.parentNodes)
                
                curNode = get_first(curNode.parentNodes)
                
                j -=1
            
        else:
            
            
            
            if curNodePa.mov[j] == MOV_DIAGONAL:
                print "DIAG"
                primerUp = True
                
                if not nodoSinUnir is None:
                    enlazar(nodoSinUnir, curNodePa.thisNode, tipoEnlaceAnterior)
                    nodoSinUnir = None
                elif not nodoAnterior is None:
                    # Arista completamente comun
                    # Hubo un nodo anterior
                    # y ademas tambien era coincidente
                    debilitar(curNodePa.thisNode, nodoAnterior,tipoEnlaceAnterior)
                    
                j = j -1
                
                
                tipoEnlaceAnterior = get_first(curNode.parentTypes)
                
                curNode = get_first(curNode.parentNodes)
                
                nodoAnterior = curNodePa.thisNode
            else:
                if not nodoAnterior is None and primerUp and not curNode is None:
                    print "TENGO QUE UNIR: ", nodoAnterior.letra, " con ", str(curNode.letra)
                    enlazar(nodoAnterior, curNode, tipoEnlaceAnterior)
                    print " NO ES DIAG "
                
                primerUp = False
                
            
            curNodePa = curNodePa.lpoint
        
    return 0
    
def plot(node):
    
    file = open("test.dot", "w")
    file.write("digraph pcspec {\n\n");
    
    visited = {}
    i = 1
    for lnode in node.n:
        curNode = lnode
        while not curNode is None:
            if curNode in visited:
                break
            visited[curNode] = True
            
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
    
def plot_simple(node):
    
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
            file.write(letra2 + "->" + letra + ' [ label="' + letra2 + ' a ' + letra + '" ]; \n')
    file.write("}");
    file.close()
    os.system("dot test.dot -T jpg > out2.jpg && eog out2.jpg")
    
def printTreeValues(n, j):
    
    if n is None:
        print "---"
        return 0;
    
    printTreeValues (n.refNode[j],n.refNodePos[j])
    
    
    print n.letra,
    print n.refNodePos
        
    return 0

# Devuelve el largo de un grafo de camino
def largo(g):
    if g.parentNodes:
        return 1 + largo (g.parentNodes[0])
    
    else:
        return 1

def merge(g1,g2):
        
    maxVal   = 0
    maxRatio = 0

    # Largo de la nueva palabra
    seqLen = largo(g2)
    
    
    preparar_grafo_lcs(g1, seqLen)

    
    for p in g1.n:
        
        
        nVal = calcN(p, g2, seqLen-1)
        nRatio = (float)(nVal-1) / max(p.length, seqLen)
        
        # Determinamos si es el mas parecido hasta el momento o no
        if  nVal >= maxVal and nRatio > maxRatio:
            maxRatio = nRatio
            maxVal = nVal
            
            caminoMasSimilar = p

    print "RATIO: ", nRatio
    # Si hay diferencias, combinamos
    if nRatio < 1:
        graphregen(caminoMasSimilar, g2, seqLen)
        
def clear(g):
    if g is None:
        return
        
    for n in g.n:
        if not n.lpoint is None:
            clear(n.lpoint.thisNode)
        del n
    del g.n
    g.n = []



def bad(prevNode, curNode):
    # Esta mal la arista prevNode->curNode
    
    # Quitar arista
    # Verificar que no quede una isla
    
    print "Borrando la arista ", prevNode.letra, " a ", curNode.letra
    
    for n in curNode.childNodes:
        print "Enlazando ", prevNode.letra, " con ", n.letra
        enlazar(n, prevNode, Node.LINK_ORD)
    
    desenlazar(curNode, prevNode)
    
    # Si no tiene padres lo borramos
    if not curNode.parentNodes:
        for n in curNode.childNodes:
            # hay que quitar los enlaces hacia los hijos
            desenlazar(n, curNode)
        del n
    
        
def come(node, ncorrida):
    nodo_inicio = get_nodos_padre(ncorrida)[0] # deberia ser uno solo
    
    #ncorrida es el init de la otra, hay que sacar ese nodo
    for n in node.childNodes:
        desenlazar(n, node)
        
        # Enganchamos los que X que node->X
        for nodo_nuevo in ncorrida.parentNodes:
            enlazar(n, nodo_nuevo, Node.LINK_ORD)
        
    # Hay que desaparecer el INIT viejo
    for nodo_nuevo in ncorrida.parentNodes:
        desenlazar(ncorrida, nodo_nuevo)
    del ncorrida
    
    enlazar(nodo_inicio, node, Node.LINK_ORD)
    

a = Aux()

g1 = a.sampleGraph1() # G1 sera el acumulado hasta el momento
g2 = a.sampleGraph2() # G2 es una nueva corrida
g3 = a.sampleGraph3() # G3 es una nueva corrida
g4 = a.sampleGraph4() # G3 es una nueva corrida


#plot(g1)

merge(g1, g2)

plot_simple(g1)

bad(g1.parentNodes[0].parentNodes[0].parentNodes[0],g1.parentNodes[0].parentNodes[0])

plot_simple(g1)

clear(g1)

come(g1.parentNodes[0].parentNodes[0], g4)


plot_simple(g1)

#largo_palabra = largo(g3)

#preparar_grafo_lcs(g1, largo_palabra)

#plot(g1)


merge(g1, g3)

plot(g1)

clear(g1)


plot_simple(g1)
