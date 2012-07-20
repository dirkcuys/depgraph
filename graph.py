# A very simple directed graph

class Node:

    stack = []
    
    def __init__(self, name):
        self.name = name
        self.dependancies = set()
        self.position = (0.0, 0.0)
        self.cache = 0
        self.rdeps = set()
        
    def add_dep(self, dep):
        self.dependancies.add(dep)
        dep.add_reverse_dep(self)
        
    def add_reverse_dep(self, rdep):
        self.rdeps.add(rdep)
        
    def calc_level(self):
        if self.name in Package.stack:
            print('Circular dependancy caused by {0}. Stack: {1}'.format(self.name, ','.join([package for package in Package.stack])))
            return 0
            
        if self.cache > 0:
            return self.cache
            
        Package.stack.append(self.name)
        #print('{0}.calcLevel() : callStack = {1}'.format(self.name, stack))
        max = 0
        for dep in self.dependancies:
            depLevel = dep.calcLevel()
            if depLevel > max:
                max = depLevel
        self.cache = max + 1
        Package.stack.pop()
        return self.cache
        
    def __str__(self):
        return '{0} [{1}]'.format(self.name, ','.join([dep.name for dep in self.dependancies]))

class Graph:
    def __init__(self):
        self.packageDict = dict()

    def add_node(self, node, parent=None):
        self.nodes[node] = node
        if parent:
            parent.add_dep(node)

