#!/usr/bin/env python
import sys
import rospy
import roslaunch
import lcs
from std_msgs.msg import String,Int32MultiArray, Float64MultiArray
import Const
import threading, time
import loadBehavior

pkg = "learning_by_imitation"#paquete donde se encuentran los archivo py
#pkg = "vrep_ros_demo"
#pkg="behavior"
 
 
idNA= 0
#dicComp={0:'init',1:'localizar', 2:'avanzar', 3:'irA'} #asocia idnumerico con nombres de comportamientos
dicComp={0:'init'} #asocia idnumerico con nombres de comportamientos


 
identify=-1
Diccionario={}
nodosLanzados={}
nodos = {}
links = []
linkEnEjecucion=[]

dicNodoComp={}#asocia id de nodo con comportamiento
dicNodoParam={}#asocia nodo con comportamiento

auxDicNodoComp={}
auxDicNodoParam={}

comando=""

errorRuido=2000#usado para errores de ruido
epsilon=2000#usado para determinar tipos de links puede pasar que se cierre un comportamiento luego de cerrar otro
tiempoEsperaBad=5000 #tiempo que se acepta luego de terminado un comportamiento para indicar que se debe eliminar del grafo
enablig = {}
ordering = {}
permanent = {}
fase="nada"
#el primer par de indices es el nodo anterior id,tiempo de fin el segundo es el nodo actual para evaluar los 10 segundos se recuerda el anterior
#esto se usa para el caso BAD
nodoEjecutando=(-1,-1,-1,-1)
idCome=-1
grafoGeneral=[]#grafo generado tras varias demostraciones
tiempoBad=5000
nodosParaAprender={}#se lanzan nodos con el fin de aprender
nodosParaEjecutar={}#nodos lanzados an el proceso de ejecucion
current_milli_time = lambda: int(round(time.time() * 1000))  

################################
#APRENDER
################################
	

#solo se atiende si estamos en fase de aprendizaje
def atenderAprender(data):
    global fase  
    if fase == "aprender":
        callback(data)
  
  
  
def separarBloques(data):
        #print "callback: ",data
        strData=str(data)
        #rospy.loginfo("comportamiento datos recibidos"+str(data))
        return map(str, strData.split('|'))
        
    
def separarSensados(separar):
        sensados={}
        for s in  separar:
            if len(s)>1:
            	#rospy.loginfo(str(len(s))+"separar "+s)
            	datos = map(float, s.split('#'))
            	#print "sensado y datos ", s,datos
            	idSensor=int (datos[0])
            	del datos[0]
            	sensados[idSensor]=datos        
        return sensados  
  

#se pueden pasar parametros como un array donde el primer elemento indica el tipo 
#de parametro y el segundo cantidad de valores los demas serian los daots, con un for se recorre etc
def callback(data):
    
    separados=separarBloques(data.data)
    d=separados[0]
    #print "separados ",d
    
    datos = d.split('#')
    del separados[0]
    param=separarSensados(separados)
    
    
    comportamiento=str(datos[0]) 
    postcondicion=int(datos[1])
    
              
    #print "valor postcondicion: ",postcondicion," comportamiento: ",comportamiento

    global nodos
    global idNA

    if postcondicion == 1:
        #nodo nuevo comportamiento recien activado
        if not Diccionario.has_key(comportamiento):
            Diccionario[comportamiento]=[]
            
        #nodo ya activado y lo sigue estando
        idActivo=nodoActivo(comportamiento)
        if idActivo!=-1:   
            #print "nodo comportamiento sigue activo"
            #actualizar datos del nodoactivo en ambas estructuras nodos y dicc
            updateParam(nodos[idActivo], param)     
        #no hay nodo activo se agrega uno nuevo
        else:
            print "nodo comportamiento nuevo ",comportamiento
            #agregar nodo            
            nuevoNodo=(idNA, current_milli_time(), -1, comportamiento, param)
            print "idNA en call ",idNA," largo ",len (nodos) 
            nodos[idNA]= nuevoNodo
            #nodos.append(nuevoNodo)
            Diccionario[comportamiento].append(nuevoNodo)       
            idNA = idNA+ 1
            print "nodos: ",nodos

    #comportamiento que estaba activo y se apaga
    elif nodoActivo(comportamiento)!=-1:
        print "finalizar nodo comportamiento",comportamiento
        #verificar que el inicio del nodo actual esta a menos de 
        #errorRuidNAo del fin de otro nodo del mismo comportamiento 
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
                # FALTA hacer el merge teniento en cuenta los parametros 
                hayQueMerger=True                
                del lista[tamanio-1]
                del lista[tamanio-2]
                anterior[2]=tiempoFinal
                mergeado=tuple(anterior)
                updateParam(mergeado, param)
                lista.append(mergeado)
                Diccionario[comportamiento]=lista
                #de la lista de nodos hay que borrar el nodo que se mergeo 
                #y acomodar el nodo anterior con su nuevo final
                del nodos[ultimo[0]] 
                nodos[anterior[0]]=mergeado
                #mergeNodos(ultimo[0], anterior[0],mergeado)  
                
                
                             
        #se asigna el final y se ajustan a nodos y diccionario        
        if not hayQueMerger:
            ultimo[2]=tiempoFinal
            del lista[tamanio-1]            
            finalizado=tuple(ultimo)
            lista.append(finalizado)
            Diccionario[comportamiento]=lista
            nodos[ultimo[0]]=finalizado
            #cerrarNodo(ultimo[0],finalizado)
            print "cerrar directamente ",comportamiento

        #print nodos  

#Arreglar
def updateParam(nodo, paramNuevo):
    salida=nodo
    return salida


def offLine ():
	
    #hay que cerrar los comportamientos cuando se cierre la demostracion
    #si no estaba prendido se ocupa el callback de ignorarlo
    msg = Int32MultiArray()
    for comp in Diccionario  :
        #msg.data = [comp,0]
        
        msg.data = str(comp)+"#0|0#1#1#1"
        callback (msg)	  
    
    #eliminar nodos de menos que errorRuido y a la vez lanzar los nodos del grafo
    global nodos
    global idNA
    global identify
    global links
    global auxDicNodoComp
    global auxDicNodoParam
    
    
    auxNodos={}
    
    idNodeAdd=lcs.getNewId()
    print "id nodo inicial ",idNodeAdd
    for n in nodos.values(): 	
        if n[2]-n[1]>errorRuido:   #el nodo es menor a un errorRuido
            auxl=list (n)
            auxl[0]=idNodeAdd
            idNodeAdd = idNodeAdd + 1
            auxNodos[idNodeAdd]=tuple(auxl)
            print "valores de nodos a agregar ",n,n[2]-n[1]
    nodos =  auxNodos    
       
    idNA=idNodeAdd #ultimo nodo es el init

    '''
    for n in range(len(nodos)-1,-1,-1):
        auxNodo=nodos[n]
	
        if auxNodo[2]-auxNodo[1]<errorRuido:   #el nodo es menor a un errorRuido
            del nodos[n]
            print "valores de nodos a borrar ",auxNodo,auxNodo[2]-auxNodo[1] 
    '''       
            
            
            
            
            
    print "generando links"
    print "tamanio nodos ",len(nodos) 
    links=[]
    for n1 in nodos.values()  :
        #carga los diccionarios
        if not  auxDicNodoComp.has_key(n1[0]):
            auxDicNodoComp[n1[0]]= n1[3] 

        if not  auxDicNodoParam.has_key(n1[0]):
            auxDicNodoParam[n1[0]]= n1[4]



        for n2 in nodos.values()  :
            if n1[0] != n2[0] and n1[1] <= n2[1]:#son nodos distintos y n2 se agrego luego que n1   

                #print "enlaces ",n1,n2,n1[2]+epsilon,n2[1]         
                
                tipoLink=-1
		    
                if n1[2] +epsilon >n2[2]: #el final de n1 mayor al de n2
                    tipoLink=2 #permanente
                elif n1[2]<n2[2] and n2[1] + epsilon <n1[2]:#el final de n2 cae en medio de n2
                    tipoLink=1 #habilitacionauxDicNodoParam
                elif n1[2]+epsilon<n2[1]: #el final de n1 es menor al inicio de n2
                    tipoLink=0 #orden  
                if tipoLink!=-1:  
                    #links.append((n1[0],n1[3] ,n2[0],n2[3] ,tipoLink))#id nodo 1 (2) comportamiento nodo 1 (2)
                    links.append((n1[0],n2[0] ,tipoLink))
                else:
                    print "el nodo no se agrego"
    if len (nodos)>0:
        agregarNodoInit(idNA)

 

        


    # print "links ",links
    for it in links:       
        print "links ",it[0]," ",it[1]," ",it[2]

    
	

#se desacopla de offline para poder usar el metodo anterior en el metodo go, ya que ahi no se necesita este nodo init
#tal vez si se necesite ya que de habeer un solo nodo no hay links que agregar
def agregarNodoInit(idInit):
    global links
    global nodos  
    global auxDicNodoComp
    global auxDicNodoParam  
    for n in nodos.values()  :
        links.append((n[0],idInit,0))

    if not  auxDicNodoComp.has_key(idInit):
        auxDicNodoComp[idInit]= "init"

    if not  auxDicNodoParam.has_key(idInit):
        auxDicNodoParam[idInit]= {}


    
#retorna el id del nodo activo para un comportamiento    
def nodoActivo(comportamiento):
    #verificar si en la lista del comportamiento hay un nodo activo
    nodoActivo=-1
    if Diccionario.has_key(comportamiento):        
        listaActual=Diccionario[comportamiento]
        tamanio=len (listaActual)    
        if tamanio>0 :
            ultimoNodo=listaActual[tamanio-1]
            datos=list(ultimoNodo)
            final=datos[2]
            #el nodo aun no esta cerrado
            if final== -1:
                nodoActivo=datos[0]
    return nodoActivo

'''
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
'''


#solo se usa para crear la topologia a partir de una sola demostracion
def crearTopologia (enlaces):
    salida =[]
    aux={}#diccionario tendra todos los nodos y la cantidad de enlaces que tiene
    print "links cretto",enlaces
    for l in enlaces:
        #se agregan al diccionario todos los nodos
        if not aux.has_key(l[0]):
            aux[l[0]]=0
        #se agrega el nodo destino porque eventualmente podria ser el nodo final y no aparece como inicio de links
        if not aux.has_key(l[1]):
            aux[l[1]]=0
        aux[l[0]]=aux[l[0]]+1
    lista=aux.items()

    #ordena por largo del camino
    ordenado=sorted(lista,key=lambda tup:tup[1])  
    for i in range(len(ordenado)-1):
        salida.append((ordenado[i+1][0],ordenado[i][0]))
    print "links cretto",enlaces," salida ",salida
    return salida


def merggearNuevaDemo():
    global links
    lcs.nuevaDemostracion( crearTopologia (links),links)
                
############################ 
#Lanzar un nodo para
#ejecutar o para aprender
############################      


def paramToString(param):
    salida=""
    for p in param:
        if len (salida)>0:
            salida=salida+'|'
        salida=salida+str(p)
        for d in param[p]:
            salida=salida+'#'+str(d)
    print "paramtostring", salida
    return salida        
             
        
        
              
                
def lanzarNodo(idNodo,idComportamiento): #es el id numerico del comportamiento 
    global dicComp
    global dicNodoParam
    #nombreComportamiento=dicComp [idComportamiento]
    nombreComportamiento=str(idComportamiento)
    print "se lanza el comportamiento:",nombreComportamiento
    
    
    global pkg
    global dicNodoParam  
    execution =nombreComportamiento + '.py'
    # en los args se envian los id de los nodos y los parametros
    if idComportamiento == "init":
        node = roslaunch.core.Node(pkg, execution, args=str(idNodo) )
    else :
        sensado=paramToString(dicNodoParam)
        data= str(idNodo)
        if len(sensado)>1:
            print "diccionario nodo param ",dicNodoParam,idNodo,dicNodoParam[int(idNodo)]
            data=data + '|' + paramToString(dicNodoParam[int(idNodo)])              
        node = roslaunch.core.Node(pkg, execution, args=str(data) )
        #node = roslaunch.core.Node(pkg, execution, env_args=[("identify",str(idNodo)),("color","negro")] )
    
    
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
    print "cargar Datos mediante XML"


#se deberian recuperar la topologia de un XML
def recuperarTopologia():
    #global links
    #return crearTopologia(links)
    return lcs.getTopologiaGeneral()    


#se deberian recuperar los enlaces de un XML
def recuperarEnlaces():
    #global links
    return lcs.getNetworkGeneral()




######SI SE CREA EL NODO INIT SEPARADO DE AQUI NO HACE FALTA SER TAN CUIDADOSO	
#lanza los nodos y crea los enlaces  , NOTA hay que sacar al nodo init en si como un nuevo nodo (no esta bueno que este embebido aca)
def crearEnlaces(linksACrear):
    nodosLanzados=[] 
    global identify    
    global dicNodoComp
    for it in linksACrear:
        '''
        #hay que evitar lanzar el nodo init y hay que obtener su id VERIFICAR AL SACAR INIT DE ACA        
        if(it[1]==0):
            identify=it[0]
            nodosLanzados.append(identify)
        if(it[3]==0):
            identify=it[2]
            nodosLanzados.append(identify)
        '''
        #se lanzan los nodos del enlace en caso de no haber sido lanzados
        if( not it[0] in nodosLanzados):
            nodosParaEjecutar[it[0]]=lanzarNodo(it[0],dicNodoComp[it[0]])
            nodosLanzados.append(it[0])
        if( not it[1] in nodosLanzados):
            nodosParaEjecutar[it[1]]=lanzarNodo(it[1],dicNodoComp[it[1]])
            nodosLanzados.append(it[1])
     
    #se envian los links a los nodos el sleep es para esperar que los nodos esten listos se puede hacer un waitmensaje
    time.sleep(1)
    for it in linksACrear:
        msg = Int32MultiArray()
        msg.data = [it[0], it[1], it[2]]#id nodo 1 y 2 y tipo de link	         
        rospy.loginfo(msg.data)
        pub.publish(msg) 


def ejecutarBad():
    global nodoEjecutando 
    global tiempoBad
    tiempoActual=current_milli_time()
    #si el nodo actual inicio hace menos de tiempoBad se borra el nodo anterior    
    tiempoDif= tiempoActual - nodoEjecutando[1]
    dentroDElTiempo=tiempoDif<tiempoBad
    existeNodoAnterior=nodoEjecutando[0] >=0
    
    #se elimina el nodo que esta en ejecucion, notar que si es el ultimo nodo tambien funciona porque al no haber
    #comportamiento posteriores el valor de ejecutando queda seteado en el ultimo nodo, es decir solo se modifica si un
    #nuevo nodo ejecuta, en caso de dejar de ejecutar no se notifica
    nodoABorrar=nodoEjecutando[2]
    if existeNodoAnterior and dentroDElTiempo:
        nodoABorrar=nodoEjecutando[0]            
    lcs.borrarNodoBad(nodoABorrar)        
    lcs.graficar("bad")   
    
    #se publica estado a Bad capaz el nombre habria que cambiarlo,
    msg = Int32MultiArray()
    msg.data = [4,nodoABorrar] 
    estado.publish(msg)
    
        
        
    

##lo siguiente de bad ya no iria

#se elimina un nodo de la lista habria que verificar si pasaron menos de tiempoBad desde que inicio el comportamiento actual y existe anterior
#en tal caso se elimina el nodo anterior si pasaron mas de tiempoEsperaBad segundos se asume que se quiere borrar el nodo actual Verificar
def BACKejecutarBad(linksAModificar):
    global nodoEjecutando 
    global tiempoBad
    tiempoActual=current_milli_time()
    #si el nodo actual inicio hace menos de tiempoBad se borra el nodo anterior    
    tiempoDif= tiempoActual - nodoEjecutando[1]
    dentroDElTiempo=tiempoDif<tiempoBad
    existeNodoAnterior=nodoEjecutando[0] >=0
    
    if existeNodoAnterior and dentroDElTiempo:
        borrarNodoBad(linksAModificar,nodoEjecutando[0])               
    
    #se elimina el nodo que esta en ejecucion, notar que si es el ultimo nodo tambien funciona porque al no haber
    #comportamiento posteriores el valor de ejecutando queda seteado en el ultimo nodo, es decir solo se modifica si un
    #nuevo nodo ejecuta, en caso de dejar de ejecutar no se notifica
    else :
        borrarNodoBad(linksAModificar,nodoEjecutando[2])
        
    return linksAModificar     
        
    
#Nota los links no tienen un orden en la lista, el nodo init no se debe borrar (controlar en el q llama a este metodo)
def borrarNodoBad(linksBad,idBad):      
    #creo la lista de destinos del nodo a borrar
    listaDestino=[]
    print "linkbad",linksBad
    for d in range(len(linksBad)):
        if (linksBad[d][0]==idBad):
            #se agregan los id y comportamiento a listaDestino 
            listaDestino.append((linksBad[d][2],linksBad[d][3]))    
                    
    print "destinos del nodo borrado",listaDestino
            
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
    
    
    
    
def atenderNodoEjecutando(data):
    global nodoEjecutando

    #llega un nuevo nodo ejecutando
    if  data.data[0] != nodoEjecutando[2]: 
        #acomodo los datos del que era ultimo pasa a ser el anterior
        
        a=nodoEjecutando[2]
        b=nodoEjecutando[3]
        #agrero el nuevo nodo ejecutando con su tiempo de inicio
        c=data.data[0]
        d=current_milli_time()
        nodoEjecutando=(a,b,c,d)

#verificar como se agrega un tramo entre el ultimo nodo y el init si hay lios con el BAD

#come debe guardar el id del nodo actual luego en ejecutar go se usara este valor para partir el grafo y agregar lo que se obtuvo en here
#se debe evitar que el robot siga en modo ejecucion y pase a un estado parecido a aprender pero que solo se mueva es decir no envie senales       
def ejecutarCome ():
    #se establece a partir del nodo actual el corte y se agrega lo aprendido justo antes de este nodo
    global idCome
    global estado
    idCome=nodoEjecutando[2]
    msg = Int32MultiArray()
    msg.data = [3,3] #estado para agregar comportamientos
    estado.publish(msg)

    


#a partir de aqui se debe pasar a una etapa de aprendizaje el link obtenido se debe guardar, recordar que para aprender se lanzan nuevos nodos
#por lo cual el estado de los nodos no se modifica 
def ejecutarHere():    
    global estado
    global fase
    global nodosParaAprender
    nodosParaAprender = {}
    for n in dicComp:
        if n!=0:#lanza nodos sin ser el init
            nodosParaAprender[n]= lanzarNodo(-1,n) 
    fase="aprender"	    
    Diccionario={}
    nodos = []
    msg.data = [1,1]#podria ser el segundo valor el id del comportamiento
    estado.publish(msg)
    print "ejecuto here"
    
    
#se realiza la particion del grafo se agrega los link obtenidos en here  se pasa a modo ejecucion nuevamente y se continua la ejecucion
def ejecutarGo(): 

    print "entro en go"
    
    global estado
    global idCome
    global nodosParaAprender
    #se obtiene el grafo generado en la mini demostracion
    global links
    #se corta el grafo general 
    global grafoGeneral 
    fase="nada"
    msg.data = [0,1]#debe avisar antes de hacer offline que se cierra asi no quedan mensajes colgados 
    estado.publish(msg)
    for it in nodosParaAprender.values():
        print it.stop()	
    print "antes de offline en go"   
    offLine()         
    print grafoGeneral   

    lcs.cortarGoCaminos(grafoGeneral,links,idCome,nodoEjecutando[0])
    lcs.graficar("go")
    #cortarGo(links,grafoGeneral,idCome)     
    #se vuelve al estado ejecucion
    fase="ejecutar"
    msg.data = [2,2] 
    estado.publish(msg) 
    
#lo que sigue de go no iria       

def cortarGo(nuevolinks,grafoGeneral,idCome): 
    if len(nuevolinks) ==0:
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
        #a cada nodo se le suma en su id el idMAximoGeneral
        modificado=(aux[0]+idMAximoGeneral,aux[1],aux[2]+idMAximoGeneral,aux[3],aux[4])
        nuevolinks[i]=modificado
                
    print "nuevolinks ",nuevolinks    
    
    
    
    '''
    sinSucesores=[]
    sinPredecesores=[]
    #agrego todos los id de los nodos a las listas sin..
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
     
    
    #de los nodos previos al objetivo, agregar links con destino al nodo inicial del nuevo link
    #hay que borrar los enlaces que tienen como destino el nodo objetivo
    
    #se agregan los enlaces de los nodos previo al nodo inicial del nuevo link
    for i in range(len(grafoGeneral)):
        if grafoGeneral[i][2]==idCome:
            aux=grafoGeneral[i]
            grafoGeneral.append((aux[0],aux[1],inicio[0],inicio[1],0))    
    
    
    #se borran los enlaces con destino a objetivo
    for i in range(len(grafoGeneral)-1,-1,-1):
        if grafoGeneral[i][2]==idCome:
            del grafoGeneral[i]
    
    
    
    #del nodo final del nuevo link agregar enlace al nodo objetivo 
    objetivo=buscarComportamiento(idCome,grafoGeneral)  
    grafoGeneral.append((fin[0],fin[1],objetivo[0],objetivo[1],0))
    ''' 
    
    
    #diccionarios con clave el id del nodo y valor el id del comportamiento
    predecesores={}
    sucesores={}
    nuevos={}
     
    
    for g in grafoGeneral:  
        if g[2]==idCome and not (predecesores.has_key(g[0])):
            predecesores[g[0]]=g[1]
        if g[0]==idCome:
            #se agrega el nodo come como un sucesor
            if not (sucesores.has_key(g[0])):
                sucesores[g[0]]=g[1]   
            #se agrega el sucesor si no estaba en la lista        
            if not (sucesores.has_key(g[2])): 
                sucesores[g[2]]=g[3]            
            
    for n in nuevolinks:       
        #se agregan nodos nuevos a una lista
        if not (nuevos.has_key(n[0])): 
            nuevos[n[0]]=n[1]
        if not (nuevos.has_key(n[2])) and n[3] !=0:#no se agrega el init
            nuevos[n[2]]=n[3]  
      
    print "nuevos ",nuevos
    print "predecesores  ",predecesores
    print "sucesores ",sucesores 
            
    for n in nuevos:
        for p in predecesores:
            print p,n
            grafoGeneral.append((p,predecesores[p],n,nuevos[n],0))
        for s in sucesores:
            grafoGeneral.append((n,nuevos[n],s,sucesores[s],0)) 
    
    
    print "grafo general al terminar cortargo", grafoGeneral
    
    return grafoGeneral
     
     
def buscarComportamiento(idNodo,linksBuscar): 
    for b in linksBuscar:
        if b[0]==idNodo:
            return (b[0],b[1])
        if b[2]==idNodo:
            return (b[2],b[3])
    return  (-1,-1)   
        
     


#######################
#creacion de caminos
#######################




def sucesoresTopologicos (topologia):
    salida={}
    #dada una topologia el diccionario guarda como clave el id del nodo
    #y como valores una lista de los sucesores
    for t in topologia:
        if not salida.has_key(t[0]):
            salida[t[0]]=[]
        salida[t[0]].append(t[1])
    return salida

    
#Tal vez se podria primero ver los que no tienen predecesores y lanzar esos por temas de eficiencia
#aca se recorren todos los nodos y se hace el algoritmo
def pathAntecesores( sucesoresTopologicos):
    #los nodos son un dicc, cada nodo tene una lista de path y cada path es una lista de nodos
    salida ={}
    for nodo in sucesoresTopologicos:#para cada nodo 
        print "Nodo ",nodo
        if not salida.has_key(nodo):    
            salida[nodo]=[]
        salida = recursionEnvioPath(nodo,[], salida,sucesoresTopologicos)   
         
    return salida    
    



#se recibe un path, se verifica si hay un path que coincida hasta el final
#en tal caso se sobreescribe el path mas corto que habia, la idea es que algun otro nodo se agrego al path..
#luego el nuevo path se envia a los nodos sucesores de forma recursiva
def recursionEnvioPath(nodo, pathAdd, caminos, sucesoresTopologicos):
    path=list(pathAdd)
    path.append(nodo)
    if nodo in sucesoresTopologicos:
        for sucesor in sucesoresTopologicos[nodo]:
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
                    #print "entro ejecutar()en path mas largo sucesor",sucesor," CML ", caminos[sucesor][cs],">>", caminos 
                    caminos[sucesor][cs]=pathMasLargo                    
                    
            if accion==2:
                print "nuevoPAth ", path
                caminos[sucesor].append(path)  
            if accion >0:   
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


    
def enviarCaminos(caminos): 
    print "Enviando caminos"
    msg = Int32MultiArray() 
    global pubCaminos  
    #print caminos
    for nodo in caminos:
        print nodo
        salida=[nodo]
        for lc in range (len (caminos[nodo]) ): 
           # for c in range (len (caminos[nodo][lc]) ): 
            #print caminos[nodo][lc], lc
            salida= salida + caminos[nodo][lc] + [-10]#donde -10 es un separador              
        #se manda mensaje aunque este vacia por si hay que inicializar 
        msg.data= salida
        # print salida  
        pubCaminos.publish(msg)    
     
'''

def atenderCaminos(data):
    #global pathPosibles
    #si es mi id agrego la lismsg)

def ta de caminos camino el nodo
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
 
#######################
#Metodo Principal
#######################     
    
def finDemo():
    global nodosParaAprender
    global nodosParaEjecutar
    global fase
    global estado
    
    
    if fase != "aprender":
        print "ATENCION: no se inicio aprendizaje"
        return


    for it in nodosParaAprender.values():
        print it.stop()

    for it in nodosParaEjecutar.values():
        print it.stop()	
     
    fase="nada"
    msg.data = [0,1]#debe avisar antes de hacer offline que se cierra asi no quedan mensajes colgados 
    estado.publish(msg)
    offLine()
    #agregarNodoInit()#agrega el nodo init al final de link
    # y agrega enlaces de orden
    #aca se podria agregar el comportamiento del capitulo 5
    if len (links)>0:
        lcs.setDicParametros(auxDicNodoParam)
        lcs.appendDicCom(auxDicNodoComp)
        lcs.nuevaDemostracion( crearTopologia (links),links) 
    else:
        print "ATENCION: La demostracion no genero nodos"
    
          
def aprender():
    global nodosParaAprender
    global nodosParaEjecutar
    global fase
    global estado
    global dicComp
    global nodos
    global Diccionario
    #mata los nodos que hubiera activos
    for it in nodosParaAprender.values():
        print it.stop()	
    for it in nodosParaEjecutar.values():
        print it.stop()	 
        	
    #hay que lanzar comportamientos para que reciban las postcondiciones a la hora de aprender NO OLVIDAR MATARLOS AL TERMNAR APRENDER
    
    nodosParaAprender = {}
    for n in dicComp:
        if n!=0:#lanza nodos sin ser el init
            nodosParaAprender[n]= lanzarNodo(-1,n) 


    fase="aprender"	    
    Diccionario={}
    nodos = {}
    id=0
    msg.data = [1,1]#podria ser el segundo valor el id del comportamiento
    estado.publish(msg)

def ejecutar():
    global nodosParaAprender
    global nodosParaEjecutar
    global fase
    global estado
    global dicComp
    global nodos
    global Diccionario
    global dicNodoComp
    global dicNodoParam
    
    #mata los nodos que hubiera activos
    for it in nodosParaAprender.values():
        print it.stop()	
    for it in nodosParaEjecutar.values():
        print it.stop()	    
        
    fase="ejecutar"    
       	    
    #aca se podria cargar la lista de nodos a ejecutar por ahora uso los definidos en el metodo
    
    #links=[(0,1,1,2,0),(0,1,2,0,0),(1,2,2,0,0)]	
    #grafoGeneral=[(0,1,1,2,0),(0,1,2,0,0),(1,2,2,0,0)] #para no complicarla mucho uso como general este link cortito
    #linkEnEjecucion=[(0,1,1,2,0),(0,1,2,0,0),(1,2,2,0,0)]
    #linkEnEjecucion=[(0,1,1,2,0),(0,1,2,1,0),(0,1,3,0,0),(1,2,3,0,0),(2,1,3,0,0),(1,1,2,1,0)]

    dicNodoComp=lcs.getDicComportamientos()
    dicNodoParam=lcs.getDicParametros()

    #enlaces=[(0,1,1,2,2),(0,1,2,0,0),(1,2,2,0,0)]	     

    enlaces=recuperarEnlaces()

    crearEnlaces(enlaces)

    time.sleep(1)
    	    
    #topologia=[(0,1),(0,2),(1,3),(2,3)]
    #topologia=[(0,1),(1,2)]

    topologia=recuperarTopologia()	

    sucesoresTop=sucesoresTopologicos (topologia)
    print "sucesores: ",sucesoresTop
    caminitos=pathAntecesores(sucesoresTop)    
    enviarCaminos(caminitos)     
    
    #se deberia esperar a que los comportamientos se activen sino no reciben el mensaje de estado
    #se podria esperar un mensaje es decir por medio de wait
    time.sleep(1)    
    
    msg.data = [2,2] 
    estado.publish(msg)
    #arranqueNivel()

#event = threading.Event()

def handler(signum, frame):    
    global event
    event.set()
    print('Signal handler called with signal [%s]' % signum)


def atenderComandos(data):
    global comando
    print "recibo comando",data.data,str(Const.COMMAND_INIT_LEARNING)
    #event.signal() 
     
    if data.data ==str(Const.COMMAND_INIT_LEARNING):
        comando="aprender"
    elif data.data == str(Const.COMMAND_END_LEARNING):
        comando="finDemo" 
    elif data.data == str(Const.COMMAND_PLAY):
        comando="ejecutar" 
    elif data.data == str(Const.COMMAND_STOP):
        comando="salir"
    elif data.data == str(Const.COMMAND_BAD):
        comando="bad" 
           

if __name__ == '__main__':
    

    print "iniciando maestro"
    rospy.init_node('maestro', anonymous=True) 
    id=0
    dicComp=loadBehavior.load_abstract_behavior()
    dicComp.remove("irA")
    dicComp.append('init')
    print "diccionario comportamientos ",dicComp
    rospy.Subscriber("command", String, atenderComandos)
    
    pub=rospy.Publisher('preConditionsSetting', Int32MultiArray, queue_size = 10)
    estado=rospy.Publisher('topicoEstado', Int32MultiArray, queue_size = 10)    
    nivel = rospy.Publisher('topicoNivel', Int32MultiArray, queue_size=10)
    rospy.Subscriber("topicoPostCondDet", String, atenderAprender)    
    motores = rospy.Publisher('topicoActuarMotores', Float64MultiArray, queue_size=10)
    pubCaminos = rospy.Publisher('topicoCaminos', Int32MultiArray, queue_size=100)
    #rospy.Ssignal.signal(signal.SIGINT, handler)ubscriber("topicoCaminos", Int32MultiArray, atenderCaminos)
   
    rospy.Subscriber("topicoNodoEjecutando", Int32MultiArray, atenderNodoEjecutando)
    
    #rospy.Subscriber("preConditionsSetting", Int32MultiArray, setting)	 
    #rospy.Subscriber("preConditionDetect", Int32MultiArray, evaluarPrecondicion)
    
    
    #event.wait()
    
    
    
    print "inicio master" 
    #comando=raw_input("> ") 
    comando=""
    msg = Int32MultiArray()
    while comando != "salir":
        comando=""
        while comando == "":
            time.sleep(1)
        print "comando ", comando

        if comando=="finDemo":
            finDemo()         
        elif comando=="aprender":
            aprender()
	elif comando=="ejecutar":
	    ejecutar()
	elif comando=="bad":    
	    #posiblemente se realice el algoritmo en vez de 
	    #sobre linkEnEjecucion sobre el grafo general	    
	    aux=ejecutarBad()
	    print  aux
	    
	elif comando=="come":    
	    aux=ejecutarCome()
	    print  aux
	elif comando=="here":
	    aux=ejecutarHere()
	    print  aux
	elif comando=="go": 
	    print "antes de go"
	    aux=ejecutarGo()	    
	    print  aux
	    
	elif comando=="probarGo": 
	    grafoGeneral=[(1,1,3,3,0),(2,2,3,3,0),(3,3,4,4,0),(3,3,5,5,0)]
	    nuevolinks=[(0,6,1,0,0)]
	    cortarGo(nuevolinks,grafoGeneral,3)
	    
	elif comando=="sc": 
	    print separarCaminos()
	elif comando=="topo": 
            linkEnEjecucion=[(0,1,0),(0,2,0),(0,3,0),(1,2,0),(1,3,0),(2,3,0)]
	    print crearTopologia(linkEnEjecucion)   
	    

	elif comando=="lcs":
            lcs.probarLCS()
	elif comando=="lcsPapper":
            lcs.probarLCSPapper()
	elif comando=="pp":   
	    pathAntiguo =[2,3,4]
	    pathNuevo=[3,4]
	    print "compararPath> ",compararPath (pathNuevo,pathAntiguo)
	    
	    topologia=[(2,4),(1,3),(3,4),(1,2),(4,6),(5,1),(7,1),(4,8)]
            #topologia=[(1,2)]
            sucesoresTopologicos=sucesoresTopologicos (topologia)
            print "sucesores: ",sucesoresTopologicos
            caminitos=pathAntecesores(sucesoresTopologicos)    
	    enviarCaminos(caminitos)
	    
	#se puede dar bad cuando se ejecuta 
	elif comando=="algoritmoBad":  
	    linksBad=[(1,1,3,3,0),(2,2,3,3,0),(3,3,4,4,0),(3,3,5,5,0),(5,5,6,6,2)]	
	    salida=borrarNodoBad(linksBad,3)
	    salida=ejecutarBad(linksBad)
	    print salida
	    #msg.data = [0,0] 
	    #estado.publish(msg)
	else:
	    msg.data = [0,1]
            estado.publish(msg)
        #entrada=raw_input("> ")
        
    #rospy.spin()


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
        
    #print "nodo llego postcondicion de tipo orden", ordering

    #se detecta cumplimiento de una postcondicio...entonces el init manda su nivel de activacion para
    #atras...si un nodo recibe y puede ejecutar ejecuta, si no puede manda
    #su nivel para atras y pone su nivel en 0 
    arranqueNivel()
 

def arranqueNivel():
  # print "nivel de activacion init"
    global nivel
    msg = Int32MultiArray()
        
    fin=True
    #para todos los nodos envia el valor para que se inicie el nivel
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
        
'''       
