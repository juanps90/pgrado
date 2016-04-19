#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import Const
import fnmatch
from lxml import etree, builder
import lxml

#	persistirGrafo
#
# 	Esta funcion persiste toda la informacion de una demostracion o la generalizacion de una tarea.
#	El primer parametro es el identificador de la tarea a persistir.
#   El segundo parametro indica que tipo de demostracion esta asociada a este archivo (fullDemo, bad, comeNgo)
#   El tercer parametro determina si es un grafo generalizado (TRUE) o no (FALSE).
#	El cuarto, quinto y sexto  parametro son (respectivamente) el diccionario de nodos y sus tareas asociadas, el grafo topologico (lista) y el grafo de red de componentes (lista).
#	Esta funcion retorna el id del grafo salvado. Este sera 0 para una generaliacion, 1 o mas para una demostracion o -1 si ocurrio algun error.
#	Las 3 listas deben existir, si alguna de ellas fuera None, el procedimiento falla.
#
# 	persistirGrafo(proceso=String, tipo=string, generalizado=Boolean, nodos=DiccionarioNodos, topologia=topologico, networkDef=networkCmp) -> int
#		DiccionarioNodos = {(int:int),...} = {(idNodo:idComportamiento),...}
#		topologico = [(int,int),...] = [(idNodoIni,idNodoFin),...]
#		networkCmp = [(int,int,int),...] = [(idNodoIni,idNodoFin,idTipoLink),...]
#
def persistirGrafo(proceso, tipo, generalizado, DicNodos, DicParametros, ListTopologia, ListNetworkDef):    
    os.environ["pgrado_HOME"] = Const.PGRADO_HOME   
    # Para debug lo imprimo
    #print 'proceso: {0}\ngeneralizado: {1}\nnodos: {2}\nparametros: {3}\ntopologia: {4}\nnetwork: {5}\n'.format(proceso, generalizado, DicNodos, DicParametros, ListTopologia, ListNetworkDef)
    #
    if generalizado:
        # Este va a ser 0 siempre porque es el generalizado
        idGrafo = 0
        tipo = 'Generalizado'
    else:
        # Este va a ser un serial (contando la cantidad de archivos con principio de nombre "proceso"
        idGrafo = len(fnmatch.filter(os.listdir('{0}/{1}'.format(os.getenv('pgrado_HOME', '#N/A'), Const.PERSIT_FOLDER_NAME)), proceso + '_*.xml'))
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
    XMLNodos = definicion(seccion=Const.SECCION_NODOS)
    XMLParams = definicion(seccion=Const.SECCION_PARAMETROS)
    XMLTopologia = definicion(seccion=Const.SECCION_TOPOLOGIA)
    XMLNetwork = definicion(seccion=Const.SECCION_NETWORK)
    #Ahora agrego a cada seccion lo que le corresponde
    for n, c in DicNodos.items():
        XMLNodos.append(nodo(idNodo('{0}'.format(n)), idComportamiento('{0}'.format(c))))
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
        XMLTopologia.append(link_topoligico(IdNodoInicial('{0}'.format(t[0])), IdNodoFinal('{0}'.format(t[1]))))
    for nd in ListNetworkDef:
        XMLNetwork.append(network_link(IdNodoInicial('{0}'.format(nd[0])), IdNodoFinal('{0}'.format(nd[1])), tipoLink('{0}'.format(nd[2]))))
    #
    # Ahora genero el XML Temporal
    DocumentoTMP = grafo(XMLNodos, XMLParams, XMLTopologia, XMLNetwork, proceso='{0}'.format(proceso), idGrafo='{0}'.format(idGrafo), tipo='{0}'.format(tipo))
    # Para debug lo imprimo
    #print lxml.etree.tostring(DocumentoTMP, pretty_print=True, xml_declaration=True, encoding='utf-8')
    # Ahora Salvamos (sobreescribe por defecto)
    DocumentoXML = etree.tostring(DocumentoTMP, pretty_print=True, xml_declaration=True, encoding='utf-8')
    f = open('{0}/{1}/{2}_{3}.xml'.format(os.getenv('pgrado_HOME', '#N/A'), Const.PERSIT_FOLDER_NAME, proceso, idGrafo), "w")    
    f.write(DocumentoXML)
    f.close()
        
#	persistirConfiguracion
#
def persistirConfiguracion(nombreConfiguracion, DiccionarioColores):    
    os.environ["pgrado_HOME"] = Const.PGRADO_HOME   
    # Para debug lo imprimo
    #print 'nombreConfiguracion: {0}\nDiccionarioColores: {1}'.format(nombreConfiguracion, DiccionarioColores)
    #
    # Defino el constructor de elementos y los elementos (tags del XML)
    E = lxml.builder.ElementMaker()
    configuracion = E.configuracion
    calibracion = E.calibracion
    color = E.color
    #colorName = E.colorName
    idColor = E.idColor
    minRGB = E.minRGB
    maxRGB = E.maxRGB
    red = E.red
    green = E.green
    blue = E.blue
    #
    XMLcalibracion = calibracion(seccion=Const.SECCION_COLORES)
    for idC, RGB in DiccionarioColores.items():
        # Creo la nueva entrada de color
        AuxRegistro = color()
        # Le agrego a esa entrada el id del color
        AuxRegistro.append(idColor('{0}'.format(idC)))
        # Agrego ahora los minimos de RGB        
        AuxminRGB = minRGB()                
        AuxminRGB.append(red('{0}'.format(RGB[0][0])))
        AuxminRGB.append(green('{0}'.format(RGB[0][1])))
        AuxminRGB.append(blue('{0}'.format(RGB[0][2])))
        AuxRegistro.append(AuxminRGB)
        # Agrego ahora los maximos de RGB        
        AuxmaxRGB = maxRGB()
        AuxmaxRGB.append(red('{0}'.format(RGB[1][0])))
        AuxmaxRGB.append(green('{0}'.format(RGB[1][1])))
        AuxmaxRGB.append(blue('{0}'.format(RGB[1][2])))
        AuxRegistro.append(AuxmaxRGB)
        # Agrego a la calibracion el color completo            
        XMLcalibracion.append(AuxRegistro)    
    # Ahora genero el XML Temporal (agrego todas las secciones en el orden deseado, por ahora solo calibracion)
    DocumentoTMP = configuracion(XMLcalibracion, nombre='{0}'.format(nombreConfiguracion))
    # Para debug lo imprimo
    #print lxml.etree.tostring(DocumentoTMP, pretty_print=True, xml_declaration=True, encoding='utf-8')
    # Ahora Salvamos (sobreescribe por defecto)
    DocumentoXML = etree.tostring(DocumentoTMP, pretty_print=True, xml_declaration=True, encoding='utf-8')
    f = open('{0}/{1}/{2}.xml'.format(os.getenv('pgrado_HOME', '#N/A'), Const.CONFIG_FOLDER_NAME, nombreConfiguracion), "w")
    f.write(DocumentoXML)
    f.close()

if __name__ == "__main__":
    #
    print 'main de salvar XML'
    n1 = {1:"A", 2:"B", 3:"C"} #nodos
    p1 = {1:{1:[0.167], 2:[0.5, 3.0]}, 2:{1:[0.099], 2:[4.66, 5.3]}, 3:{1:[0.169], 2:[0.75, 6.5]}} #parametros
    t1 = [(1, 2), (2, 3)] #topologia
    k1 = [(1, 2, Const.LINK_PRM), (2, 3, Const.LINK_ORD), (1, 3, Const.LINK_ORD)] #network
    #
    #persistir_Demostracion(sys.argv[1], 'fullDemo', False, n, p, t, k)
    #persistirGrafo(sys.argv[1], 'fullDemo', True, n1, p1, t1, k1)
    #
    c1 ={0:[[1, 1, 1], [1, 1, 1]], 1:[[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]], 
         2:[[0.0, 0.65882354974747, 0.074509806931019], [0.16078431904316, 0.83137255907059, 0.22352941334248]], 
         3:[[0.61960786581039, 0.0, 0.019607843831182], [0.71764707565308, 0.066666670143604, 0.078431375324726]],
         4:[[0.69019609689713, 0.69019609689713, 0.054901961237192], [0.99607843160629, 0.99607843160629, 0.28627452254295]],
         5:[[0.015686275437474, 0.0, 0.67058825492859], [0.2392156869173, 0.2392156869173, 0.87058824300766]], 
         6:[[0.65882354974747, 0.50588238239288, 0.062745101749897], [0.95294117927551, 0.80392158031464, 0.45490196347237]]
         }   
    #persistirConfiguracion(sys.argv[1], c1)
    
