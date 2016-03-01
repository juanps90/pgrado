from node import Node
class Aux:
    
    def sampleGraph1(self):
        # ABDFG
        
        nA = Node()
        nA.letra = 'A'
        
        nB = Node()
        nB.letra = 'B'
        
        nC = Node()
        nC.letra = 'C'
        
        nD = Node()
        nD.letra = 'D'
        
        nE = Node()
        nE.letra = 'E'
        
       
        nINIT = Node()
        
        nINIT.parentNodes = [nE]
        nE.parentNodes = [nD]
        nD.parentNodes = [nB, nC]
        nC.parentNodes = [nA]
        nB.parentNodes = [nA]
        
        
        # -- network --
        nA.networkNodes = [nD, nE, nINIT]
        nA.networkTypes = [Node.LINK_ORD, Node.LINK_ORD, Node.LINK_ORD]
        
        nB.networkNodes = [nE, nINIT]
        nB.networkTypes = [Node.LINK_ORD, Node.LINK_ORD]
        
        nC.networkNodes = [nE, nINIT]
        nC.networkTypes = [Node.LINK_ORD, Node.LINK_ORD]
        
        nD.networkNodes = [nINIT]
        nD.networkTypes = [Node.LINK_ORD]
        
        # --- 
        
        nINIT.parentTypes = [Node.LINK_ORD]
        nE.parentTypes = [Node.LINK_ORD]
        nD.parentTypes = [Node.LINK_ORD, Node.LINK_ORD]
        nC.parentTypes = [Node.LINK_ORD]
        nB.parentTypes = [Node.LINK_ORD]
        
        
        # Enlaces reversos
        nE.childNodes = [nINIT]
        nD.childNodes = [nE]
        nC.childNodes = [nD]
        nB.childNodes = [nD]
        nA.childNodes = [nB, nC]
        
        
        
        return nINIT
        
    def sampleGraph2(self):
        
        nA = Node()
        nA.letra = 'A'
        
      
        nK = Node()
        nK.letra = 'K'
        
        nD = Node()
        nD.letra = 'D'
        
        nE = Node()
        nE.letra = 'E'
       
        nINIT = Node()
        

        nINIT.parentNodes = [nE]
        nE.parentNodes = [nD]
        nD.parentNodes = [nK]
        nK.parentNodes = [nA]
        
        
        # -- network --
        nA.networkNodes = [nD, nE, nINIT]
        nA.networkTypes = [Node.LINK_ORD,Node.LINK_ORD,Node.LINK_ORD]
        
        nK.networkNodes = [nE, nINIT]
        nK.networkTypes = [Node.LINK_ORD,Node.LINK_ORD]
        
        nD.networkNodes = [nINIT]
        nD.networkTypes = [Node.LINK_ORD]
        # -- 
        
        
        nINIT.parentTypes = [Node.LINK_ORD]
        nE.parentTypes = [Node.LINK_ORD]
        nD.parentTypes = [Node.LINK_ORD]
        nK.parentTypes = [Node.LINK_ORD]
        
        return nINIT
        
    def sampleGraph3(self):
        
        nA = Node()
        nA.letra = 'R'
        
      
        nK = Node()
        nK.letra = 'K'
        
        nD = Node()
        nD.letra = 'D'
        
        nE = Node()
        nE.letra = 'E'
       
        nINIT = Node()
        

        nINIT.parentNodes = [nE]
        nE.parentNodes = [nD]
        nD.parentNodes = [nK]
        nK.parentNodes = [nA]
        
        # -- network --
        nA.networkNodes = [nD, nE, nINIT]
        nA.networkTypes = [Node.LINK_ORD,Node.LINK_ORD,Node.LINK_ORD]
        
        nK.networkNodes = [nD, nINIT]
        nK.networkTypes = [Node.LINK_ORD,Node.LINK_ORD]
        
        nD.networkNodes = [nINIT]
        nD.networkTypes = [Node.LINK_ORD]
        # -- 
        
        nINIT.parentTypes = [Node.LINK_ORD]
        nE.parentTypes = [Node.LINK_ORD]
        nD.parentTypes = [Node.LINK_ORD]
        nK.parentTypes = [Node.LINK_ORD]
        
        return nINIT
        
    def sampleGraph4(self):
        
        nX = Node()
        nX.letra = 'X'
        
      
        nY = Node()
        nY.letra = 'Y'
        
        nZ = Node()
        nZ.letra = 'Z'
        
        nINIT = Node()
        

        nINIT.parentNodes = [nZ]
        nZ.parentNodes = [nY]
        nY.parentNodes = [nX]
        
        nX.networkNodes = [nZ, nINIT]
        nX.networkTypes = [Node.LINK_ORD, Node.LINK_ORD]
        
        nY.networkTypes = [Node.LINK_ORD]
        nY.networkNodes = [nINIT]
        
        
        
        nINIT.parentTypes = [Node.LINK_ORD]
        nZ.parentTypes = [Node.LINK_ORD]
        nY.parentTypes = [Node.LINK_ORD]
        
        nX.childNodes = [nY]
        nY.childNodes = [nZ]
        nZ.childNodes = [nINIT]
        
        
        return nINIT
