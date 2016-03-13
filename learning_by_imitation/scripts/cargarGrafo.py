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
# 	obtener_definicion(proceso=String, idGrafo=int) -> [errores, listaNodos, topologico, networkCmp]
#       errores = cantidad de errores encontrados
#		listaNodos = [(int,int),(int,int),...,(int,int)]
#		topologico = [(int,int),(int,int),...,(int,int)]
#		networkCmp = [(int,int,int),(int,int,int),...,(int,int,int)]
#
def obtener_definicion(proceso):
    errores = 0
    nodos = []
    topologia = []
    networkDef = []    
    nombre = r'{0}_0.xml'.format(proceso)
    if len(fnmatch.filter(os.listdir('.'), '{0}_0.xml'.format(proceso))) == 0:
        print 'No se encuentra una generalizacion para la tarea "{0}".'.format(proceso)
        errores += errores
    else:        
        with open(nombre) as f:
            xml = f.read()
        root = objectify.fromstring(xml)
        for definicion in root.getchildren():
            seccion = definicion.get("seccion")
            for e in definicion.getchildren():
                if seccion == constPersist.SECCION_NODOS:
                    nodos.append( [ int(data.text) for data in e.iterchildren() ] )
                elif seccion == constPersist.SECCION_TOPOLOGIA:
                    topologia.append( [ int(data.text) for data in e.iterchildren() ] )                
                elif seccion == constPersist.SECCION_NETWORK:
                    networkDef.append( [ int(data.text) for data in e.iterchildren() ] )                
                else:
                    print '{0}: {1}'.format( seccion , [ int(data.text) for data in e.iterchildren() ] )
                    errores += errores
    # Retorno
    return [errores, nodos,topologia,networkDef]

if __name__ == "__main__":
    resultado = obtener_definicion(sys.argv[1])
    print 'errores: {0}'.format(resultado[0])
    print 'nodos: {0}'.format(resultado[1])
    print 'topologico: {0}'.format(resultado[2])
    print 'network: {0}'.format(resultado[3])

