#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# @package Master
# @brief ----
# @details ----
# @authors Gustavo Irigoyen
# @authors Juan Pablo Sierra
# @authors Juan Eliel Ibarra
# @authors Gustavo Evovlockas
# @date Abril 2016
#

import rospy
import roslaunch
import LCS
from std_msgs.msg import String,Int32MultiArray, Float64MultiArray
import Const
import time
import LoadBehavior



from attributes import SensorFactory

# paquete donde se encuentran los archivo py
pkg = "learning_by_imitation"
 
# identidicador del tipo de tarea (se va a obtener desde v-rep o consola)
idTask = "TESTING"
# id de los nosdos que se van agregando
idNA = 0
# asocia idnumerico con nombres de comportamientos
dicComp = {0:'Init'} 

identify = -1
dictionary = {}
nodesLanzados = {}
nodes = {}#diccionario con clave id de node, cada nodo (idNA, start,end, behaviour, param)
links = []
linkEnEjecucion = []
# asocia id de node con comportamiento
dicNodeComp = {}
# asocia node con comportamiento
dicNodeParam = {}
auxDicNodeComp = {}
auxDicNodeParam = {}
# Comando actual
comand = ""
# usado para errores de ruido
errorRuido = 2000 
# tiempo que se acepta luego de terminado un comportamiento para indicar que se debe eliminar del grafo
tiempoBad = 10000
enablig = {}
ordering = {}
permanent = {}
fase="nada"
# el primer par de indices es el node anterior id,tiempo de fin el segundo es el node actual para evaluar los 10 segundos se recuerda el anterior
# esto se usa para el caso BAD
nodeEjecutando = ( (-1,-1) , (-1,-1) )
idCome = -1
# grafo generado tras varias demostraciones
grafoNuevo = []

# se lanzan nodes con el fin de learn
nodesToLearn = {}
# nodes lanzados an el proceso de ejecucion
nodesParaEjecutar = {}
current_milli_time = lambda: int(round(time.time() * 1000))  
diccSenAprender={}
nodesActives={}
nodesFinalized=[] 

################################
#APRENDER
################################

#solo se atiende si estamos en fase de aprendizaje
def atenderAprender(data):
    global fase  
    if fase == "learn" or fase=="here":
        callback(data)
  
def separarBloques(data):
        # print "callback: ",data
        strData = str(data)
        # rospy.loginfo("comportamiento datos recibidos"+str(data))
        return map(str, strData.split('|'))
    
def separarSensados(separar):
        sensados={}
        for s in  separar:
            if len(s)>1:
            	# rospy.loginfo(str(len(s))+"separar "+s)
            	datos = map(float, s.split('#'))
            	# print "sensado y datos ", s,datos
            	idSensor=int (datos[0])
            	del datos[0]
            	sensados[idSensor]=datos        
        return sensados  

# habria que mandar tolerancias
def compararParametros(data1,data2):
    #if Const.debugMaestro == 1:
        #print "comparamos parametros"
    # Recorremos cada clave en el diccionario
    for d in data1: # d tiene el Id de cada SENSOR
        #if Const.debugMaestro == 1:
            #print "Comparo ", data1[d], " con ", data2[d]
        sns = SensorFactory.get(d, data1[d]) # Obtenemos un sensor a partir de las lecturas en data1
        #if Const.debugMaestro == 1:
            #print "sns queda", sns
        if not sns.similar(data2[d]):   # Comparamos los datos de data1 con data2
            #if Const.debugMaestro == 1:
                #print "Encontramos datos dinstitos: ", data1[d], "vs", data2[d]
            return False
    #if Const.debugMaestro == 1:
        #print "SON IGUALES"
    return True







# se pueden pasar parametros como un array donde el primer elemento indica el tipo 
# de parametro y el segundo cantidad de valores los demas serian los daots, con un for se recorre etc
def callback(data):    
    separados=separarBloques(data.data)
    d=separados[0]
    #print "separados ",d    
    datos = d.split('#')
    del separados[0]
    param=separarSensados(separados)
    
    
    comportamiento=str(datos[0]) 
    postcondicion=int(datos[1])
    global nodesActives
    global nodesFinalized
              
    #print "valor postcondicion: ",postcondicion," comportamiento: ",comportamiento

    global nodes
    global idNA
    
    idActive=nodeActive(comportamiento,param)

    if postcondicion == 1:
        #node nuevo comportamiento recien activado
        if not dictionary.has_key(comportamiento):
            dictionary[comportamiento]=[]             
            
        #node ya activado y lo sigue estando
        
        if idActive!=-1:   
            #print "node comportamiento sigue active"
            #actualizar datos del nodeactive en ambas estructuras nodes y dicc
            updateParam(nodes[idActive], param)  
            if Const.debugMaestro == 1:
                print "update nodes: ",nodes
        #no hay node active se agrega uno nuevo
        else:
           
            #agregar node            
            nuevoNode=(idNA, current_milli_time(), -1, comportamiento, param)
            if Const.debugMaestro == 1:
                print "idNA en call ",idNA," largo ",len (nodes) ," ",nuevoNode
                print comportamiento,"node comportamiento nuevo ",nodes
            nodes[idNA]= nuevoNode
            #nodes.append(nuevoNode)
            dictionary[comportamiento].append(nuevoNode)   
            nodesActives[idNA]= nuevoNode
            
            idNA = idNA+ 1


    #comportamiento que estaba active y se apaga
    #elif nodeActive(comportamiento) != -1: 
    elif idActive!=-1:  
        #se saca de la lista de activos
        print ">>>ID ACTIVOS ",idActive 
        del nodesActives[idActive]      
        
        if Const.debugMaestro == 1:   
           print "finalizar node comportamiento",comportamiento 
           
        huboMerged=False        
        tiempoFinal=current_milli_time()
             
             
        #busca el nodo en los terminados los cuales estan ordenados por finalizacion
        #
        for n in range(len(nodesFinalized)-1,-1,-1):    
            if tiempoFinal-nodesFinalized[n][2]<errorRuido:
                if  nodesFinalized[n][3]==comportamiento and compararParametros(param,nodesFinalized[n][4]):
                    auxNode=list (nodes[nodesFinalized[n][0]])
                    auxNode[2]=tiempoFinal
                    nodes[nodesFinalized[n][0]]=tuple (auxNode)   
                    nodesFinalized.append(nodesFinalized[n][0])
                    del nodes[idActive]
                    del nodesFinalized [n] 
                    huboMerged=True
                    break
            else:
                break
                
        if not huboMerged:
            print "NODO ACTIVO",nodes[idActive]
            auxNode=list (nodes[idActive])
            auxNode[2]=tiempoFinal
            auxTupla=tuple (auxNode)  
            nodes[idActive]=auxTupla
            nodesFinalized.append(auxTupla)
            
            
            
            
            
            
            
            
            
            
        '''
            
        #verificar que el inicio del node actual esta a menos de 
        #errorRuidNAo del fin de otro node del mismo comportamiento 
        #en tal caso hacer un merge
        
        if Const.debugMaestro == 1:        
            print "tiempo final: ",tiempoFinal," ",comportamiento
        lista=dictionary[comportamiento]
        tamanio=len(lista)
        
        ultimo=list(lista[tamanio-1])
        #ultimo=list(id)        
        
        #hay mas de un node se verifica si hay que hacer merge
        if tamanio > 1:            
            anterior=list(lista[tamanio-2])
            #se verifica inicio del ultimo y fin del anterior y se saca el ultimo de diccionario y se
            #le asigna final al anterior, de los nodes se saca el de id ultimo
            if Const.debugMaestro == 1:            
                print ultimo[1]-anterior[2]
            if (ultimo[1]-anterior[2])<errorRuido and compararParametros(ultimo[4],anterior[4]):
                if Const.debugMaestro == 1: 
                    print "hay que merger ",comportamiento
                # FALTA hacer el merge teniento en cuenta los parametros 
                hayQueMerger=True                
                del lista[tamanio-1]
                del lista[tamanio-2]
                anterior[2]=tiempoFinal
                mergeado=tuple(anterior)
                updateParam(mergeado, param)
                lista.append(mergeado)
                dictionary[comportamiento]=lista
                #de la lista de nodes hay que borrar el node que se mergeo 
                #y acomodar el node anterior con su nuevo final
                del nodes[ultimo[0]] 
                nodes[anterior[0]]=mergeado
                #mergeNodes(ultimo[0], anterior[0],mergeado)  
                
                
                             
        #se asigna el final y se ajustan a nodes y diccionario        
        if not hayQueMerger:
            ultimo[2]=tiempoFinal
            del lista[tamanio-1]            
            finalizado=tuple(ultimo)
            lista.append(finalizado)
            dictionary[comportamiento]=lista
            nodes[ultimo[0]]=finalizado
            #cerrarNode(ultimo[0],finalizado)
            if Const.debugMaestro == 1: 
                print comportamiento, " cerrar directamente ", finalizado

        #print nodes  
        
        '''

 
#retorna el id del node active para un comportamiento 
#verifica si los parametros son similiares para un comportamiento   
#se busca en la lista de nodos activos
def nodeActive(comportamiento, param):
    #verificar si en la lista del comportamiento hay un node active
    global nodesActives
    
    for n in nodesActives:
        print "n",n
        if  nodesActives[n][3]==comportamiento and compararParametros(param,nodesActives[n][4]):
            return n
    return -1 



#El update solo se hace en la lista de nodes no en el diccionario de comportamientos usado 
#como auxiliar
def updateParam(node, paramNuevo):
    global nodes
    global auxDic
    nuevoNode=(node[0],node[1],node[2],node[3], paramNuevo)
    nodes[node[0]]=nuevoNode    
    nodesActives [node[0]]=nuevoNode
    

def offLine ():	
    
    global nodes
    global idNA
    global identify
    global links
    global auxDicNodeComp
    global auxDicNodeParam    
    
    global nodesActives
    print "estamos en ooffline" 
    #hay que cerrar los comportamientos cuando se cierre la demostracion
    #si no estaba prendido se ocupa el callback de ignorarlo
    tiempoFinal=current_milli_time()  
    for n in nodesActives  :   
        auxNode=list (nodes[n])
        auxNode[2]=tiempoFinal
        nodes[n]=tuple (auxNode)  
                
          
    #eliminar nodes de menos que errorRuido y a la vez lanzar los nodes del grafo

    
    
    auxNodes = {}     
    auxDicNodeComp = {}
    auxDicNodeParam = {}    
    
     
    
    idNodeAdd = LCS.getNewId()
    if Const.debugMaestro == 1:
        print "id node inicial ",idNodeAdd
    for n in nodes.values(): 	
        if n[2] - n[1] > errorRuido:   #el node es menor a un errorRuido
            auxl = list (n)
            auxl[0] = idNodeAdd
            auxNodes[idNodeAdd] = tuple(auxl)            
            idNodeAdd = idNodeAdd + 1
            if Const.debugMaestro == 1:
                print "valores de nodes a agregar ",n,n[2]-n[1]
    nodes =  auxNodes    
    # ultimo node es el Init
    idNA = idNodeAdd 

    '''
    for n in range(len(nodes)-1,-1,-1):
        auxNode=nodes[n]
	
        if auxNode[2]-auxNode[1]<errorRuido:   #el node es menor a un errorRuido
            del nodes[n]
            print "valores de nodes a borrar ",auxNode,auxNode[2]-auxNode[1] 
    '''    
            
    if Const.debugMaestro == 1:
        print "generando links"
    if Const.debugMaestro == 1:
        print "tamanio nodes ",len(nodes) 
    links = []
    for n1 in nodes.values()  :
        #carga los diccionarios
        if not  auxDicNodeComp.has_key(n1[0]):
            auxDicNodeComp[n1[0]]= n1[3] 

        if not  auxDicNodeParam.has_key(n1[0]):
            auxDicNodeParam[n1[0]]= n1[4]

        for n2 in nodes.values()  :
            if n1[0] != n2[0] and n1[1] < n2[1]:
                # Son nodes distintos y n2 comenzo despues de n1

                # De manera analoga al paper pongo las tareas como A y B
                iniA, finA, iniB, finB = n1[1], n1[2], n2[1], n2[2]
                tipoLink = -1
                if ( iniA + Const.EPSILON < iniB < finA - Const.EPSILON ) and ( iniA + Const.EPSILON < finB < finA + Const.EPSILON ):                    
                    # (B empieza durante A) y ademas (B termina antes que termine A o junto con A) => permanente
                    tipoLink = Const.LINK_PRM
                elif ( finA - Const.EPSILON <= iniB < finA + Const.EPSILON ) or ((iniA + Const.EPSILON < iniB < finA - Const.EPSILON) and (finA + Const.EPSILON < finB)) :
                    # (B empieza justo cuando termina A) o bien (B empieza durante A y termina despues que A) => habilitacion
                    tipoLink = Const.LINK_ENA 
                elif finA + Const.EPSILON < iniB: 
                    # B empieza despues que termino A => orden
                    tipoLink = Const.LINK_ORD
                if tipoLink != -1:  
                    #links.append((n1[0],n1[3] ,n2[0],n2[3] ,tipoLink))#id node 1 (2) comportamiento node 1 (2)
                    links.append((n1[0], n2[0], tipoLink))
                    if Const.debugMaestro == 1:
                        print "el node se agrego"
                    print "$> {0}, {1}, {2}, {3}, {4}, {5}, {6} >>> {7}".format(n1[0], iniA, finA, n2[0], iniB, finB, Const.EPSILON, tipoLink)
                else:
                    if Const.debugMaestro == 1:
                        print "el node no se agrego"
                    print "$> {0}, {1}, {2}, {3}, {4}, {5}, {6} >>> {7}".format(n1[0], iniA, finA, n2[0], iniB, finB, Const.EPSILON, tipoLink)
                tipoLink = -1
    if len (nodes) > 0:
        addInitNode(idNA)
        
    # print "links ",links
    if Const.debugMaestro == 1:
        for it in links:       
            print "links ",it[0]," ",it[1]," ",it[2]
        
#se desacopla de offline para poder usar el metodo anterior en el metodo go, ya 
#que ahi no se necesita este node Init 
#tal vez si se necesite ya que de habeer un solo node no hay links que agregar
def addInitNode(idInit):
    global links
    global nodes  
    global auxDicNodeComp
    global auxDicNodeParam  
    for n in nodes.values()  :
        links.append((n[0],idInit,Const.LINK_ORD))

    if not  auxDicNodeComp.has_key(idInit):
        auxDicNodeComp[idInit] = "Init"
    if not  auxDicNodeParam.has_key(idInit):
        auxDicNodeParam[idInit] = {}
    

    
    
    
    
    '''
    nodeActive=-1
    if dictionary.has_key(comportamiento):        
        listaActual=dictionary[comportamiento]
        tamanio=len (listaActual)    
        if tamanio>0 :
            ultimoNode=listaActual[tamanio-1]
            datos=list(ultimoNode)
            final=datos[2]
            #el node aun no esta cerrado
            if final== -1:
                nodeActive=datos[0]
    return nodeActive
    '''
    
    

'''
def cerrarNode(idCerrar,finalizado):
    global nodes
    for n in range(len(nodes)-1,-1,-1):
        if nodes[n][0]==idCerrar:
            nodes[n]=finalizado
            return

def mergeNodes(idEliminar,idModificar,nodeMergueado): 
    global nodes
    pasosRestantes=2
    for n in range(len(nodes)-1,-1,-1):
        if nodes[n][0]==idEliminar:
            del nodes[n]	    	
            pasosRestantes=pasosRestantes-1
            if pasosRestantes<=0:
                return	
        elif nodes[n][0]==idModificar:
            nodes[n]=nodeMergueado
            pasosRestantes=pasosRestantes-1	   
            if pasosRestantes<=0:
                return
'''



#solo se usa para crear la topologia a partir de una sola demostracion
def createTopology (enlaces):
    salida =[]
    aux={}#diccionario tendra todos los nodes y la cantidad de enlaces que tiene
    if Const.debugMaestro == 1:
        print "links crearTopo",enlaces
    for l in enlaces:
        # se agregan al diccionario todos los nodes
        if not aux.has_key(l[0]):
            aux[l[0]]=0
        # se agrega el node destino porque eventualmente podria ser el
        #node final y no aparece como inicio de links
        if not aux.has_key(l[1]):
            aux[l[1]]=0
        aux[l[0]]=aux[l[0]]+1
#lista=aux.items()

    auxOrd={}
    for n in aux:
        numSuc=aux[n]
        if not auxOrd.has_key(numSuc):
            auxOrd[numSuc]=[]
        auxOrd[numSuc].append(n)
     
    ordenado=[]
    for o in auxOrd:
        ordenado.append(auxOrd[o])

    for o in range (len(ordenado)-1,0,-1): 
        if Const.debugMaestro == 1:
            print "ordenado>",ordenado
        for p in ordenado[o]:
            for s in ordenado[o-1]:
                salida.append( (p,s) )

    return salida







                
############################ 
#Lanzar un node para
#execute o para learn
############################ 

def paramToString(param):
    salida=""
    for p in param:
        if len (salida)>0:
            salida=salida+'|'
        salida=salida+str(p)
        for d in param[p]:
            salida=salida+'#'+str(d)
    if Const.debugMaestro == 1:
        print "paramtostring", salida
    return salida 
                
def lanzarNode(idNode,idComportamiento): #es el id numerico del comportamiento 
    global dicComp
    global dicNodeParam
    #nombreComportamiento=dicComp [idComportamiento]
    nombreComportamiento=str(idComportamiento)
    if Const.debugMaestro == 1:
        print "se lanza el comportamiento:",nombreComportamiento    
    
    global pkg
    global dicNodeParam  
    execution =nombreComportamiento + '.py'
    # en los args se envian los id de los nodes y los parametros
    if idComportamiento == "Init":
        node = roslaunch.core.Node(pkg, execution, args=str(idNode) )
    else :
        sensado=paramToString(dicNodeParam)
        data= str(idNode)
        if len(sensado)>1 and idNode!=-1:
            if Const.debugMaestro == 1:
                print "diccionario node param ",dicNodeParam,idNode,dicNodeParam[int(idNode)]
            data=data + '|' + paramToString(dicNodeParam[int(idNode)])              
        node = roslaunch.core.Node(pkg, execution, args=str(data) )
        #node = roslaunch.core.Node(pkg, execution, env_args=[("identify",str(idNode)),("color","negro")] )    
    
    launch = roslaunch.scriptapi.ROSLaunch()
    launch.start()
    salida= launch.launch(node)
    time.sleep(1)
    return salida
    
############################ 
#EJECUTAR
############################ 

#No olvidar ajustar el nombre de pkg al del proyecto

def cargarDatos():
    if Const.debugMaestro == 1:
        print "cargar Datos mediante XML"

#se deberian recuperar la topologia de un XML
def recuperarTopologia():
    #global links
    #return createTopology(links)
    return LCS.getTopologiaGeneral()    


#se deberian recuperar los enlaces de un XML
def recuperarEnlaces():
    #global links
    return LCS.getNetworkGeneral()




######SI SE CREA EL NODO INIT SEPARADO DE AQUI NO HACE FALTA SER TAN CUIDADOSO	
#lanza los nodes y crea los enlaces  , NOTA hay que sacar al node Init en si como un nuevo node (no esta bueno que este embebido aca)
def createLinks(linksACrear):
    nodesLanzados=[] 
    global identify    
    global dicNodeComp
    for it in linksACrear:
        '''
        #hay que evitar lanzar el node Init y hay que obtener su id VERIFICAR AL SACAR INIT DE ACA        
        if(it[1]==0):
            identify=it[0]
            nodesLanzados.append(identify)
        if(it[3]==0):
            identify=it[2]
            nodesLanzados.append(identify)
        '''
        #se lanzan los nodes del enlace en caso de no haber sido lanzados
        if( not it[0] in nodesLanzados):
            nodesParaEjecutar[it[0]]=lanzarNode(it[0],dicNodeComp[it[0]])
            nodesLanzados.append(it[0])
        if( not it[1] in nodesLanzados):
            nodesParaEjecutar[it[1]]=lanzarNode(it[1],dicNodeComp[it[1]])
            nodesLanzados.append(it[1])
     
    #se envian los links a los nodes el sleep es para esperar que los nodes esten listos se puede hacer un waitmensaje
    time.sleep(1)
    for it in linksACrear:
        msg = Int32MultiArray()
        msg.data = [it[0], it[1], it[2]]#id node 1 y 2 y tipo de link	         
        rospy.loginfo(msg.data)
        pub.publish(msg) 


def executeBad():
    global nodeEjecutando 
    global tiempoBad
    global ordenes
    global fase
    global idTask
    if fase!="execute":
        print "ATENCION solo se puede hacer BAD cuando se este ejecutando"    
        return
    fase="bad"
    
    tiempoActual = current_milli_time()
    # si el node actual inicio hace menos de tiempoBad se borra el node anterior    
    tiempoDif = tiempoActual - nodeEjecutando[1][1]
    dentroDelTiempo = tiempoDif < tiempoBad
    existeNodeAnterior = nodeEjecutando[0][0] != -1
    
    # se elimina el node que esta en ejecucion,si se termino el ciclo
    #Init envia un su id se verifica si es el Init entonces se borra siempre el anterior a init
    nodeABorrar = nodeEjecutando[1][0]
    if LCS.getCompDeNode(nodeABorrar)=="Init":
        nodeABorrar=-1
    
    #si esta en Init o existe el anterior y estoy en el tiempo se borra el anterior        
    if ( nodeABorrar==-1)  or ( existeNodeAnterior and dentroDelTiempo):
        nodeABorrar = nodeEjecutando[0][0]
        nodeEjecutando = (-1, nodeEjecutando[1])
    
    elif nodeABorrar == nodeEjecutando[1][0] and nodeABorrar <> -1:
        
        nodeEjecutando = nodeEjecutando = (nodeEjecutando[0], -1)         
        #odoEjecutando[0] = nodeEjecutando[1]

    if nodeABorrar==-1:
        return
    if Const.debugMaestro == 1:
        print "nodeEjecutando ",nodeEjecutando  
        
    #el LCS verifica si se puede borrar el node     
    #no se borra si solo queda un node y el Init ni si el node ya fue borrado
    #tener en cuenta que el ejecutando anterior al Init es uno y si ya se borro
    #no se puede volver a borrar
    borrar=LCS.borrarNodeBad(idTask,nodeABorrar)        
    LCS.graficar("bad")   
    

  
    #se publica estado a Bad capaz el nombre habria que cambiarlo,
    if borrar:  
        msg = Int32MultiArray()
        msg.data = [0,nodeABorrar] 
        ordenes.publish(msg)


    fase="execute"

        

    
def atenderNodeEjecutando(data):
    global nodeEjecutando
    # llega un nuevo node ejecutando
    if  data.data[0] != nodeEjecutando[1][0]: 
        # acomodo los datos del que era ultimo pasa a ser el anterior        
        anterior=nodeEjecutando[1]
        
        # Para el caso de un BAD que haya eliminado el node en ejecucion nos deja
        # el par (comportamientoAnterior, comportamientoActual= ( _ , -1)
        # La idea es no perder ese comportamientoAnterior, evitando reemplazarlo por -1
        if anterior == -1:
            anterior = nodeEjecutando[0]
            
        # agrero el nuevo node ejecutando con su tiempo de inicio
        a=data.data[0]
        b=current_milli_time()
        actual=(a,b)
        nodeEjecutando=(anterior,actual)

#verificar como se agrega un tramo entre el ultimo node y el Init si hay lios con el BAD

#come debe guardar el id del node actual luego en execute go se usara este valor para partir el grafo y agregar lo que se obtuvo en here
#se debe evitar que el robot siga en modo ejecucion y pase a un estado parecido a learn pero que solo se mueva es decir no envie senales       
def executeCome ():
    #se establece a partir del node actual el corte y se agrega lo aprendido justo antes de este node
    global idCome
    global estado
    global dictionary
    global nodes
    global fase
    global idNA
    global diccSenAprende
    global nodesActives
    global nodesFinalized

    if fase!="execute":
        print "ATENCION solo se puede hacer COME cuando se este ejecutando"    
        return
    if Const.debugMaestro == 1:
        print "nodeEjecutando ",nodeEjecutando
    idCome=nodeEjecutando[1][0]
    if idCome==-1: 
        print "ATENCION no se puede agregar nodes"  
        return    

    msg = Int32MultiArray()
    msg.data = [3,3] #estado para agregar comportamientos
    estado.publish(msg)

    dictionary={}
    #diccSenAprender={}
    nodes = {}
    nodesActives={}
    nodesFinalized=[] 
    idNA=0
    fase="come"

#a partir de aqui se debe pasar a una etapa de aprendizaje el link obtenido se debe guardar, recordar que para learn se lanzan nuevos nodes
#por lo cual el estado de los nodes no se modifica 
def executeHere():    
    global estado
    global fase
    global nodesToLearn
    
    if fase!="come":
        print "ATENCION solo se puede hacer HERE luego de COME"
        return

    nodesToLearn = {}
    for n in dicComp:
        if n!="Init":#lanza nodes sin ser el Init
            nodesToLearn[n]= lanzarNode(-1,n) 
    fase="here"	   

    msg.data = [1,1]#podria ser el segundo valor el id del comportamiento
    estado.publish(msg)
    if Const.debugMaestro == 1:
        print "ejecuto here"
    
    
#se realiza la particion del grafo se agrega los link obtenidos en here  se pasa a modo ejecucion nuevamente y se continua la ejecucion
def executeGo():  
    
    if Const.debugMaestro == 1:
        print "entro en go"    
    global fase
    global estado
    global idCome
    global nodesToLearn
    global auxDicNodeParam
    global auxDicNodeComp 
    global idTask
    
    if fase=="come":
        msg.data = [2,2] 
        estado.publish(msg)  
        fase="execute"
        print "ATENCION no hay nada nuevo aprendido"
        return
    
    if fase!="here":
        print "ATENCION solo se puede hacer GO luego de HERE" 
        return
    #se obtiene el grafo generado en la mini demostracion
    global links
    #se corta el grafo general 

    msg.data = [0,1]#debe avisar antes de hacer offline que se cierra asi no quedan mensajes colgados 
    estado.publish(msg)
    for it in nodesToLearn.values():
        print it.stop()	
    if Const.debugMaestro == 1:
        print "antes de offline en GO"   
    offLine()         
    
    #cortarGo(links,grafoGeneral,idCome)     
    #se vuelve al estado ejecucion

    msg.data = [2,2] 
    estado.publish(msg)  
    
  
    # addInitNode()#agrega el node Init al final de link y agrega enlaces de orden
    # aca se podria agregar el comportamiento del capitulo 5
    if len (links) > 0:        
        if Const.debugMaestro == 1:
            print "nodes nuevos en go",nodes
        grafoNuevo= createTopology(links)
        LCS.setDicParametros(auxDicNodeParam)
        LCS.appendDicCom(auxDicNodeComp)
        LCS.graficarTopologia(grafoNuevo,"NuevaDemo")
        nodeIdEjec = -1
        if nodeEjecutando[0] <> -1:
            nodeIdEjec = nodeEjecutando[0][0]
            
        LCS.cortarGoCaminos(idTask,grafoNuevo,links,idCome,nodeIdEjec)
        LCS.graficar("ComeGo")         
    else:
        print "ATENCION: La demostracion no genero nodes"    
    
    if Const.debugMaestro == 1:
        print "nodeEjecutando ",nodeEjecutando," idCome ",idCome

    fase="execute"
    
    
  
     
def buscarComportamiento(idNode,linksBuscar): 
    for b in linksBuscar:
        if b[0]==idNode:
            return (b[0],b[1])
        if b[2]==idNode:
            return (b[2],b[3])
    return  (-1,-1)   
    
#######################
#creacion de caminos
#######################
    
def sucesoresTopologicos (topologia):
    salida={}
    #dada una topologia el diccionario guarda como clave el id del node
    #y como valores una lista de los sucesores
    for t in topologia:
        if not salida.has_key(t[0]):
            salida[t[0]]=[]
        salida[t[0]].append(t[1])
    return salida

    
#Tal vez se podria primero ver los que no tienen predecesores y lanzar esos por temas de eficiencia
#aca se recorren todos los nodes y se hace el algoritmo
def pathPrev( sucesoresTopologicos):
    #los nodes son un dicc, cada node tene una lista de path y cada path es una lista de nodes
    salida ={}
    for node in sucesoresTopologicos:#para cada node 
        if Const.debugMaestro == 1:
            print "Node ",node
        if not salida.has_key(node):    
            salida[node]=[]
        salida = recursionEnvioPath(node, [], salida, sucesoresTopologicos)   
    return salida    
    
#se recibe un path, se verifica si hay un path que coincida hasta el final
#en tal caso se sobreescribe el path mas corto que habia, la idea es que algun otro node se agrego al path..
#luego el nuevo path se envia a los nodes sucesores de forma recursiva
def recursionEnvioPath(node, pathAdd, caminos, sucesoresTopologicos):
    path=list(pathAdd)
    path.append(node)
    if node in sucesoresTopologicos:
        for sucesor in sucesoresTopologicos[node]:
            if not caminos.has_key(sucesor):    
                caminos[sucesor]=[]
                
            #se verifica si el nuevo path no es igual que el que habia en tal caso se lo pisa si es mas largo el nuevo
            accion=2 # 0 no se hace nada,1 se alarga el path ,2 se agrega un nuevo path
            for cs in range (len (caminos[sucesor])):
                pathMasLargo=compararPath (path,caminos[sucesor][cs])
                if pathMasLargo != None:   
                    if len (path)==len(pathMasLargo):#el nuevo path resulta ser el mas largo
                        accion=1 
                    else:
                        accion=0   
                    #print "entro execute()en path mas largo sucesor",sucesor," CML ", caminos[sucesor][cs],">>", caminos 
                    caminos[sucesor][cs]=pathMasLargo                    
                    
            if accion==2:
                if Const.debugMaestro == 1:
                    print "nuevoPAth ", path
                caminos[sucesor].append(path)  
            if accion >0:   
                if Const.debugMaestro == 1:
                    print caminos
                caminos = recursionEnvioPath(sucesor,path, caminos,sucesoresTopologicos)  
    return caminos

#devuelve el path mas largo si coinciden y none en caso de que no tengan nada en comun 
def compararPath (pathNuevo,pathAntiguo):
    #por si alguno es nulo
    if pathAntiguo == None or pathNuevo==None:
        return None    
    
    #se establece el path mas largo
    dif= len(pathNuevo) - len(pathAntiguo)
    pathMasLargo=pathNuevo

    pathMasCorto=pathAntiguo
    if dif<0:
         dif=-dif
         pathMasLargo=pathAntiguo
         pathMasCorto=pathNuevo        
        
    #recorriendo de fin a inicio si no coinciden los path se retorna None
    for i in range(len(pathMasCorto)-1,-1,-1):
        if pathMasLargo[i+dif] != pathMasCorto[i]:
            #print pathMasLargo[i+dif] , pathMasCorto[i]
            return None
    return pathMasLargo #devuelve el path mas largo
    
def sendPath(caminos): 
    if Const.debugMaestro == 1:
        print "Enviando caminos"
    msg = Int32MultiArray() 
    global pubCaminos  
    #print caminos
    for node in caminos:
        if Const.debugMaestro == 1:
            print node
        salida = [node]
        for lc in range (len (caminos[node]) ): 
           # for c in range (len (caminos[node][lc]) ): 
            #print caminos[node][lc], lc
            salida = salida + caminos[node][lc] + [-10]#donde -10 es un separador              
        #se manda mensaje aunque este vacia por si hay que inicializar 
        msg.data = salida
        # print salida  
        pubCaminos.publish(msg)    
        

 
#######################
#Metodo Principal
#######################     
    
def endDemo():
    global nodesToLearn
    global nodesParaEjecutar
    global fase
    global estado
    global idTask
    global auxDicNodeParam
    global auxDicNodeComp   

    
    if fase != "learn":
        print "ATENCION: no se inicio aprendizaje"
        return


    for it in nodesParaEjecutar.values():
        print it.stop()	
        
    print "estamos en endDemo", nodesToLearn 
      
    for it in nodesToLearn.values():
        print it.stop()    
    print "estamos en endDemo 1"   
    fase="nada"
    msg = Int32MultiArray() 
    msg.data = [0,1]#debe avisar antes de hacer offline que se cierra asi no quedan mensajes colgados 
    estado.publish(msg)
    print "estamos en endDemo 2" 
    offLine()
    # addInitNode()#agrega el node Init al final de link y agrega enlaces de orden
    # aca se podria agregar el comportamiento del capitulo 5
    if len (links) > 0:
        topologia=createTopology(links)
        LCS.setDicParametros(auxDicNodeParam)
        LCS.appendDicCom(auxDicNodeComp)
        LCS.nuevaDemostracion(topologia , links, idTask) 
        print "",
    else:
        print "ATENCION: La demostracion no genero nodes"    
          
def learn():
    global nodesToLearn
    global nodesParaEjecutar
    global fase
    global estado
    global dicComp
    global nodes
    global dictionary
    global idNA
    global diccSenAprender
    global nodesActives
    global nodesFinalized
    #if  fase=="learn":
    #   return    
    
    #mata los nodes que hubiera actives
    for it in nodesToLearn.values():
        print it.stop()	
    for it in nodesParaEjecutar.values():
        print it.stop()	
        	
    #hay que lanzar comportamientos para que reciban las postcondiciones a la hora de learn NO OLVIDAR MATARLOS AL TERMNAR APRENDER 
    
    nodesToLearn = {}
    for n in dicComp:
        if n!="Init":#lanza nodes sin ser el Init
            nodesToLearn[n] = lanzarNode(-1,n) 

    fase="learn"	
    diccSenAprender={}    
    dictionary = {}
    nodes = {}
    nodesActives={}
    nodesFinalized=[] 
    idNA = 0
    msg.data = [1,1] # podria ser el segundo valor el id del AbstractBehavior
    estado.publish(msg)

#Falta pasarle el id de la tarea a cargar
def execute():
    global nodesToLearn
    global nodesParaEjecutar
    global fase
    global estado
    global dicComp
    global nodes
    global dictionary
    global dicNodeComp
    global dicNodeParam
    global idTask
    global nodeEjecutando


    
    nodeEjecutando = ( (-1,-1) , (-1,-1) )
    
    #mata los nodes que hubiera actives
    for it in nodesToLearn.values():
        print it.stop()	
    for it in nodesParaEjecutar.values():
        print it.stop()	    
        
    fase="execute"    
       	    
    #aca se podria cargar la lista de nodes a execute por ahora uso los definidos en el metodo
    
    #links=[(0,1,1,2,0),(0,1,2,0,0),(1,2,2,0,0)]	
    #grafoGeneral=[(0,1,1,2,0),(0,1,2,0,0),(1,2,2,0,0)] #para no complicarla mucho uso como general este link cortito
    #linkEnEjecucion=[(0,1,1,2,0),(0,1,2,0,0),(1,2,2,0,0)]
    #linkEnEjecucion=[(0,1,1,2,0),(0,1,2,1,0),(0,1,3,0,0),(1,2,3,0,0),(2,1,3,0,0),(1,1,2,1,0)]
    LCS.cargarEstructuras(idTask) #se le deberia pasar id de la tarea a cargar
    dicNodeComp = LCS.getDicComportamientos()
    dicNodeParam = LCS.getDicParametros()
    LCS.graficar("Ejecutar")
    if Const.debugMaestro == 1:
        print "dicc node param ", dicNodeParam
    if len (dicNodeParam) == 0:
        print "No hay nada para execute", dicNodeComp
        return

    #enlaces=[(0,1,1,2,2),(0,1,2,0,0),(1,2,2,0,0)]	     

    enlaces = recuperarEnlaces()
    createLinks(enlaces)
    time.sleep(1)    	  
    
    #topologia=[(0,1),(0,2),(1,3),(2,3)]
    #topologia=[(0,1),(1,2)]

    topologia = recuperarTopologia()
    sucesoresTop = sucesoresTopologicos (topologia)
    if Const.debugMaestro == 1:
        print "sucesores: ",sucesoresTop
    caminitos = pathPrev(sucesoresTop)    
    sendPath(caminitos)     
    
    # se deberia esperar a que los comportamientos se activen sino no reciben el mensaje de estado
    # se podria esperar un mensaje es decir por medio de wait
    time.sleep(1)    
    msg.data = [2,2] 
    estado.publish(msg)
    #arranqueNivel()

#event = threading.Event()
 
 
def endExecute():
    global estado
    global fase 
    fase="nada"
    msg.data = [0,0] # podria ser el segundo valor el id del AbstractBehavior
    estado.publish(msg)    
 

def atenderComandos(data):
    global comand
    global idTask
    if Const.debugMaestro == 1:
        print "recibo comand",data.data,str(Const.COMMAND_INIT_LEARNING)
    #event.signal()
    aux = data.data.split('|')
    if aux[0] ==str(Const.COMMAND_INIT_LEARNING):
        comand="learn"
    elif aux[0] == str(Const.COMMAND_END_LEARNING):
        comand="endDemo"
        idTask = aux[1]
    elif aux[0] == str(Const.COMMAND_PLAY):
        comand="execute" 
        idTask = aux[1]
    elif aux[0] == str(Const.COMMAND_STOP):
        comand="endExecute"
    elif aux[0] == str(Const.COMMAND_BAD):
        comand="bad"            
    elif aux[0] == str(Const.COMMAND_GO):
        comand="go"    
    elif aux[0] == str(Const.COMMAND_COME):
        comand="come"            
    elif aux[0] == str(Const.COMMAND_HERE):
        comand="here"            
    elif aux[0] == str(Const.COMMAND_EXIT):
        comand="salir"            

def finalize():
    finalizeTopic.publish("END")
    rospy.signal_shutdown("Bye!")

def shutdown():
    print "Bye!"

if __name__ == '__main__':    
    
    
    #links=[(2, 3, 1), (2, 4, 1), (2, 5, 1), (2, 6, 0), (3, 6, 0), (4, 6, 0), (5, 6, 0)]

    
    #print "topologia crear ",createTopology(links)
    
    

    print "iniciando Master"

    rospy.init_node('Master', anonymous=True)
    rospy.on_shutdown(shutdown)
    
    id = 0
    dicComp = LoadBehavior.load_abstract_behavior()
    dicComp.append('Init')
    if not 'GoTo' in dicComp:
        dicComp.append('GoTo')
    print "diccionario AbstractBehavior ",dicComp
    rospy.Subscriber("topic_command", String, atenderComandos)
    ordenes = rospy.Publisher('topic_orders', Int32MultiArray, queue_size = 10)    
    pub = rospy.Publisher('topic_preConSetting', Int32MultiArray, queue_size = 10)
    estado = rospy.Publisher('topic_state', Int32MultiArray, queue_size = 10)    
    nivel = rospy.Publisher('topic_level', Int32MultiArray, queue_size=10)
    rospy.Subscriber("topic_postCondDetected", String, atenderAprender)    
    motores = rospy.Publisher('topic_operateEngine', Float64MultiArray, queue_size=10)
    pubCaminos = rospy.Publisher('topic_path', Int32MultiArray, queue_size=100)
    finalizeTopic = rospy.Publisher('topic_finalize', String, queue_size=10)
    #rospy.Ssignal.signal(signal.SIGINT, handler)ubscriber("topic_path", Int32MultiArray, atenderCaminos)   
    rospy.Subscriber("topic_runningNode", Int32MultiArray, atenderNodeEjecutando)    
    #rospy.Subscriber("topic_preConSetting", Int32MultiArray, setting)	 
    #rospy.Subscriber("topic_preConDetection", Int32MultiArray, evaluarPrecondicion)    
    
    #event.wait()
    msg = Int32MultiArray()
    msg.data = [0,1]
    estado.publish(msg)
    
    #comand=raw_input("> ") 
    comand = ""
    
    while comand != "salir":
        comand = ""
        while comand == "":
            time.sleep(1)
        print "comand ", comand
        if comand == "endDemo":
            endDemo()         
        elif comand == "learn":
            learn()
	elif comand == "execute":
	    execute()
	elif comand == "endExecute":
	    endExecute()   
     
     
	elif comand == "bad":    
	    #posiblemente se realice el algoritmo en vez de 
	    #sobre linkEnEjecucion sobre el grafo general	    
	    aux = executeBad()
	    if Const.debugMaestro == 1:
             print  aux	    
	elif comand == "come":    
	    aux = executeCome()
	    if Const.debugMaestro == 1:
             print  aux
	elif comand == "here":
	    aux = executeHere()
	    if Const.debugMaestro == 1:
             print  aux
	elif comand == "go": 
	    if Const.debugMaestro == 1:
             print "antes de go"
	    aux = executeGo()	    
	    if Const.debugMaestro == 1:
             print  aux	    
	elif comand == "probarGo": 
	    grafoGeneral = [(1,1,3,3,0),(2,2,3,3,0),(3,3,4,4,0),(3,3,5,5,0)]
	    nuevolinks = [(0,6,1,0,0)]
	    #cortarGo(nuevolinks,grafoGeneral,3)	    
	#elif comand == "sc": 
	   # print separarCaminos()
	elif comand == "topo":
         linkEnEjecucion = [(0,1,0),(0,2,0),(0,3,0),(1,2,0),(1,3,0),(2,3,0)]
         aux = createTopology(linkEnEjecucion)
         if Const.debugMaestro == 1:
             print aux
	elif comand == "lcs":
            LCS.probarLCS()
	elif comand == "lcsPapper":
            LCS.probarLCSPapper()
	elif comand == "pp":   
	    pathAntiguo = [2,3,4]
	    pathNuevo = [3,4]
	    if Const.debugMaestro == 1:
             print "compararPath> ",compararPath (pathNuevo,pathAntiguo)	    
	    topologia = [(2,4),(1,3),(3,4),(1,2),(4,6),(5,1),(7,1),(4,8)]
            #topologia=[(1,2)]
            sucesoresTopologicos = sucesoresTopologicos (topologia)
            if Const.debugMaestro == 1:
                print "sucesores: ",sucesoresTopologicos
            caminitos = pathPrev(sucesoresTopologicos)    
	    sendPath(caminitos)	    
	#se puede dar bad cuando se ejecuta 
	elif comand == "algoritmoBad":  
	    linksBad = [(1,1,3,3,0),(2,2,3,3,0),(3,3,4,4,0),(3,3,5,5,0),(5,5,6,6,2)]	
	    #salida = borrarNodeBad(linksBad,3)
	    salida = executeBad(linksBad)
	    if Const.debugMaestro == 1:
             print salida
	    #msg.data = [0,0] 
	    #estado.publish(msg)
	else:
         msg.data = [0,1]
         estado.publish(msg)
        #entrada=raw_input("> ")
    finalize()
    rospy.spin() 

'''

#######################
#NODO INIT (SACAR DE AQUI)
#######################


def evaluation(l):
    result = True
    for it in l:
        result = result and it
        if not result:
            break
    return result



def setting(data):
   global identify
   #print "entro en setting Init ",data.data[1]," id Init ",identify
    
   # data.data[0] = fromCompID, data.data[1] = toCompID, data.data[2] = linkType. linkType puede ser permantente(0), de orden(1) o de habilitacion(2)
   if data.data[1] == identify:
        print "es mi id"
        if data.data[2] == 2:
            permanent[data.data[0]] = False
            print "permanente ", len(permanent)
        elif data.data[2] == 1:
            print "habilitacion "
            enablig[data.data[0]] = False
        elif data.data[2] == 0:
            print "orden "
            ordering[data.data[0]] = False 

def evaluarPrecondicion(data):#invocado en etapa de ejecucion cuando llega una postcondicion    
    skip = False
    comportamiento=data.data[0] 
    postcondicion=data.data[1]

    if permanent.has_key(comportamiento):
        permanent[comportamiento] = postcondicion == 1
        if permanent[comportamiento]:
            print "es permanente"
        else:
            print "salio de permanente"
    elif enablig.has_key(comportamiento):
        enablig[comportamiento] = postcondicion == 1
        if enablig[comportamiento] or ejecutando:#si se esta ejecutando no importa que se apague
            print "esta habilitado"	
        else:
            print "se inhabilito"
    elif ordering.has_key(comportamiento):
        ordering[comportamiento] = ordering[comportamiento] or (postcondicion == 1)
       # print "es de orden"
    else:
        skip = True
        
    #print "node llego postcondicion de tipo orden", ordering

    #se detecta cumplimiento de una postcondicio...entonces el Init manda su nivel de activacion para
    #atras...si un node recibe y puede execute ejecuta, si no puede manda
    #su nivel para atras y pone su nivel en 0 
    arranqueNivel()
 

def arranqueNivel():
  # print "nivel de activacion Init"
    global nivel
    msg = Int32MultiArray()
        
    fin=True
    #para todos los nodes envia el valor para que se inicie el nivel
    for o in ordering:
        msg.data = [identify, -1]#manda para atras el nivel inicial
        nivel.publish(msg)        
    
    for o in ordering:
        #en caso que la relacion de orden aun no se cumplio
        if not ordering[o]:
            msg.data = [identify, o]#manda para atras el nivel
            nivel.publish(msg)
            fin=False
    #if fin:
        #rospy.loginfo("termino el ciclo")
            
##lo siguiente de bad ya no iria

#se elimina un node de la lista habria que verificar si pasaron menos de tiempoBad desde que inicio el AbstractBehavior actual y existe anterior
#en tal caso se elimina el node anterior si pasaron mas de tiempoEsperaBad segundos se asume que se quiere borrar el node actual Verificar
def BACKexecuteBad(linksAModificar):
    global nodeEjecutando 
    global tiempoBad
    tiempoActual=current_milli_time()
    #si el node actual inicio hace menos de tiempoBad se borra el node anterior    
    tiempoDif= tiempoActual - nodeEjecutando[1]
    dentroDElTiempo=tiempoDif<tiempoBad
    existeNodeAnterior=nodeEjecutando[0] >=0
    
    if existeNodeAnterior and dentroDElTiempo:
        borrarNodeBad(linksAModificar,nodeEjecutando[0])               
    
    #se elimina el node que esta en ejecucion, notar que si es el ultimo node tambien funciona porque al no haber
    #AbstractBehavior posteriores el valor de ejecutando queda seteado en el ultimo node, es decir solo se modifica si un
    #nuevo node ejecuta, en caso de dejar de execute no se notifica
    else :
        borrarNodeBad(linksAModificar,nodeEjecutando[2])
        
    return linksAModificar                 
            
            
            
            
    
#Nota los links no tienen un orden en la lista, el node Init no se debe borrar (controlar en el q llama a este metodo)
def borrarNodeBad(linksBad,idBad):      
    #creo la lista de destinos del node a borrar
    listaDestino=[]
    print "linkbad",linksBad
    for d in range(len(linksBad)):
        if (linksBad[d][0]==idBad):
            #se agregan los id y AbstractBehavior a listaDestino 
            listaDestino.append((linksBad[d][2],linksBad[d][3]))    
                    
    print "destinos del node borrado",listaDestino
            
    # de los que son origen del node a borrar agrega los destinos del node a borrar
    for l in range(len(linksBad)):
        if (linksBad[l][2]==idBad):#idborrar es destino del links
            for d in range(len(listaDestino)):    
                # se agregan links de orden entre los origens de los nodes y los destinos del node borrado 
                linksBad.append((linksBad[l][0],linksBad[l][1],listaDestino[d][0],listaDestino[d][1],0))
    
    print "linkbad",linksBad
    
    # se eliminana todos los links que tengan a idborrar como origen o destino
    for b in range(len(linksBad)-1,-1,-1):
        if (linksBad[b][0]==idBad or linksBad[b][2]==idBad):
            del linksBad[b]
    return linksBad          
     
'''       

'''
sinSucesores=[]
sinPredecesores=[]
#agrego todos los id de los nodes a las listas sin..
for l in nuevolinks:    
    grafoGeneral.append(l)
    if not l[0] in sinSucesores:
        sinSucesores.append(l[0])
        sinPredecesores.append(l[0])
    if not l[2] in sinSucesores:
        sinSucesores.append(l[2])
        sinPredecesores.append(l[2])
print   "grafoGeneral",grafoGeneral         
print   "nuevos ",nuevolinks   

#se sacn los que tienen sucesor y predecesor respectivamente, los que queden en las listas seran final e inicio respectivamente
for l in nuevolinks:
    if (l[0] in sinSucesores):
        sinSucesores.remove(l[0]) 
    if (l[2] in sinPredecesores):
        sinPredecesores.remove(l[2]) 
 
print "sinPredecesores",sinPredecesores
print "sinSucesores",sinSucesores
 
inicio=buscarComportamiento(sinPredecesores[0],nuevolinks)
fin=buscarComportamiento(sinSucesores[0],nuevolinks)
 

#de los nodes previos al objetivo, agregar links con destino al node inicial del nuevo link
#hay que borrar los enlaces que tienen como destino el node objetivo

#se agregan los enlaces de los nodes previo al node inicial del nuevo link
for i in range(len(grafoGeneral)):
    if grafoGeneral[i][2]==idCome:
        aux=grafoGeneral[i]
        grafoGeneral.append((aux[0],aux[1],inicio[0],inicio[1],0))    


#se borran los enlaces con destino a objetivo
for i in range(len(grafoGeneral)-1,-1,-1):
    if grafoGeneral[i][2]==idCome:
        del grafoGeneral[i]



#del node final del nuevo link agregar enlace al node objetivo 
objetivo=buscarComportamiento(idCome,grafoGeneral)  
grafoGeneral.append((fin[0],fin[1],objetivo[0],objetivo[1],0))
''' 



'''  
#lo que sigue de go no iria       

def cortarGo(nuevolinks,grafoGeneral,idCome): 
    if len(nuevolinks) == 0:
        print "link de tama;o cero en cortar"
        return grafoGeneral

    #se van a dar id repetidos
    #se halla el maximo id del general, y se suma a los id del links nuevo
    idMAximoGeneral=-1
    for l in grafoGeneral:
        if idMAximoGeneral<l[0]:
            idMAximoGeneral=l[0]
        if idMAximoGeneral<l[2]:
            idMAximoGeneral=l[2]      
    idMAximoGeneral=idMAximoGeneral+1
    print "idMAximoGeneral", idMAximoGeneral
    for i in range(len(nuevolinks)):
        aux=nuevolinks[i]
        #a cada node se le suma en su id el idMAximoGeneral
        modificado=(aux[0]+idMAximoGeneral,aux[1],aux[2]+idMAximoGeneral,aux[3],aux[4])
        nuevolinks[i]=modificado
                
    print "nuevolinks ",nuevolinks  
    

    
    # diccionarios con clave el id del node y valor el id del AbstractBehavior
    predecesores = {}
    sucesores = {}
    nuevos = {}     
    
    for g in grafoGeneral:  
        if g[2] == idCome and not (predecesores.has_key(g[0])):
            predecesores[g[0]] = g[1]
        if g[0] == idCome:
            #se agrega el node come como un sucesor
            if not (sucesores.has_key(g[0])):
                sucesores[g[0]] = g[1]   
            #se agrega el sucesor si no estaba en la lista        
            if not (sucesores.has_key(g[2])): 
                sucesores[g[2]] = g[3]            
            
    for n in nuevolinks:       
        #se agregan nodes nuevos a una lista
        if not (nuevos.has_key(n[0])): 
            nuevos[n[0]] = n[1]
        if not (nuevos.has_key(n[2])) and n[3] != 0:#no se agrega el Init
            nuevos[n[2]] = n[3]  
      
    print "nuevos ",nuevos
    print "predecesores  ",predecesores
    print "sucesores ",sucesores 
            
    for n in nuevos:
        for p in predecesores:
            print p,n
            grafoGeneral.append((p,predecesores[p],n,nuevos[n],Const.LINK_ORD))
        for s in sucesores:
            grafoGeneral.append((n,nuevos[n],s,sucesores[s],Const.LINK_ORD)) 
    
    
    print "grafo general al terminar cortargo", grafoGeneral
    
    return grafoGeneral
'''   



'''
def atenderCaminos(data):
    #global pathPosibles
    #si es mi id agrego la lismsg)

def ta de caminos camino el node
    #if data.data[0] == identify:
    if True: 
        #elimina de la lista el dato del id
        lista=list(data.data)        
        #print lista
        del lista[0]
        
        print separarCaminos(lista)
        #pathPosibles[data.data[1]]=lista
        #print lista

def separarCaminos(caminos):
    salida = []
    #caminos = [1,2,3,-10,4,5,6,-10,7,8,9,-10]
    inicio=0
    fin=0
    while inicio< len (caminos):    
        fin=caminos.index(-10,inicio)
        #print fin
        tramo=caminos[inicio:fin]
        #print tramo
        salida.append(tramo) 
        inicio=fin+1
    
    return salida
 
'''

'''
def merggearNuevaDemo(idTask):
    global links
    LCS.nuevaDemostracion( createTopology(links),links,idTask )
    





def createTopology (enlaces):
    salida =[]
    aux={}#diccionario tendra todos los nodes y la cantidad de enlaces que tiene
    print "links cretto",enlaces
    for l in enlaces:
        # se agregan al diccionario todos los nodes
        if not aux.has_key(l[0]):
            aux[l[0]]=0
        # se agrega el node destino porque eventualmente podria ser el node final y no aparece como inicio de links
        if not aux.has_key(l[1]):
            aux[l[1]]=0
        aux[l[0]]=aux[l[0]]+1
    lista=aux.items()

    # ordena por largo del camino
    ordenado=sorted(lista,key=lambda tup:tup[1])  
    for i in range(len(ordenado)-1):
        salida.append((ordenado[i+1][0],ordenado[i][0]))
    print "links cretto",enlaces," salida ",salida
    return salida
   
    
'''