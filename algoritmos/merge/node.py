class LinkPoint:
    def __init__(self, node):
        self.thisNode =  node # Referencias al nodo padre
        self.score = 0
		
        self.lpoint = None
        self.ltype  = None
        
        self.length = 0 # largo del camino
        
		# ------ Datos para calculos de valores --------
        self.values = None
        self.samePrefix = None
		
		# Indica el nodo al que apunta cuando se esta haciendo el algoritmo de similitud
		# O sea el mas parecido
        self.refNode = None
        # Indica la posicion a la que se hace referencia
		# Es necesario indicarla porque cuando se cambia de nodo pueden pasar dos cosas
		# 1- Es una diagonal, entonces hay que referenciar la celda anterior
		# 2- Es un avance vertical, entonces se mantiene el mismo indice de celda
		# A priori, no es posible determinarlo dado que se sabe que hay un cambio vertical
        self.refNodePos = None
        
        node.n.append(self)

#class LinkNodo:
#	def __init__(self, ltype, lnode):
#		self.ltype =  ltype
#        self.lnode = lnode



class Node:
    """Representa un nodo"""
    LINK_ORD=1
    LINK_ENA=2
    LINK_PRM=3
    
    def __init__(self):
        # ------ Datos de la estructura ------------
        self.letra = None
        self.n = [] # LinkPoint()
        # extraLinks
	
    def run(self, conds):
        print "RUN iracolor"
        
