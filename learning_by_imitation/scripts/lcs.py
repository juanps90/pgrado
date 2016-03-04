#!/usr/bin/env python

import os



MejorCamino=[]
topologiaGeneral=[]
networkGeneral=[]
parComp={}
diccionario={}


#lo siguente es lo que hice en maestro ahi se usa para cada nodo aca se deberia usar
#un metodo que solo busque los caminos al init 

def sucesoresTopologicos (topologia):
    salida={}
    #dada una topologia el diccionario guarda como clave el id del nodo
    #y como valores una lista de los sucesores
    for t in topologia:
        if not salida.has_key(t[0]):
            salida[t[0]]=[]
        salida[t[0]].append(t[1])
    return salida

def nodosIniciales(topologia):
    aux={}
    salida =[]
    for t in topologia:
        #se agrega el predecesor como un posible nodo inicial
        if not aux.has_key(t[0]):
            aux[t[0]]=True
        #el otro ya posee antecesor
        aux[t[1]]=False
    for a in aux :
        if aux[a]:
            salida.append(a)        
    return salida



    
#Tal vez se podria primero ver los que no tienen predecesores y lanzar esos por temas de eficiencia
#aca se recorren todos los nodos y se hace el algoritmo
def todosLosCaminos( topologia):
    #los nodos son un dicc, cada nodo tene una lista de path y cada path es una lista de nodos
    salida =[]
    iniciales= nodosIniciales(topologia)
    sucesores= sucesoresTopologicos (topologia)
    #print "sucesores",sucesores
    for nodo in iniciales:#para cada nodo inicial
        #print "Nodo ",nodo
        recursionEnvioPath(nodo,[], salida,sucesores)   
         
    return salida    
    

#recursivamente se agregan nodos a los caminos
def recursionEnvioPath(nodo, pathAdd, caminos, sucesores):
    path=list(pathAdd)
    path.append(nodo)
    #print "sucesores",sucesores
 
    if nodo in sucesores:
        for sucesor in sucesores[nodo]:
            print "caminos",caminos
            recursionEnvioPath(sucesor,path, caminos,sucesores)
    else:
        caminos.append(path)
    return caminos
 

 

def todosLosSucesores( topologia):
    #los nodos son un dicc, cada nodo tene una lista de path y cada path es una lista de nodos
    salida ={}
    iniciales= nodosIniciales(topologia)
    sucesores= sucesoresTopologicos (topologia)
    #print sucesores
    for nodo in iniciales:#para cada nodo inicial
        #print "Nodo ",nodo
        recursionSucesores(nodo, salida,sucesores)   
         
    return salida    


#se recibe un path, se verifica si hay un path que concida hasta el final
#en tal caso se sobreescribe el path mas corto que habia, la idea es que algun otro nodo se agrego al path..
#luego el nuevo path se envia a los nodos sucesores de forma recursiva
def recursionSucesores(nodo,  sucesores, sucesoresTopologicos):
    if not sucesores.has_key(nodo):    
        sucesores[nodo]=[]
    if nodo in sucesoresTopologicos:        
        for sucesor in sucesoresTopologicos[nodo]:            
            if  not sucesor in sucesores[nodo]:
                sucesores[nodo].append(sucesor)  
            sucesores[nodo] =sucesores [nodo]+recursionSucesores(sucesor, sucesores,sucesoresTopologicos)  
    sucesores[nodo]=list(set( sucesores[nodo]))
    #print sucesores
    return sucesores[nodo]












#########################################################


def compararParamComportamiento(x,y):
    global paramCom
    global diccionario
    '''
    #aca se deberia comparar por parametros tambien hay que tener
    #en cuenta un cierto margen de error
    if diccionario[x]==diccionario[y]:
        parX=paramCom[x]
        parY=paramCom[y]
        for px in parX:
            lista=parX
            for 
    '''
    return diccionario[x]==diccionario[y]
    
     


def  LCSLength(X,Y):
    m=len(X)+1
    n=len(Y)+1
    print  "m y n en LCS: ",m,n
    C = [range(n) for i in range(m)]
    for i in  range (m):
       C[i] [0]= 0
    for j in  range (n):
       C[0] [j]= 0
    for i in  range (1,m):
         for j in  range (1,n):
            if compararParamComportamiento(X[i-1],Y[j-1]):
                C[i] [j] = C[i-1] [j-1] + 1
            else:
                C[i] [j] = max(C[i] [j-1], C[i-1] [j])
    return C


        


def backtrack(C , X , Y, i, j,sentido):
    if i == 0 or j == 0:
        return "100"

    if  compararParamComportamiento(X[i-1] ,  Y[j-1] ) :        
        idx=str( X[i-1])
        idy=str( Y[j-1])
        X[i-1] =Y[j-1]
        #return backtrack(C, X, Y, i-1, j-1) + X[i-1][0]
        return backtrack(C, X, Y, i-1, j-1,'d') +"&"+ idx +"&"+idy
    else:
        #si son iguales tomo el sentido diferente de modo que los caminos sean lo mas corto
        #sino pasa el ejemplo del 8 que termina armando path del doble del largo /se ve mejor
        #por imagenes
        if C[i] [j-1] == C[i-1] [j]:
            if sentido=='i':
                 return backtrack(C, X, Y, i, j-1,'j')
            else:
                return backtrack(C, X, Y, i-1, j,'i')        
        elif C[i] [j-1] > C[i-1] [j]:
            return backtrack(C, X, Y, i, j-1,'j')
        else:
            return backtrack(C, X, Y, i-1, j,'i')

 




def graficarTopologia(topologia,idArchivo):
    file = open (idArchivo+".dot","w")

    file.write("digraph pcspec{\n\n")  

    for t in topologia:
        label=str(diccionario[t[0]])+ "-"+str(diccionario[t[1]])
        file.write(str(t[0])+ "->"+str(t[1])+' [ label="' + label + '" ]; \n') 
    file.write("}")
    file.close()
    os.system("dot "+idArchivo+".dot -T jpg > "+idArchivo+".jpg && eog "+idArchivo+".jpg ")




def graficarNetwork(network,idArchivo):
    print "network ",network
    file = open (idArchivo+".dot","w")

    file.write("digraph pcspec{\n\n")  

    for t in network:
        link=t[2]
        if link==0:
            tipoLink="Ord"
        elif link==1:
            tipoLink="Hab"
        elif link==2:
            tipoLink="Per"
        origen=str(t[0])
        destino=str(t[1])          
        file.write( origen+ "->"+destino+' [ label="' + tipoLink + '" ]; \n')
 
    file.write("}")
    file.close()
    os.system("dot "+idArchivo+".dot -T jpg > "+idArchivo+".jpg && eog "+idArchivo+".jpg ")


def graficar(idArchivo):
    global topologiaGeneral
    global networkGeneral
    graficarNetwork(networkGeneral,idArchivo)
    graficarTopologia(topologiaGeneral,idArchivo)



###############################################3





def tranTopoACamino(topologia):
    salida=[]
    aux={}
    nodo=nodosIniciales(topologia)[0]
    salida.append(nodo)
    for n in range(len(topologia)):	
        aux[topologia[n][0] ]=topologia[n][1]
    while aux.has_key(nodo):
        salida.append(aux[nodo])
        nodo=aux[nodo]

    print "topologia camino",topologia
 
    return salida


def tranComCamATopologia(X): 
    salida=[]
    for t in range(len(X)-1): 
        salida.append ((X[t],X[t+1]))
    return salida



def obtenerMejorAjuste (X,topologia,diccionario):
    global MejorCamino
    MejorCamino=[]

    '''
    nuevoCamino=tranTopoACamino(topologiaNueva)
    # print nuevoCamino
    X=asociarCompPorCaminos(nuevoCamino, diccionario)
    # print X
    '''
    #print X

    caminos=todosLosCaminos  (topologia)

    print "caminos: ",  caminos
 
    maxLargo=-1
    tablaAGuardar=[]

    for c in caminos:
        Y= c
        Tabla= LCSLength(X,Y)
        print "tabla" , Tabla
        m=len(Tabla)
        n=len (Tabla[m-1])        
        auxMax=Tabla[m-1][n-1]
            
        if auxMax >  maxLargo :
            maxLargo=auxMax
            tablaAGuardar=Tabla
            MejorCamino=Y
    return tablaAGuardar
 
#teniendo todos los caminos se compara el nuevo con cada camino con cada camino hallado

#la comparacion que resulte con mas semejanzas es es la que se mergea

#se asocia para cada camino el id del nodo con un comportamiento en nuestro caso letas


def anexarNuevaTopologia(topologia,anexar):
    #todo para evitar meter un link repetido
    aux={}
    salida=list(topologia)
    for t  in topologia:
        if not aux.has_key(t[0]):
            aux[t[0]]=[ ]
        aux[t[0]]=aux[t[0]] +[t[1]]
    print "auxiliar topologia ",aux
    
    for a in anexar:
        if aux.has_key(a[0]):
            if not a[1] in aux[a[0]]:
                #print "",a,a[0],a[1],aux[a[0]]
                salida.append(a)
        else:
            salida.append(a)
    return salida







def  igualar(nuevoNetwork,iguales):
    network=list(nuevoNetwork)
    del iguales[0]
    for i in range(len(iguales)/2):
        for n in range (len(network)):
            #cambia origen y destino del network
            indice=2*i
            #print iguales[indice]," iguales ",iguales[indice+1]
            
            if network[n][0]==iguales[indice]:
                cambio=(iguales[indice+1],network[n][1],network[n][2])
                network[n]=cambio
            elif network[n][1]==iguales[indice]:
                cambio=(network[n][0],iguales[indice+1],network[n][2])
                network[n]=cambio 
    return network


def anexarNuevoNetwork (topologia,network,anexar):
    #se comparan los iniciales finales y luego el tipo de link si es menor
    #restrictivo se lo cambia por el nuevo si no estaba se lo agrega
    auxEnlaces={}
    salida=list(network)
    salida=sorted( salida, key=lambda tuple: tuple[0])
    anexar=sorted( anexar, key=lambda tuple: tuple[0])
    #print salida, anexar
    for a in  anexar :
        nuevo=True
        for s in range (len(salida)): 
            #print a[0],a[1],salida[s][0],salida[s][1]
            if a[0]==salida[s][0]:
                if a[1]==salida[s][1]:
                    nuevo=False
                    #print a
                    if a[2]<salida[s][2]:
                        salida[s]=a 
        if nuevo:
            salida.append(a)
            
    #para el network se necesita obtener la relacion entre nodos con igual id,
    #agregar los links nuevos si no pertenecian, en caso de existir otro enlace a los mismos nodos
    
    #se agregan link de orden a los enlaces que no existan
    sucesores= todosLosSucesores( salida)
    for s in range (len(salida)):
        #de paso creo el diccionario de enlacces
        if not auxEnlaces.has_key(salida[s][0]):
            auxEnlaces[salida[s][0]]=[]
        if not   salida[s][1]  in auxEnlaces[salida[s][0]]:                
            auxEnlaces[salida[s][0]].append(salida[s][1])

    
    print "sucesores",sucesores
    print "auxEnlaces ",auxEnlaces
    print "salida ann ",salida
    for s in sucesores :
        for e in sucesores[s]:
            if not e in auxEnlaces[s]:
                salida.append((s,e,0))
               
    return salida







#hay que determinar cuales son los sucesores de un nodo luego verificar si hay enlace para sus sucesores
#si no los hay agregar de orden

#por backtraking obtengo todos los sucesores 

#para cada sucesur se verifica en el diccionario con clave el nodo actual, si no esta se agrega un link de orden



def getNetworkGeneral():
    global networkGeneral
    return networkGeneral

def getTopologiaGeneral():
    global topologiaGeneral
    return topologiaGeneral

def getDicParametros():
    global parComp
    return parComp

def getDicComportamientos():
    #esto solo para probar ejecutar sin demostrar
    global topologiaGeneral
    global diccionario
    global networkGeneral
    global parComp
    if len (diccionario)==0:
        #diccionario={0:1,1:2,2:0}
        parComp={0:{0:[0,0,0]},1:{0:[2,2,2]}}
        diccionario={0:"localizar",1:"avanzar",2:"init"}
        networkGeneral=[(0,1,2),(0,2,0),(1,2,0)]
        topologiaGeneral=[(0,1),(1,2)]
    return diccionario




def setNetworkGeneral(network):
    global networkGeneral
    networkGeneral=network

def setTopologiaGeneral(topologia):
    global topologiaGeneral
    topologiaGeneral=topologia


#ARREGLAR ACA ES APPEND
def setDicParametros(param):
    global parComp
    parComp =param

def appendDicCom(comp):
    global diccionario
    diccionario =comp


def getNewId():
    global topologiaGeneral
    salida = -1
    for t in topologiaGeneral:
        if t[0]>salida:
            salida = t[0]
        if t[1]>salida:
            salida = t[1]
            
    return salida+1

def nuevaDemostracion(topologiaNueva,networkNueva):
    global MejorCamino
    global topologiaGeneral
    global networkGeneral
    global diccionario
    X=tranTopoACamino(topologiaNueva)
    #X=asociarCompPorCaminos(nuevoCamino, diccionario)
    MA=obtenerMejorAjuste (X,topologiaGeneral,diccionario)

    Y=MejorCamino

    print "mejorAjuste: ",MA
    print "X Y: ",X,Y
    
    comun=backtrack(MA , X , Y,len(X),len(Y),'d')
    iguales=map (int, comun.split("&"))

    print "iguales",iguales,comun

 
    anexar=igualar(networkNueva,iguales)
    print "anexar",anexar
    networkGeneral=anexarNuevoNetwork (topologiaGeneral,networkGeneral,anexar)
    
    
    print "backtrack: ", comun
    anexar= tranComCamATopologia(X)    
    topologiaGeneral=anexarNuevaTopologia(topologiaGeneral,anexar)
    print "topologia",topologiaGeneral
    graficarTopologia(topologiaGeneral,"topologia")
    graficarNetwork(networkGeneral,"network")
    return topologiaGeneral






#Nota los links no tienen un orden en la lista, el nodo init no se debe borrar (controlar en el q llama a este metodo)
#por caminos solo elimina el enlace entre el previo y el nodo a eliminar y agrega un links entre previo y siguientes 
#del nodo idBad
def borrarNodoBadCaminos(idBad, idPrevio):
    global topologiaGeneral
    global networkGeneral

    #primero borra de la topologia
    
    #creo la lista de destinos del nodo a borrar
    listaDestino=[]
    numPredecesores=0#se cuenta el numero de predecesores del nodo a borrar si solo tiene uno se borra todo el nodo
    print "topo bad ",topologiaGeneral
    for d in range(len(topologiaGeneral)):
        if (topologiaGeneral[d][0]==idBad):
            #se agregan los id y comportamiento a listaDestino 
            listaDestino.append( topologiaGeneral[d][1])
        if topologiaGeneral[d][1]==idBad:
            numPredecesores=numPredecesores+1
    
    print "topo 2 bad",topologiaGeneral

    #so}i el nodo a borrar tiene varios predecesores se elimina solo el tramo del camino que tiene a idPrevio
    if numPredecesores > 1:
        #de idPrevio agrega links a los destinos del nodo a borrar
        for d in range(len(listaDestino)):    
            #se agregan links de orden entre los origens de los nodos y los destinos del nodo borrado 
            topologiaGeneral.append( (idPrevio,listaDestino[d]) )
        
        #se eliminan los links que tengan a idprevio como destino y a idBad como destino se supone sea uno solo
        for b in range(len(topologiaGeneral)-1,-1,-1):
            if (topologiaGeneral[b][0]==idPrevio and topologiaGeneral[b][1]==idBad):
                del topologiaGeneral[b]
            
        #para eliminar posibles repetidos en el caso del paper seria borrar el nodo C de arriba
        topologiaGeneral = list(set(topologiaGeneral))

        #se busca el enlace que tenga como origen a idPrevio y destino idBad se lo
        #borra si no es de orden y se pone uno de orden
        for b in range(len(networkGeneral)-1,-1,-1):
            if (networkGeneral[b][0]==idPrevio and networkGeneral[b][1]==idBad and networkGeneral[b][2]>0):
                del networkGeneral[b]
                networkGeneral.append((idPrevio,idBad,0)) 
    #se borra el nodo completo si solo hay un predecesor           
    else :    
        borrarNodoBad(idBad)




 



#Nota los links no tienen un orden en la lista, el nodo init no se debe borrar (controlar en el q llama a este metodo)
def borrarNodoBad(idBad):
    global topologiaGeneral
    global networkGeneral

    #primero borra de la topologia
    
    #creo la lista de destinos del nodo a borrar
    listaDestino=[]
    print "topo bad ",topologiaGeneral
    for d in range(len(topologiaGeneral)):
        if (topologiaGeneral[d][0]==idBad):
            #se agregan los id y comportamiento a listaDestino 
            listaDestino.append( topologiaGeneral[d][1])    
                    
    print "destinos del nodo borrado",listaDestino
            
    #de los que son origen del nodo a borrar agrega los destinos del nodo a borrar
    for l in range(len(topologiaGeneral)):
        if (topologiaGeneral[l][1]==idBad):#idborrar es destino del links
            for d in range(len(listaDestino)):    
                #se agregan links de orden entre los origens de los nodos y los destinos del nodo borrado 
                topologiaGeneral.append( (topologiaGeneral[l][0],listaDestino[d]) )
    
    print "topo 2 bad",topologiaGeneral
    
    #se eliminana todos los links que tengan a idborrar como origen o destino
    for b in range(len(topologiaGeneral)-1,-1,-1):
        if (topologiaGeneral[b][0]==idBad or topologiaGeneral[b][1]==idBad):
            del topologiaGeneral[b]
    #para eliminar posibles repetidos en el caso del paper seria borrar el nodo C de arriba
    topologiaGeneral = list(set(topologiaGeneral))

    #segundo borra de la network
    
    #se eliminana todos los links que tengan a idborrar como origen o destino
    for b in range(len(networkGeneral)-1,-1,-1):
        if (networkGeneral[b][0]==idBad or networkGeneral[b][1]==idBad):
            del networkGeneral[b] 


#para no repetir id se pregunta antes de una demo el id mas alto y de ahi se empiezan a contar
def getMaxIdNodo():
    salida=-1
    for d in diccionario:
        if d >salida :
            salida=d
    return salida+1







#no importa si la demo trae o no el nodo init se contemplan ambos casos
#se supone que no hay id repetidos de la nueva demo 
def cortarGoCaminos(nuevaTopologia,nuevaNetwork,idCome,idPrevio):
    global topologiaGeneral
    global networkGeneral
    global diccionario
    
    if len(nuevaTopologia) ==0 or len(nuevaNetwork) ==0  :
        print "links de tamano cero en cortar"
        return topologiaGeneral


    #se verifica si al intentar agregar no hay un tramo igual entre los nodos idPrevio e idCome
    caminos= todosLosCaminos( topologiaGeneral)
    nuevoCamino=tranTopoACamino(nuevaTopologia)

    for c in caminos:
        if idPrevio in c and idCome in c:
            inicio=c.index(idPrevio)+1
            fin = c.index(idCome)
            encontre=True
            if inicio==fin:
                encontre=False
            for v in range (inicio ,fin):
                x=nuevoCamino[v-inicio]
                y=c[v]               
                if not compararParamComportamiento(x,y):
                    encontre=False
                    break
            if encontre:
                print "el camino agregado ya existia"
                return
   
   
    #diccionarios con clave el id del nodo y valor el id del comportamiento
    predecesores=[]
    sucesores=[]
     

    #agrega en la topologia

    #el inicial se agrega como sucesor de los predecesores de idcome
    #el final tiene de sucesor solo al idcome                                   
    final=-1
    camino=tranTopoACamino(nuevaTopologia)
    inicial=camino[0]
    final=camino[ len(camino)-1 ]
    
    #se elimina el enlace al nodo init y se determina el nodo final en realidad el final si hay init es el
    #es camino el nodo anterior al init
    if diccionario[final] ==0:#no se agrega el init
        for n in nuevaTopologia: 
            if diccionario[n[1]] ==0:#no se agrega el init
                final=n[0]
                nuevaTopologia.remove(n)
                break            
 

    #se agrega al idcome como sucesor de la nueva topologia
    sucesores.append(idCome)
    '''
    #se recorre la topologia y se agregan predecesores
    #ademas se borran los enlaces que iban al idCome    
    for g in range (len(topologiaGeneral)-1,-1,-1):  
        if topologiaGeneral[g][1]==idCome and not (topologiaGeneral[g][0]  in predecesores ):
            predecesores.append( topologiaGeneral[g][0] )
            topologiaGeneral.remove(topologiaGeneral[g])
    '''

            
    predecesores.append( idPrevio )
    for g in range (len(topologiaGeneral)-1,-1,-1):
        if topologiaGeneral[g][0]==idPrevio and topologiaGeneral[g][1]== idCome :                     
            topologiaGeneral.remove( (idPrevio,idCome))      
 
            
    print "nuevaTopologia ",nuevaTopologia   
       
    print "predecesores  ",predecesores
    print "sucesores ",sucesores 
            
    for p in predecesores: 
        topologiaGeneral.append((p,inicial))
    for s in sucesores:
        topologiaGeneral.append((final,s))
            
    topologiaGeneral=list(set(topologiaGeneral+nuevaTopologia))
    
 
    #agrega en la network
    
    predecesores=[]
    sucesores=[]
    nuevos=[]

    for g in range (len( networkGeneral)-1,-1,-1):
        if networkGeneral[g][0]==idPrevio and networkGeneral[g][1]== idCome and  networkGeneral[g][2]>0:                     
            networkGeneral.remove( networkGeneral[g])      
            networkGeneral.append((idPrevio,idCome,0))

    #se agrega al idcome como sucesor de la nueva network
    sucesores.append(idCome)
    #se agrega al idPrevio como predecesor de la nueva network
    predecesores.append( idPrevio)
    #se recorre la network y se agregan sucesores y predecesores
    for g in networkGeneral:  
        if g[1]==idPrevio and not (g[0]  in predecesores ):
            predecesores.append(g[0])
        if g[0]==idCome and not (g[1]  in sucesores): 
            sucesores.append(g[1])
            
    print     "nuevaNetwork",    nuevaNetwork
    for n in range (len(nuevaNetwork)-1,-1,-1):       
        #se agregan nodos nuevos a una lista
        if not (  nuevaNetwork[n][0] in nuevos ): 
            nuevos.append(nuevaNetwork[n][0])
        if not (nuevaNetwork[n][1] in nuevos ):
            if diccionario[nuevaNetwork[n][1]] !=0:#no se agrega el init
                nuevos.append(nuevaNetwork[n][1])
            else:
                nuevaNetwork.remove(nuevaNetwork[n])
                  
    print "nuevos ",nuevos
    print "predecesores  ",predecesores
    print "sucesores ",sucesores 
            
    for n in nuevos:
        for p in predecesores: 
            networkGeneral.append((p,n,0))
        for s in sucesores:
            networkGeneral.append((n,s,0)) 
    networkGeneral=list(set(networkGeneral+nuevaNetwork))
     

 








#no importa si la demo trae o no el nodo init se contemplan ambos casos
#se supone que no hay id repetidos de la nueva demo
def cortarGo(nuevaTopologia,nuevaNetwork,idCome):
    global topologiaGeneral
    global networkGeneral
    global diccionario
    
    if len(nuevaTopologia) ==0 or len(nuevaNetwork) ==0  :
        print "links de tamano cero en cortar"
        return topologiaGeneral

    #se verifica si al intentar agregar el nuevo tramo ya no habia un tramo igual y entonces no se agrega

    #HACER


   
    #diccionarios con clave el id del nodo y valor el id del comportamiento
    predecesores=[]
    sucesores=[]
     

    #agrega en la topologia

    #el inicial se agrega como sucesor de los predecesores de idcome
    #el final tiene de sucesor solo al idcome                                   
    final=-1
    camino=tranTopoACamino(nuevaTopologia)
    inicial=camino[0]
    final=camino[ len(camino)-1 ]
    
    #se elimina el enlace al nodo init y se determina el nodo final en realidad el final si hay init es el
    #es camino el nodo anterior al init
    if diccionario[final] ==0:#no se agrega el init
        for n in nuevaTopologia: 
            if diccionario[n[1]] ==0:#no se agrega el init
                final=n[0]
                nuevaTopologia.remove(n)
                break            
 

    #se agrega al idcome como sucesor de la nueva topologia
    sucesores.append(idCome)

    
    #se recorre la topologia y se agregan predecesores
    #ademas se borran los enlaces que iban al idCome    
    for g in range (len(topologiaGeneral)-1,-1,-1):  
        if topologiaGeneral[g][1]==idCome and not (topologiaGeneral[g][0]  in predecesores ):
            predecesores.append( topologiaGeneral[g][0] )
            topologiaGeneral.remove(topologiaGeneral[g])
            

            
    print "nuevaTopologia ",nuevaTopologia   
       
    print "predecesores  ",predecesores
    print "sucesores ",sucesores 
            
    for p in predecesores: 
        topologiaGeneral.append((p,inicial))
    for s in sucesores:
        topologiaGeneral.append((final,s))
            
    topologiaGeneral=list(set(topologiaGeneral+nuevaTopologia))
    
 



    #agrega en la network

    predecesores=[]
    sucesores=[]
    nuevos=[]

    #se agrega al idcome como sucesor de la nueva network
    sucesores.append(idCome)
    #se recorre la network y se agregan sucesores y predecesores
    for g in networkGeneral:  
        if g[1]==idCome and not (g[0]  in predecesores ):
            predecesores.append(g[0])
        if g[0]==idCome and not (g[1]  in sucesores): 
            sucesores.append(g[1])
            
    print     "nuevaNetwork",    nuevaNetwork
    for n in range (len(nuevaNetwork)-1,-1,-1):       
        #se agregan nodos nuevos a una lista
        if not (  nuevaNetwork[n][0] in nuevos ): 
            nuevos.append(nuevaNetwork[n][0])
        if not (nuevaNetwork[n][1] in nuevos ):
            if diccionario[nuevaNetwork[n][1]] !=0:#no se agrega el init
                nuevos.append(nuevaNetwork[n][1])
            else:
                nuevaNetwork.remove(nuevaNetwork[n])
                  
    print "nuevos ",nuevos
    print "predecesores  ",predecesores
    print "sucesores ",sucesores 
            
    for n in nuevos:
        for p in predecesores: 
            networkGeneral.append((p,n,0))
        for s in sucesores:
            networkGeneral.append((n,s,0)) 
    networkGeneral=list(set(networkGeneral+nuevaNetwork))
     

 




######################################### 

def probarLCS():

    global parComp
    global diccionario

    parComp={0:{},1:{},2:{},3:{},4:{},5:{},6:{},7:{},8:{}}
    diccionario={0:1,1:1,2:0}
    network=[(0,1,2),(1,2,0),(0,2,0)]
    network=[]
    topologia=[(0,1),(1,2)]
    topologia=[]
    topologiaNueva=[(0,1),(1,2)]
    nuevaNetwork=[(0,1,2),(1,2,0),(0,2,0)]
    topologia=nuevaDemostracion(topologiaNueva,nuevaNetwork)

def probarLCSPapper():

    global parComp
    global diccionario
    global topologiaGeneral
    global networkGeneral
    parComp={0:{},1:{},2:{},3:{},4:{},5:{},6:{},7:{},8:{},9:{},10:{},11:{}}
    #diccionario={0:1,1:3,2:2,3:6,4:1,5:1,6:2,7:6,8:3,9:5,10:3,11:0}

    diccionario={0:"A",1:"C",2:"B",3:"F",4:"A",5:"A",6:"B",7:"F",8:"C",9:"E",10:"F",11:0}

    
    topologiaGeneral=[(0,1),(1,2),(2,3),(3,4)]
    networkGeneral=[(0,2,2),     (0,1,0),(1,2,2),(2,3,0),(3,4,0),(0,3,0),(0,4,2),(1,3,0),(1,4,2),(2,4,2)]
    #print todosLosSucesores( topologia) 
    #anexar=[(0,1,1),(1,2,2),(0,2,0)]
    #print anexarNuevoNetwork (network,anexar)
    #graficarNetwork(network)
    
    topologiaNueva=[(5,6),(6,7),(7,8)]
    nuevaNetwork=[ (5,6,2),      (5,7,0),(6,7,2),(7,8,1),(5,8,2),(6,8,2)]
    topologia=nuevaDemostracion(topologiaNueva,nuevaNetwork)
    print "topologia ", topologia
 

def probarBadCaminos():
    probarLCSPapper()
    global networkGeneral
    borrarNodoBadCaminos(2,1)#elegir el nodo a borrar el segundo es el id previo sino lo hay se pone -1
    graficarTopologia(topologiaGeneral,"topoluegoDeBadCaminos")
    graficarNetwork(networkGeneral,"netluegoDeBadCaminos")



def probarBad():
    probarLCSPapper()
    global networkGeneral
    
    borrarNodoBad(1)#elegir el nodo a borrar
    graficarTopologia(topologiaGeneral,"topoluegoDeBad")
    graficarNetwork(networkGeneral,"netluegoDeBad")
    
    borrarNodoBad(3)#elegir el nodo a borrar
    graficarTopologia(topologiaGeneral,"topoluegoDeBad")
    graficarNetwork(networkGeneral,"netluegoDeBad")
    


def probarComeHereGo():
    probarLCSPapper()

    
    
   # topologiaNueva=[(9,10),(10,11)]
 #   nuevaNetwork=[ (9,10,0),(9,11,0),(10,11,0)]

    topologiaNueva=[(9,10)]
    nuevaNetwork=[ (9,10,0)]
    
    cortarGo(topologiaNueva,nuevaNetwork,4)
    graficarTopologia(topologiaGeneral,"topoluegoDeGo")
    graficarNetwork(networkGeneral,"netluegoDeGo")



def probarComeHereGoCaminos():
    global diccionario
    diccionario={0:"A",1:"C",2:"B",3:"F",4:"A",5:"A",6:"B",7:"F",8:"C",9:"E",10:"C",11:"Z"}
    
    probarLCSPapper()
    
   # topologiaNueva=[(9,10),(10,11)]
 #   nuevaNetwork=[ (9,10,0),(9,11,0),(10,11,0)]

    #este agregado no se reflejara en el grafo porque existe un camino igual
    topologiaNueva=[(10,11)]
    nuevaNetwork=[ (10,11,0)]
    
    cortarGoCaminos(topologiaNueva,nuevaNetwork,8,2)
    graficarTopologia(topologiaGeneral,"topoluegoDeGo")
    graficarNetwork(networkGeneral,"netluegoDeGo")

    #se agrega un nuevo tramo
    topologiaNueva=[(9,11)]
    nuevaNetwork=[ (9,11,0)]
    
    cortarGoCaminos(topologiaNueva,nuevaNetwork,2,1)
    graficarTopologia(topologiaGeneral,"topoluegoDeGo")
    graficarNetwork(networkGeneral,"netluegoDeGo")

    #se agrega un nuevo tramo
    topologiaNueva=[(10,11)]
    nuevaNetwork=[ (10,11,0)]
    
    cortarGoCaminos(topologiaNueva,nuevaNetwork,2,0)
    graficarTopologia(topologiaGeneral,"topoluegoDeGo")
    graficarNetwork(networkGeneral,"netluegoDeGo")



def probarAlternancia():
    global parComp
    global diccionario
    global topologiaGeneral
    global networkGeneral
    parComp={0:{},1:{},2:{},3:{},4:{},5:{},6:{},7:{},8:{},9:{},10:{},11:{}}
   # diccionario={0:"A",1:"B",2:"C",3:"D",4:"E",5:"A",6:"X",7:"C",8:"Y",9:"E",10:"C",11:0}
    diccionario={0:"A",1:"X",2:"C",3:"Y",4:"E",5:"A",6:"Y",7:"C",8:"X",9:"E",10:"X",11:0, 12:"Y",13:"C",14:"X",15:0 }

    
    topologiaGeneral=[(0,1),(1,2),(2,3),(3,4)]
    networkGeneral=[(0,2,2),     (0,1,0),(1,2,2),(2,3,0),(3,4,0),(0,3,0),(0,4,2),(1,3,0),(1,4,2),(2,4,2)]
    
    topologiaNueva=[(5,6),(6,7),(7,8),(8,9)]
    nuevaNetwork=[ (5,6,2),      (5,7,0),(6,7,2),(7,8,1),(5,8,2),(6,8,2) , (5,9,0),(6,9,0),(7,9,0),(8,9,0)     ]
    topologia=nuevaDemostracion(topologiaNueva,nuevaNetwork)
 
    borrarNodoBad(2)#elegir el nodo a borrar
    graficarTopologia(topologiaGeneral,"topoluegoDeBadCaminos1")
    #graficarNetwork(networkGeneral,"netluegoDeBadCaminos1")


    borrarNodoBad(3)#elegir el nodo a borrar
    graficarTopologia(topologiaGeneral,"topoluegoDeBadCaminos1")
    #graficarNetwork(networkGeneral,"netluegoDeBadCaminos1")

    borrarNodoBad(8)#elegir el nodo a borrar
    graficarTopologia(topologiaGeneral,"topoluegoDeBadCaminos1")
    #graficarNetwork(networkGeneral,"netluegoDeBadCaminos1")



    topologiaNueva=[(10,11)]
    nuevaNetwork=[ (10,11,0)]
    
    cortarGoCaminos(topologiaNueva,nuevaNetwork,4,2)
    graficarTopologia(topologiaGeneral,"topoluegoDeGo1")
    #graficarNetwork(networkGeneral,"netluegoDeGo1")



    


'''
    borrarNodoBad(7)#elegir el nodo a borrar
    #graficarTopologia(topologiaGeneral,"topoluegoDeBadCaminos2")
    #graficarNetwork(networkGeneral,"netluegoDeBadCaminos2")
    
    borrarNodoBad(8)#elegir el nodo a borrar
    #graficarTopologia(topologiaGeneral,"topoluegoDeBadCaminos3")
    #graficarNetwork(networkGeneral,"netluegoDeBadCaminos3")

    topologiaNueva=[(10,11)]
    nuevaNetwork=[ (10,11,0)]
    
    cortarGoCaminos(topologiaNueva,nuevaNetwork,4,2)
    #graficarTopologia(topologiaGeneral,"topoluegoDeGo1")
    #graficarNetwork(networkGeneral,"netluegoDeGo1")

 

    topologiaNueva=[(12,13),(13,14),(14,15)]
    nuevaNetwork=[ (12,13,0),(12,14,0),(12,15,0),(13,14,0),(13,15,0),(14,15,0)]
    
    cortarGoCaminos(topologiaNueva,nuevaNetwork,4,0)
    graficarTopologia(topologiaGeneral,"topoluegoDeGo2")
    graficarNetwork(networkGeneral,"netluegoDeGo2")
'''



def probarAlternancia2():
    global parComp
    global diccionario
    global topologiaGeneral
    global networkGeneral
    parComp={0:{},1:{},2:{},3:{},4:{},5:{},6:{},7:{},8:{},9:{},10:{},11:{}}
   # diccionario={0:"A",1:"B",2:"C",3:"D",4:"E",5:"A",6:"X",7:"C",8:"Y",9:"E",10:"C",11:0}
    diccionario={0:"A",1:"X",2:"C",3:"Y",4:"E",5:"A",6:"Y",7:"C",8:"X",9:"E",10:"Y",11:0, 12:"Y",13:"C",14:"X",15:0 }

    
    topologiaGeneral=[(0,1),(1,2),(2,3),(3,4)]
    networkGeneral=[(0,2,2),     (0,1,0),(1,2,2),(2,3,0),(3,4,0),(0,3,0),(0,4,2),(1,3,0),(1,4,2),(2,4,2)]
    
    topologiaNueva=[(5,6),(6,7),(7,8),(8,9)]
    nuevaNetwork=[ (5,6,2),      (5,7,0),(6,7,2),(7,8,1),(5,8,2),(6,8,2) , (5,9,0),(6,9,0),(7,9,0),(8,9,0)     ]
    topologia=nuevaDemostracion(topologiaNueva,nuevaNetwork)
 
    borrarNodoBadCaminos(3,2)#elegir el nodo a borrar
    graficarTopologia(topologiaGeneral,"topoluegoDeBadCaminos1")
    graficarNetwork(networkGeneral,"netluegoDeBadCaminos1")

'''
    borrarNodoBad(7)#elegir el nodo a borrar
    #graficarTopologia(topologiaGeneral,"topoluegoDeBadCaminos2")
    #graficarNetwork(networkGeneral,"netluegoDeBadCaminos2")
    
    borrarNodoBad(8)#elegir el nodo a borrar
    #graficarTopologia(topologiaGeneral,"topoluegoDeBadCaminos3")
    #graficarNetwork(networkGeneral,"netluegoDeBadCaminos3")

    topologiaNueva=[(10,11)]
    nuevaNetwork=[ (10,11,0)]
    
    cortarGoCaminos(topologiaNueva,nuevaNetwork,4,2)
    #graficarTopologia(topologiaGeneral,"topoluegoDeGo1")
    #graficarNetwork(networkGeneral,"netluegoDeGo1")

 

    topologiaNueva=[(12,13),(13,14),(14,15)]
    nuevaNetwork=[ (12,13,0),(12,14,0),(12,15,0),(13,14,0),(13,15,0),(14,15,0)]
    
    cortarGoCaminos(topologiaNueva,nuevaNetwork,4,0)
    graficarTopologia(topologiaGeneral,"topoluegoDeGo2")
    graficarNetwork(networkGeneral,"netluegoDeGo2")
 '''

    
    
#Estos son lo que estan mejor 
#probarComeHereGoCaminos()
#probarBad()

#el comeHereGo no le hice verificar que no haya un camino igual
#probarBadCaminos()
#probarComeHereGo()

'''
topologiaNueva=[(4,5)] 
topologia=nuevaDemostracion(topologia,topologiaNueva,network,nuevaNetwork,diccionario)
print "topologia ", topologia


topologiaNueva=[(6,7)] 
topologia=nuevaDemostracion(topologia,topologiaNueva,network,nuevaNetwork,diccionario)
print "topologia ", topologia

topologiaNueva=[(8,9)] 
topologia=nuevaDemostracion(topologia,topologiaNueva,network,nuevaNetwork,diccionario)
print "topologia ", topologia
       
'''

    

'''

    borrarNodoBadCaminos(8,2)#elegir el nodo a borrar
    graficarTopologia(topologiaGeneral,"topoluegoDeBadCaminos2")
    #graficarNetwork(networkGeneral,"netluegoDeBadCaminos")

    borrarNodoBadCaminos(3,2)#elegir el nodo a borrar
    graficarTopologia(topologiaGeneral,"topoluegoDeBadCaminos2")
    #graficarNetwork(networkGeneral,"netluegoDeBadCaminos")

    borrarNodoBadCaminos(8,1)#elegir el nodo a borrar
    graficarTopologia(topologiaGeneral,"topoluegoDeBadCaminos2")
    #graficarNetwork(networkGeneral,"netluegoDeBadCaminos")

    borrarNodoBadCaminos(4,1)#elegir el nodo a borrar
    graficarTopologia(topologiaGeneral,"topoluegoDeBadCaminos2")
    #graficarNetwork(networkGeneral,"netluegoDeBadCaminos")



    topologiaNueva=[(10,11)]
    nuevaNetwork=[ (10,11,0)]
    
    cortarGoCaminos(topologiaNueva,nuevaNetwork,3,1)
    graficarTopologia(topologiaGeneral,"topoluegoDeGo")
    #graficarNetwork(networkGeneral,"netluegoDeGo")
'''








