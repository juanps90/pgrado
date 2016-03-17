#!/usr/bin/env python

import sys
import os
import constPersist
from lxml import etree, objectify
import lxml.etree
import lxml.builder
import fnmatch

#   obtener_definicion
#
# 	Esta funcion devuelve toda la generalizacion de una tarea (identificada por el nombre "proceso")
#
# 	obtener_definicion(proceso=String, idGrafo=int) -> [errores, DiccionarioNodos, DiccionarioParams, topologico, networkCmp]
#       errores = cantidad de errores encontrados (0 todo OK)
#		DiccionarioNodos = {int:string,...} = {idNodo:idComportamiento,...} 
#       DiccionarioParams = {int:{int:[float32,...]},...} = {idNodo:{idSensor:[valorParam,...]},...}
#		topologico = [(int,int),...] = [(idNodoIni,idNodoFin),...]
#		networkCmp = [(int,int,int),...] = [(idNodoIni,idNodoFin,idTipoLink),...]
#
def obtener_definicion(proceso):
    errores = 0
    nodos = {}
    parametros = {}
    topologia = []
    networkDef = []    
    nombre = r'{0}_0.xml'.format(proceso)
    if len(fnmatch.filter(os.listdir('.'), '{0}_0.xml'.format(proceso))) == 0:
        print 'No se encuentra una generalizacion para la tarea "{0}".'.format(proceso)
        errores += 1
    else:        
        with open(nombre) as f:
            xml = f.read()
        root = objectify.fromstring(xml)
        for definicion in root.getchildren():
            if definicion.get("seccion") == constPersist.SECCION_NODOS:
                for nodo in definicion.getchildren():
                    aux = [ data.text for data in nodo.iterchildren() ]
                    nodos[int(aux[0])] = aux[1]
            elif definicion.get("seccion") == constPersist.SECCION_PARAMETROS:
                for r in definicion.getchildren():
                    idNodo = int(r.idNodo.text)
                    params = {}
                    for s in r.sensor:
                        idSensor = int(s.idSensor.text)
                        aux = [ float(d.text) for d in s.Parametros.iterchildren() ] 
                        params[idSensor] = aux
                    parametros[idNodo] = params   
            elif definicion.get("seccion") == constPersist.SECCION_TOPOLOGIA:
                for linkT in definicion.getchildren():
                    aux = [ data.text for data in linkT.iterchildren() ]              
                    topologia.append( (int(aux[0]), int(aux[1])) )
            elif definicion.get("seccion") == constPersist.SECCION_NETWORK:           
                for linkNL in definicion.getchildren():
                    aux = [ data.text for data in linkNL.iterchildren() ]              
                    networkDef.append( (int(aux[0]), int(aux[1]), int(aux[2])) )
            else:
                print 'Seccion no esperada {0}'.format( definicion.get("seccion"))
                errores += 1
    # Retorno
    return [errores, nodos, parametros, topologia, networkDef]

if __name__ == "__main__":
    #
    resultado = obtener_definicion(sys.argv[1])
    print 'errores: {0}'.format(resultado[0])
    print 'nodos: {0}'.format(resultado[1])
    print 'parametros: {0}'.format(resultado[2])
    print 'topologico: {0}'.format(resultado[3])
    print 'network: {0}'.format(resultado[4])
    #
