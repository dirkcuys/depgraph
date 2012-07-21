import sys

from circle_graph import draw_circle_graph
from pydeps import load_graph

base_dir = '.'

if len(sys.argv) == 2:
    base_dir = sys.argv[1]

graph = load_graph(base_dir)
print(graph)
draw_circle_graph(graph, 'pycircle')
