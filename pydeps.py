import subprocess
import sys
import re

from graph import Node

excludes = [
    'os',
    'subprocess',
    'logging',
    're',
    'datetime'
]

def find(directory, regex):
    find_cmd = 'find {0} -iname {1}'.format(directory, regex)
    find_proc = subprocess.Popen(find_cmd.split(), stdout=subprocess.PIPE)
    (outd, ind) = find_proc.communicate()
    return outd.split("\n")[:-1]

def normalize_file_name(filename):
    # clean up file name
    filename = filename.replace(base_dir, '')
    filename = filename[:-3]
    if len(filename) and filename[0] == '/':
        filename = filename[1:]
    return filename.replace('/', '.')

def filter_common(package):
    if package.find('django') != -1:
        return False
    return True

def find_first(dep_map, dep_name):
    if dep_name in dep_map.keys():
        return dep_map[dep_name]
    for key in dep_map.keys():
        if key.endswith(dep_name):
            return dep_map[key]
    regex = '(?P<start>[\w\.]+)\.(?P<end>[\w]+)'
    for key in dep_map.keys():
        match = re.match(regex, key)
        if match and key.endswith(match.group(0)):
            return dep_map[key]
    return None

def load_graph(base_dir):
    node_list = {}

    files = find(base_dir, '*.py')

    for f in files:
        normalized = normalize_file_name(f)
        node = Node(normalized)
        node.filename = f
        node_list[f] = node

    for node in node_list.values():

        regex = '^from (?P<module>[\w\.]+) import (?P<sub_module>[\w]+)'
        regex2 = '^import (?P<module>[\w]+)$'

        node_file = open(node.filename)
        matches = [re.match(regex, line) for line in node_file if re.match(regex, line)]
        matches += [re.match(regex2, line) for line in node_file if re.match(regex2, line)]

        join = lambda x : '.'.join(x.groups())
        dep_names = map(join, matches)

        dep_names = filter(filter_common, dep_names)
        
        deps = []
        for dep_name in dep_names:
            if find_first(node_list, dep_name):
                deps += [find_first(node_list, dep_name)]


        print(node.name)
        print(deps)

    # build graph
    return node_list

if __name__ == "__main__":
    base_dir = '.'
    if len(sys.argv) == 2:
        base_dir = sys.argv[1]

    load_graph(base_dir)
