#!/usr/bin/env python

import sys
import os
import Const
import fnmatch
from lxml import etree
import lxml.etree
import lxml.builder

#	persistir_Demostracion
#
# 	Esta funcion persiste toda la informacion de una demostracion o la generalizacion de una tarea.
#	El primer parametro es el identificador de la tarea a persistir. 
#   El segundo parametro indica que tipo de demostracion esta asociada a este archivo (fullDemo, bad, comeNgo)
#   El tercer parametro determina si es un grafo generalizado (TRUE) o no (FALSE).
#	El cuarto, quinto y sexto  parametro son (respectivamente) el diccionario de nodos y sus tareas asociadas, el grafo topologico (lista) y el grafo de red de componentes (lista).
#	Esta funcion retorna el id del grafo salvado. Este sera 0 para una generaliacion, 1 o mas para una demostracion o -1 si ocurrio algun error.
#	Las 3 listas deben existir, si alguna de ellas fuera None, el procedimiento falla.
#
# 	persistir_Demostracion(proceso=String, tipo=string, generalizado=Boolean, nodos=DiccionarioNodos, topologia=topologico, networkDef=networkCmp) -> int
#		DiccionarioNodos = {(int:int),...} = {(idNodo:idComportamiento),...} 
#		topologico = [(int,int),...] = [(idNodoIni,idNodoFin),...]
#		networkCmp = [(int,int,int),...] = [(idNodoIni,idNodoFin,idTipoLink),...]
#
def persistir_Demostracion(proceso, tipo, generalizado, DicNodos, DicParametros, ListTopologia, ListNetworkDef):
    print('proceso: {0}\ngeneralizado: {1}\nnodos: {2}\nparametros: {3}\ntopologia: {4}\nnetwork: {5}\n'.format(proceso, generalizado, DicNodos, DicParametros, ListTopologia, ListNetworkDef))
    if generalizado:
        # Este va a ser 0 siempre porque es el generalizado
        idGrafo = 0
        tipo = 'Generalizado'
    else:
        # Este va a ser un serial (contando la cantidad de archivos con principio de nombre "proceso"
        idGrafo = len(fnmatch.filter(os.listdir('.'), proceso + '_*.xml')) 
        if idGrafo == 0:
            idGrafo += 1
    #
    # Defino el constructor de elementos y los elementos (tags del XML)
    E = lxml.builder.ElementMaker()
    grafo = E.grafo
    definicion = E.definicion
    nodo = E.nodo
    idNodo = E.idNodo
    idComportamiento = E.idComportamiento
    registro = E.registro
    sensor = E.sensor
    idSensor = E.idSensor
    parametros = E.Parametros
    data = E.data        
    network_link = E.network_link
    link_topoligico = E.link_topoligico
    IdNodoInicial = E.IdNodoInicial
    IdNodoFinal = E.IdNodoFinal    
    tipoLink = E.tipoLink
    # Creo las secciones basicas (sin contenido en principio)
    XMLNodos = definicion(seccion = Const.SECCION_NODOS)
    XMLParams = definicion(seccion = Const.SECCION_PARAMETROS)
    XMLTopologia = definicion(seccion = Const.SECCION_TOPOLOGIA)
    XMLNetwork = definicion(seccion = Const.SECCION_NETWORK)
    #Ahora agrego a cada seccion lo que le corresponde
    for n, c in DicNodos.items():     
        XMLNodos.append(nodo(idNodo('{0}'.format(n)),idComportamiento('{0}'.format(c))))    
    for n, p in DicParametros.items():
        AuxRegistro = registro()
        AuxRegistro.append((idNodo('{0}'.format(n))))        
        for s, v in p.items():
            AuxSensor = sensor()
            AuxSensor.append(idSensor('{0}'.format(s)))
            AUXParams = parametros()
            for d in v:
                AUXParams.append(data('{0}'.format(d)))
            AuxSensor.append(AUXParams)
            AuxRegistro.append(AuxSensor)
        XMLParams.append(AuxRegistro)
    for t in ListTopologia:
        XMLTopologia.append(link_topoligico(IdNodoInicial('{0}'.format(t[0])),IdNodoFinal('{0}'.format(t[1]))))    
    for nd in ListNetworkDef:
        XMLNetwork.append(network_link(IdNodoInicial('{0}'.format(nd[0])),IdNodoFinal('{0}'.format(nd[1])),tipoLink('{0}'.format(nd[2]))))
    #
    # Ahora genero el XML Temporal
    DocumentoTMP = grafo(XMLNodos, XMLParams, XMLTopologia, XMLNetwork, proceso='{0}'.format(proceso), idGrafo='{0}'.format(idGrafo), tipo='{0}'.format(tipo))
    # Para debug lo imprimo
    #print lxml.etree.tostring(DocumentoTMP, pretty_print=True, xml_declaration=True, encoding='utf-8')
    # Ahora Salvamos (sobreescribe por defecto)
    DocumentoXML = etree.tostring(DocumentoTMP, pretty_print=True, xml_declaration=True, encoding='utf-8')
    with open('{0}_{1}.xml'.format(proceso, idGrafo), "w") as f:
        f.write(DocumentoXML)    

if __name__ == "__main__":
    #
    n = {1:"A",2:"B",3:"C"} #nodos    
    p = {1:{1:[0.167],2:[0.5,3.0]},2:{1:[0.099],2:[4.66,5.3]},3:{1:[0.169],2:[0.75,6.5]}} #parametros
    t = [(1,2),(2,3)] #topologia
    k = [(1,2,Const.LINK_PRM),(2,3,Const.LINK_ORD),(1,3,Const.LINK_ORD)] #network
    #
    #persistir_Demostracion(sys.argv[1], 'fullDemo', False, n, p, t, k)
    persistir_Demostracion(sys.argv[1], 'fullDemo', True, n, p, t, k)
    #    
