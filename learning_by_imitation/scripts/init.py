#!/usr/bin/env python
import sys
import time
import rospy
import roslaunch
from std_msgs.msg import String, Int32MultiArray

id = 0
dicComp={0:'init',1:'localizar', 2:'avanzar'} #asocia idnumerico con nombres de comportamientos
identify=-1
Diccionario={}
nodosLanzados={}
nodos = []
links = []
errorRuido=2000#usado para errores de ruido
epsilon=2000#usado para determinar tipos de links puede pasar que se cierre un comportamiento luego de cerrar otro
tiempoEsperaBad=5000 #tiempo que se acepta luego de terminado un comportamiento para indicar que se debe eliminar del grafo
enablig = {}
ordering = {}
permanent = {}
fase="aprender"

current_milli_time = lambda: int(round(time.time() * 1000))  

def offLine ():
	
    #hay que cerrar los comportamientos cuando se cierre la demostracion
    #si no estaba prendido se ocupa el callback de ignorarlo
    msg = Int32MultiArray()
    for comp in Diccionario  :
	msg.data = [comp,0]
	callback (msg)	  
    
    #eliminar nodos de menos que errorRuido y a la vez lanzar los nodos del grafo
    global nodos
    global id
    global identify
    global links
    identify=id #ultimo nodo es el init
    for n in range(len(nodos)-1,-1,-1):
	auxNodo=nodos[n]
	
        if auxNodo[2]-auxNodo[1]>errorRuido:   #el nodo es mayor a un errorRuido
	   # lanzarNodo(auxNodo[0],auxNodo[3]) #se lanzan nodos de un comportamiento se manda el id del nodo a lanzar como segundo parametro
#           auxNodo[3] representa el id del comportamiento no el id que tiene el nodo
            print "lanzando nuevo nodo"
	else: 
            del nodos[n]
	    print "valores de nodos a borrar ",auxNodo,auxNodo[2]-auxNodo[1]


    '''
    print "generando links"
    for comp in Diccionario  :
        for comp2 in Diccionario  :
            if comp != comp2 :
                lista=Diccionario[comp]
                lista2=Diccionario[comp2]
                if len (lista) == len (lista2) and lista2[0][1]>lista[0][1]:
                    tipoLink=-1
                    auxLink=-1
                    for i in range(0, len(lista)):
                        if lista[i][2] +epsilon >lista2[i][2]:
                            tipoLink=2
                        elif lista[i][2]<lista2[i][2] and lista2[i][1] + epsilon <lista[i][2]:
                            tipoLink=1
                        elif lista[i][2]+epsilon<lista2[i][1]:
                            tipoLink=2                        
                        if (auxLink!=-1 and auxLink!=tipoLink) or tipoLink==-1:
                            break
                        auxLink=tipoLink    
                    if tipoLink!=-1:  
                        links.append((comp,comp2,abs(tipoLink)))
    '''

    print "generando links"

    #se agrega el nodo init al final del grafo
    tiempo=current_milli_time()+epsilon + 300 #para adelantarlo al ultimo nodo
    nuevoNodo=(identify, tiempo ,tiempo + 2*epsilon +5000, 0, {})#se le da un tiempo de fin 
    # nodos[id]= nuevoNodo
    nodos.append(nuevoNodo)
    print "id del init ",identify

    print "tamanio nodos ",len(nodos)
    '''
    for a in nodos  :
	n1=nodos[a]
	for b in nodos  :
	    n2=nodos[b]
    '''
    for n1 in nodos  :
        for n2 in nodos  :
            if n1[0] != n2[0] and n1[1] <= n2[1]:#son nodos distintos y n2 se agrego luego que n1   

		#print "enlaces ",n1,n2,n1[2]+epsilon,n2[1]         
                
		tipoLink=-1
		    
		if n1[2] +epsilon >n2[2]: #el final de n1 mayor al de n2
		    tipoLink=2 #permanente
		elif n1[2]<n2[2] and n2[1] + epsilon <n1[2]:#el final de n2 cae en medio de n2
		    tipoLink=1 #habilitacion
		elif n1[2]+epsilon<n2[1]: #el final de n1 es menor al inicio de n2
		    tipoLink=0 #orden  
                if tipoLink!=-1:  
		   # links.append((n1[0],n2[0],tipoLink))
		    links.append((n1[0],n1[3] ,n2[0],n2[3] ,tipoLink))#id nodo 1 (2) comportamiento nodo 1 (2)
    		else:
		    print "el nodo no se agrego"
 
    # print "links ",links
    for it in links:       
	print "links ",it[1]," ",it[3]," ",it[4]
	
	
	
#lanza los nodos y crea los enlaces  , NOTA hay que sacar al nodo init en si como un nuevo nodo (no esta bueno que este embebido aca)
def crearEnlaces():
    nodosLanzados=[] 
    global identify
    
    
    for it in links:
        #hay que evitar lanzar el nodo init y hay que obtener su id VERIFICAR AL SACAR INIT DE ACA        
        if(it[1]==0):
            identify=it[0]
            nodosLanzados.append(identify)
        if(it[3]==0):
            identify=it[2]
            nodosLanzados.append(identify)
    
        #se lanzan los nodos del enlace en caso de no haber sido lanzados
        if( not it[0] in nodosLanzados):
            lanzarNodo(it[0],it[1])
            nodosLanzados.append(it[0])
        if( not it[2] in nodosLanzados):
            lanzarNodo(it[2],it[3])
            nodosLanzados.append(it[2])
     
    #se envian los links a los nodos el sleep es para esperar que los nodos esten listos se puede hacer un waitmensaje
    time.sleep(5)
    for it in links:
        msg = Int32MultiArray()
	msg.data = [it[0], it[2], it[4]]#id nodo 1 y 2 y tipo de link	
        pub.publish(msg)        
        
        
        
        

def nodoActivo(comportamiento):
    #verificar si en la lista del comportamiento hay un nodo activo
    nodoActivo=False
    if Diccionario.has_key(comportamiento):        
        listaActual=Diccionario[comportamiento]
        tamanio=len (listaActual)    
        if tamanio>0 :
            ultimoNodo=listaActual[tamanio-1]
            datos=list(ultimoNodo)
            final=datos[2]
            if final== -1:
                nodoActivo=True
    return nodoActivo

#solo se atiende si estamos en fase de aprendizaje
def aprender(data):
    global fase 
    if fase == "aprender":
	callback(data)


def callback(data): 
    comportamiento=data.data[0] 
    postcondicion=data.data[1]
           
    #print "valor postcondicion: ",postcondicion," comportamiento: ",comportamiento

    global nodos
    global id

    if postcondicion == 1:
        #nodo nuevo comportamiento recien activado
        if not Diccionario.has_key(comportamiento):
            Diccionario[comportamiento]=[]
        #no hay nodo activo se agrega uno nuevo
        if not nodoActivo(comportamiento):   
            print "nodo comportamiento nuevo ",comportamiento
            #agregar nodo            
            nuevoNodo=(id, current_milli_time(), -1, comportamiento, {})
           # nodos[id]= nuevoNodo
            nodos.append(nuevoNodo)
            Diccionario[comportamiento].append(nuevoNodo)       
            id = id + 1
            print "nodos: ",nodos
        #nodo ya activado y lo sigue estando
        #else:
            #print "nodo comportamiento sigue activo"
            #actualizar datos del nodoactivo
            #print "nodos ",nodos
    #comportamiento que estaba activo y se apaga
    elif nodoActivo(comportamiento):
        print "finalizar nodo comportamiento",comportamiento
        #verificar que el inicio del nodo actual esta a menos de errorRuido del fin de otro nodo del mismo comportamiento 
        #en tal caso hacer un merge
        tiempoFinal=current_milli_time()
        print "tiempo final: ",tiempoFinal," ",comportamiento
        lista=Diccionario[comportamiento]
        tamanio=len(lista)
        hayQueMerger=False        
        ultimo=list(lista[tamanio-1])
	#ultimo=list(id)        

	#hay mas de un nodo se verifica si hay que hacer merge
        if tamanio > 1:            
            anterior=list(lista[tamanio-2])
            #se verifica inicio del ultimo y fin del anterior y se saca el ultimo de diccionario y se
            #le asigna final al anterior, de los nodos se saca el de id ultimo
            print ultimo[1]-anterior[2]
            if (ultimo[1]-anterior[2])<errorRuido:
                print "hay que merger ",comportamiento
                hayQueMerger=True                
                del lista[tamanio-1]
                del lista[tamanio-2]
                anterior[2]=tiempoFinal
                mergeado=tuple(anterior)
                lista.append(mergeado)
                Diccionario[comportamiento]=lista
		#de la lista de nodos hay que borrar el nodo que se mergeo y acomodar el nodo anterior con su nuevo final
                #del nodos[ultimo[0]] 
                #nodos[anterior[0]]=mergeado
                mergeNodos(ultimo[0], anterior[0],mergeado)               
        #se asigna el final y se ajustan a nodos y diccionario        
        if not hayQueMerger:
            ultimo[2]=tiempoFinal
            del lista[tamanio-1]            
            finalizado=tuple(ultimo)
            lista.append(finalizado)
            Diccionario[comportamiento]=lista
            #nodos[len(nodos)-1]=finalizado
            cerrarNodo(ultimo[0],finalizado)
            print "cerrar directamente ",comportamiento

        #print nodos   

def cerrarNodo(idCerrar,finalizado):
    global nodos
    for n in range(len(nodos)-1,-1,-1):
	if nodos[n][0]==idCerrar:
            nodos[n]=finalizado
            return

def mergeNodos(idEliminar,idModificar,nodoMergueado): 
    global nodos
    pasosRestantes=2
    for n in range(len(nodos)-1,-1,-1):
	if nodos[n][0]==idEliminar:
            del nodos[n]	    	
	    pasosRestantes=pasosRestantes-1
	    if pasosRestantes<=0:
		return	
	elif nodos[n][0]==idModificar:
	    nodos[n]=nodoMergueado
	    pasosRestantes=pasosRestantes-1	   
	    if pasosRestantes<=0:
		return



#No olvidar ajustar el nombre de pkg al del proyecto
def lanzarNodo(idNodo,idComportamiento): #es el id numerico del comportamiento

    '''
    Nodin = roslaunch.core.Node
    #n = Nodin('prototipo', 'type1')
    n = Nodin('prototipo', 'type4', args="que dice")
    print "junate esta", n.to_remote_xml()
    '''

    nombreComportamiento=dicComp [idComportamiento]
    print "se lanza el comportamiento",nombreComportamiento
    pkg = 'learning_by_imitation'
    global process   
    execution =nombreComportamiento + '.py'
    # Ver como usar args en las tareas localizar y avanzar.     
    node = roslaunch.core.Node(pkg, execution, args=str(idNodo))
    launch = roslaunch.scriptapi.ROSLaunch()
    launch.start()
    process[idNodo] = launch.launch(node)



def evaluation(l):
    result = True
    for it in l:
        result = result and it
        if not result:
            break
    return result



def setting(data):
   global identify
   #print "entro en setting init ",data.data[1]," id init ",identify
    
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
    print "entro en ejecutar localizar"
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
        print "es de orden"
    else:
        skip = True
        
    print ordering

    #se detecta cumplimiento de una postcondicio...entonces el init manda su nivel de activacion para
    #atras...si un nodo recibe y puede ejecutar ejecuta, si no puede manda
    #su nivel para atras y pone su nivel en 0 
    arranqueNivel()

 






def arranqueNivel():
    print "nivel de activacion init"
    global nivel
    msg = Int32MultiArray()
    fin=True
    for o in ordering:
        #en caso que la relacion de orden aun no se cumplio
	if not ordering[o]:
	    msg.data = [identify, o]#manda para atras el nivel
	    nivel.publish(msg)
	    fin=False
    if fin:
	rospy.loginfo("termino el ciclo")
	msg = Int32MultiArray()
	msg.data = [-1,-1] 	 
        motores.publish(msg) 
        motores


#se elimina un nodo de la lista habria que verificar si pasaron menos de 10 segundos desde que termino el comportamiento anterior
#en tal caso se elimina el nodo anterior si pasaron mas de tiempoEsperaBad segundos se asume que se quiere borrar el nodo actual Verificar
def buscarIdBad(linksAModificar):
    #hay que saber que nodo se ejecutaba antes del actual si no pasaron mas de 10 segundos tambien hay que guardar el id   
    print "implementar"
    
    
#Nota los links no tienen un orden en la lista, el nodo init no se debe borrar (controlar en el q llama a este metodo)
def borrarNodoBad(linksBad,idBad):      
    #creo la lista de destinos del nodo a borrar
    listaDestino=[]
    print "linkbad",linksBad
    for d in range(len(linksBad)):
        if (linksBad[d][0]==idBad):
            #se agregan los id y comportamiento a listaDestino 
            listaDestino.append((linksBad[d][2],linksBad[d][3]))    
                    
    print "destino",listaDestino
            
    #de los que son origen del nodo a borrar agrega los destinos del nodo a borrar
    for l in range(len(linksBad)):
        if (linksBad[l][2]==idBad):#idborrar es destino del links
            for d in range(len(listaDestino)):    
                #se agregan links de orden entre los origens de los nodos y los destinos del nodo borrado 
                linksBad.append((linksBad[l][0],linksBad[l][1],listaDestino[d][0],listaDestino[d][1],0))
    
    print "linkbad",linksBad
    
    #se eliminana todos los links que tengan a idborrar como origen o destino
    for b in range(len(linksBad)-1,-1,-1):
        if (linksBad[b][0]==idBad or linksBad[b][2]==idBad):
            del linksBad[b]
    return linksBad
    
    

if __name__ == '__main__':
    process = {}

    print "iniciando init"
    rospy.init_node('init', anonymous=True) 
    id=0
 
    pub=rospy.Publisher('preConditionsSetting', Int32MultiArray, queue_size = 10)
    estado=rospy.Publisher('topicoEstado', Int32MultiArray, queue_size = 10)
    rospy.Subscriber("preConditionsSetting", Int32MultiArray, setting)	 
    nivel = rospy.Publisher('topicoNivel', Int32MultiArray, queue_size=10)
    rospy.Subscriber("postConditionDetect", Int32MultiArray, aprender)
    rospy.Subscriber("preConditionDetect", Int32MultiArray, evaluarPrecondicion)
    motores = rospy.Publisher('topicoActuarMotores', Int32MultiArray, queue_size=10)
    
   
   
    entrada=raw_input()   
    msg = Int32MultiArray()
    while entrada != "salir":
	if entrada=="finDemo":
            fase="nada"
	    msg.data = [0,1]#debe avisar antes de hacer offline que se cierra asi no quedan mensajes colgados 
	    estado.publish(msg)
	    offLine()
	    '''
            topo = Int32MultiArray()
	    topo.data = [1,2,2]
            pub.publish(topo)
            '''            
	elif entrada=="aprender":
	#hay que lanzar comportamientos para que reciban las postcondiciones a la hora de aprender NO OLVIDAR MATARLOS AL TERMNAR APRENDER
            pkg = 'prototipo'
            process = {}
            for n in dicComp:
                lanzarNodo(n,n) 
	
	
	    fase="aprender"	    
	    Diccionario={}
            nodos = []
	    msg.data = [1,1]#podria ser el segundo valor el id del comportamiento
	    estado.publish(msg)
	elif entrada=="ejecutar":
	    for it in process.values():
                print it.stop()	
    	    fase="ejecutar"
    	    
    	    
    	    
	    #aca se podria cargar la lista de nodos a ejecutar por ahora uso los definidos en el metodo
	    
	    #links=[(0,1,1,2,0),(0,1,2,0,0),(1,2,2,0,0)]	
	    links=[(0,1,1,2,0),(0,1,2,0,0),(1,2,2,0,0)]	
	    crearEnlaces()
	    
	    #se deberia esperar a que los comportamientos se activen sino no reciben el mensaje de estado
	    #se podria esperar un mensaje es decir por medio de wait
	    time.sleep(5)
	    
	    
	    msg.data = [2,2] 
	    estado.publish(msg)
	    arranqueNivel()
	    
	elif entrada=="bad":  
	    linksBad=[(1,1,3,3,0),(2,2,3,3,0),(3,3,4,4,0),(3,3,5,5,0),(5,5,6,6,2)]	
	    salida=borrarNodoBad(linksBad,3)
	    print salida
	    msg.data = [0,0] 
	    estado.publish(msg)
	else:
	    msg.data = [0,1]
            estado.publish(msg)
        entrada=raw_input()
        
    #rospy.spin()

