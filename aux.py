from node import Node
class Aux:
    
    def sampleGraph1(self):
        # ABDFG
        
        nA = Node()
        nA.letra = 'A'
        
        nB = Node()
        nB.letra = 'B'
        
        nD = Node()
        nD.letra = 'D'
        
       
        nINIT = Node()
        
        nINIT.parentNodes = [nA, nB, nD]
        nINIT.parentTypes  = {nA: Node.LINK_ORD, nB: Node.LINK_ORD, nD: Node.LINK_ORD}
        nD.parentNodes    = [nA, nB]
        nD.parentTypes  = {nA:Node.LINK_ORD,nB: Node.LINK_ENA}
        nB.parentNodes    = [nA]
        nB.parentTypes  = {nA:Node.LINK_PRM}
        nA.parentNodes    = []
        
        return nINIT
        
    def sampleGraph2(self):
        nA = Node()
        nA.letra = 'A'
        
        nB = Node()
        nB.letra = 'C'
        
        nC = Node()
        nC.letra = 'D'
      
        nINIT = Node()
        
        nINIT.parentNodes = [nA, nB, nC]
        nINIT.parentTypes  = {nA: Node.LINK_ORD,nB: Node.LINK_ORD, nC: Node.LINK_ORD}
        nC.parentNodes    = [nA, nB]
        nC.parentTypes  = {nA: Node.LINK_ORD,nB: Node.LINK_ORD}
        nB.parentNodes    = [nA]
        nB.parentTypes  = {nA: Node.LINK_ORD}
        nA.parentNodes    = []

        
        return nINIT
        
