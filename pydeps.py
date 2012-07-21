import subprocess
import sys
import re

from graph import Node

def find(directory, regex):
    find_cmd = 'find {0} -iname {1}'.format(directory, regex)
    find_proc = subprocess.Popen(find_cmd.split(), stdout=subprocess.PIPE)
    (outd, ind) = find_proc.communicate()
    return outd.split("\n")[:-1]

def normalize_file_name(filename, basename):
    # clean up file name
    filename = filename.replace(basename, '')
    filename = filename[:-3]
    if len(filename) and filename[0] == '/':
        filename = filename[1:]
    return filename.replace('/', '.')

def filter_common(package):
    if package.find('__init__') != -1:
        return False
    if package.find('migrations') != -1:
        return False
    if package.find('test') != -1:
        return False
    return True


def find_first(dep_map, dep_name):
    """ find the first matching dep """
    if dep_name in dep_map.keys():
        return dep_map[dep_name]

    for key in dep_map.keys():
        if key.endswith(dep_name):
            return dep_map[key]

    regex = '(?P<start>[\w\.]+)\.(?P<end>[\w]+)'
    for key in dep_map.keys():
        match = re.match(regex, dep_name)
        if match and key.endswith(match.group('start')):
            return dep_map[key]

    return None


def load_graph(base_dir):
    node_list = {}

    files = find(base_dir, '*.py')

    files = filter(filter_common, files)

    for f in files:
        normalized = normalize_file_name(f, base_dir)
        node = Node(normalized)
        node.filename = f
        node_list[normalized] = node

    print(node_list)

    for node in node_list.values():

        regex = '^from (?P<module>[\w\.]+) import (?P<sub_module>[\w]+)'
        regex2 = '^import (?P<module>[\w]+)$'

        node_file = open(node.filename)
        matches = [re.match(regex, line) for line in node_file if re.match(regex, line)]
        matches += [re.match(regex2, line) for line in node_file if re.match(regex2, line)]

        join = lambda x : '.'.join(x.groups())
        dep_names = map(join, matches)

        
        for dep_name in dep_names:
            if find_first(node_list, dep_name):
                node.add_dep(find_first(node_list, dep_name))

    return node_list

if __name__ == "__main__":
    base_dir = '.'
    if len(sys.argv) == 2:
        base_dir = sys.argv[1]

    print(load_graph(base_dir))
