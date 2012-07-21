# A very simple directed graph

class Node:

    stack = []
    
    def __init__(self, name):
        self.name = name
        self.dependancies = set()
        #self.position = (0.0, 0.0)
        self.cache = 0
        self.rdeps = set()
        
    def add_dep(self, dep):
        self.dependancies.add(dep)
        dep._add_reverse_dep(self)
        
    def _add_reverse_dep(self, rdep):
        self.rdeps.add(rdep)
        
    def __str__(self):
        return '{0} [{1}]'.format(self.name, ','.join([dep.name for dep in self.dependancies]))

    def __unicode__(self):
        return self.__str__()

class Graph:
    def __init__(self):
        self.packageDict = dict()

    def add_node(self, node, parent=None):
        self.nodes[node] = node
        if parent:
            parent.add_dep(node)

