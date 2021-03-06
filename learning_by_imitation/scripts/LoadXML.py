#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# @package LoadXML
# @brief ----
# @details ----
# @authors Gustavo Irigoyen
# @authors Juan Pablo Sierra
# @authors Juan Eliel Ibarra
# @authors Gustavo Evovlockas
# @date Abril 2016
#

import os
import Const
from lxml import etree, objectify, builder
import fnmatch

#   obtener_definicion
#
# 	Esta funcion devuelve toda la generalizacion de una tarea (identificada por el nombre "proceso")
#
# 	obtener_definicion(proceso=String, idGrafo=int) -> [errores, DiccionarioNodos, DiccionarioParams, topologico, networkCmp]
#          errores = cantidad de errores encontrados (0 todo OK)
#		DiccionarioNodos = {int:string,...} = {idNodo:idComportamiento,...} 
#          DiccionarioParams = {int:{int:[float32,...]},...} = {idNodo:{idSensor:[valorParam,...]},...}
#		topologico = [(int,int),...] = [(idNodoIni,idNodoFin),...]
#		networkCmp = [(int,int,int),...] = [(idNodoIni,idNodoFin,idTipoLink),...]
#
def obtenerGrafo(proceso):    
    os.environ["pgrado_HOME"] = Const.PGRADO_HOME   
    #
    errores = 0
    nodos = {}
    parametros = {}
    topologia = []
    networkDef = []    
    if len(fnmatch.filter(os.listdir('{0}/{1}'.format(os.getenv('pgrado_HOME', '#N/A'), Const.PERSIT_FOLDER_NAME)), '{0}_0.xml'.format(proceso))) == 0:
        print 'No se encuentra una generalizacion para la tarea "{0}".'.format(proceso)
        errores += 1
    else:                
        nombre = '{0}/{1}/{2}_0.xml'.format(os.getenv('pgrado_HOME', '#N/A'), Const.PERSIT_FOLDER_NAME, proceso)
        with open(nombre) as f:
            xml = f.read()
            f.close()
        root = objectify.fromstring(xml)
        for definicion in root.getchildren():
            if definicion.get("seccion") == Const.SECCION_NODOS:
                for nodo in definicion.getchildren():
                    aux = [ data.text for data in nodo.iterchildren() ]
                    nodos[int(aux[0])] = aux[1]
            elif definicion.get("seccion") == Const.SECCION_PARAMETROS:
                for r in definicion.getchildren():
                    idNodo = int(r.idNodo.text)
                    params = {}
                    print 'idNodo: ', idNodo, ' - Tiene sensor: ', r.find("sensor")
                    if r.find("sensor") != None:
                        # Si tiene sensores asociados (puede no tener!)                        
                        for s in r.sensor:
                            idSensor = int(s.idSensor.text)
                            aux = [ float(d.text) for d in s.Parametros.iterchildren() ] 
                            params[idSensor] = aux
                    parametros[idNodo] = params   
            elif definicion.get("seccion") == Const.SECCION_TOPOLOGIA:
                for linkT in definicion.getchildren():
                    aux = [ data.text for data in linkT.iterchildren() ]              
                    topologia.append( (int(aux[0]), int(aux[1])) )
            elif definicion.get("seccion") == Const.SECCION_NETWORK:           
                for linkNL in definicion.getchildren():
                    aux = [ data.text for data in linkNL.iterchildren() ]              
                    networkDef.append( (int(aux[0]), int(aux[1]), int(aux[2])) )
            else:
                print 'Seccion no esperada {0}'.format( definicion.get("seccion"))
                errores += 1
    # Retorno
    return [errores, nodos, parametros, topologia, networkDef]

#   obtener_definicion
#
def obtenerConfiguracion(nombreConfiguracion):    
    os.environ["pgrado_HOME"] = Const.PGRADO_HOME   
    errores = 0
    colores = {}    
    if len(fnmatch.filter(os.listdir('{0}/{1}'.format(os.getenv('pgrado_HOME', '#N/A'), Const.CONFIG_FOLDER_NAME)), '{0}.xml'.format(nombreConfiguracion))) == 0:
        print 'No se encuentra la calibracion solicitada ("{0}").'.format(nombreConfiguracion)
        errores += 1
    else:      
        nombre = '{0}/{1}/{2}.xml'.format(os.getenv('pgrado_HOME', '#N/A'), Const.CONFIG_FOLDER_NAME, nombreConfiguracion)
        with open(nombre) as f:
            xml = f.read()
            f.close()
        root = objectify.fromstring(xml)
        for seccion in root.getchildren():
            if seccion.get("seccion") == Const.SECCION_COLORES:
                for c in seccion.getchildren():
                    idColor = int(c.idColor.text)
                    RGB = [[ float(rgb.text) for rgb in c.minRGB.iterchildren() ], [ float(rgb.text) for rgb in c.maxRGB.iterchildren() ]]                    
                    colores[idColor] = RGB
            else:
                print 'Seccion no esperada {0}'.format( seccion.get("seccion"))
                errores += 1
    #
    return [errores, colores]
    
if __name__ == "__main__":
    print 'MAIN de cargar xml'
    #
    #resultado = obtenerConfiguracion(sys.argv[1])
    #print 'errores: {0}'.format(resultado[0])
    #print 'colores: {0}'.format(resultado[1])
    #resultado = obtenerGrafo(sys.argv[1])
#    print 'errores: {0}'.format(resultado[0])
#    print 'nodos: {0}'.format(resultado[1])
#    print 'parametros: {0}'.format(resultado[2])
#    print 'topologico: {0}'.format(resultado[3])
#    print 'network: {0}'.format(resultado[4])
    #
