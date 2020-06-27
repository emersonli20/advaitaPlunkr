from __future__ import print_function
from ontobio.ontol_factory import OntologyFactory
import obonet
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup, SoupStrainer
import inflect
import math

p = inflect.engine()

html_file = open('templates/cellLocation.html', 'r')
cellLocation = html_file.read()
html_file.close()
soup  = BeautifulSoup(cellLocation,'html.parser')

ofactory = OntologyFactory()
ont = ofactory.create('go')

input_csv = 'melanoma2.csv'
data = pd.read_csv(input_csv)
data = data.to_numpy()

def has_class_but_no_id(tag):
    return tag.has_attr('title')

def get_starting_nodes():
    starting_node_titles = []
    titles = soup.find_all("g", title=True)
    for title in titles:
        temp = str(title)
        a = temp.find("title")
        b = temp.find(">")
        name = temp[a+7:b-1]
        if name[len(name)-3:] == 'ies':
            name = name[:-3]
            name = name + 'y'
        if name[-1] == 's':
            if name[-2] != 'u':
                name = name[:-1]
        if name[-1] == 'i':
            name = name[:-1]
            name = name + 'us'
        if name[-1] == 'a':
            name = name[:-1]
            name = name + 'on'
        if name.lower() not in starting_node_titles:
            starting_node_titles.append(name.lower())
#     print(starting_node_titles)

    graph = obonet.read_obo('go.obo')
    name_to_id = {data['name'].lower(): id_ for id_, data in graph.nodes(data=True) if 'name' in data}
    starting_node_ids = []
    for name in starting_node_titles:
        try:
            starting_node_ids.append(name_to_id[name])
        except:
            starting_node_ids.append(None)

#     print(starting_node_ids)

    starting_node_titles_np = np.array(starting_node_titles)[np.newaxis]
    starting_node_ids_np = np.array(starting_node_ids)[np.newaxis]

    starting_nodes = np.concatenate((starting_node_titles_np.T, starting_node_ids_np.T),axis=1)
#     print(starting_nodes)
#     print(starting_nodes.shape)
    return starting_nodes, starting_node_titles, starting_node_ids

def bfs(source):
    explored = []
    queue = [source]
    while queue:
        node = queue.pop(0)
        # what if the starting node is None? then ont.children(source) returns nothing
        if node not in explored:
            explored.append(node)
            children = ont.children(source)
            queue.extend(children)
    return explored


def min_pval(nodes):
    pvals = []
    for node in nodes:
        for i in range(len(data[:,0])):
            if node == data[i,0]:
                pvals.append(data[i,4])
    if not pvals:
        return None
    else:
        return min(pvals)


def get_pvals():
    pvals = []
    for node in starting_node_ids:
        pvals.append(min_pval(bfs(node)))
    return pvals


def log_arr(arr, base):
    res = [-math.log(x, base) if x is not None else None for x in arr]
    return [x for x in res if x is not None] # removes None values

def set_comp_color(comp, row, base, mx):
    # strainer = SoupStrainer('g', title=comp)
    #strainer = SoupStrainer('g', attrs={'title': lambda x: x and x.lower()==comp})
    strainer = SoupStrainer('g', attrs={'title': lambda x: x and (modded_singularize(x).lower()==comp
                                       if modded_singularize(x) else x.lower()==comp)})
    comp_soup = BeautifulSoup(cellLocation, 'html.parser', parse_only=strainer)
    paths = comp_soup.find_all('path', style=True)
    new_paths = ''
    for path in paths:
        pval_input = plunker_inputs[row,2]
        rgb = log_pval_to_rgb(pval_input, mx, base) # experiment with different bases and scales
        temp = str(path)
        a = temp.find('style')
        temp = ''.join((temp[:a+13], rgb, temp[a+19:]))
        new_paths += temp
    return new_paths

def new_html(base=10):
    mx = max(log_arr(final_pvals, base))
    print()
    print('max -log(pval): ' + str(mx))
    print('scale = ' + str(255/mx))
    new_file = ''
    for i in range(plunker_inputs.shape[0]):
        new_file += set_comp_color(plunker_inputs[i,0], i, base, mx)

    paths_only_soup = BeautifulSoup(new_file, 'html.parser')
    # paths_only_soup_str = str(paths_only_soup)
    old_paths = soup.find_all('path', style=True)
    new_paths = paths_only_soup.find_all('path', style=True) # new_paths has the new rgb values

    for i in range(len(new_paths)):
        old_paths[i].replace_with(new_paths[i])

    target = soup.find_all(text="Max")
    for v in target:
        v.replace_with(str(round(mx,2)))

    titles = soup.find_all("g", title=True)
    idx = 0
    while idx < len(titles):
        if final_pvals[int(idx/2)] is None:
            final_pvals[int(idx / 2)] = 0
        titles[idx]['key'] = round(final_pvals[int(idx/2)], 6)
        idx = idx + 1

    return str(soup)


def pval_to_rgb(pval):
    r_str = 'ff'
    if np.isnan(pval):
        return r_str*3
    g = int(round(pval*255))
    b = int(round(pval*255))
    g_str = format(g,'x')
    if len(g_str) < 2:
        g_str = '0' + g_str
    b_str = format(b,'x')
    if len(b_str) < 2:
        b_str = '0' + b_str
    rgb = r_str + g_str + b_str
    return rgb

def log_pval_to_rgb(pval, mx, base):
    # make it cyan to magenta
    # cyan: 00FFFF
    # magenta: FF00FF
    # as y increases, r increases, g decreases
    b_str = 'ff'
    if np.isnan(pval):
        return 'ffffff'
    x = -math.log(pval, base)

    scale = 255 / mx
    y = int(round(x*scale))
    r = y
    g = 255 - y

    r_str = format(r,'x')
    if len(r_str) < 2:
        r_str = '0' + r_str

    g_str = format(g,'x')
    if len(g_str) < 2:
        g_str = '0' + g_str

    rgb = r_str + g_str + b_str
    return rgb

def modded_singularize(word):
    word = word
#     if ' and ' in word:
#         x = word.split(' and ')
    if word[-2:] == 'ia':
        word = word[:-2] + 'ion'
        return word
    return p.singular_noun(word)


starting_nodes, starting_node_titles, starting_node_ids = get_starting_nodes()

final_pvals = get_pvals()
print(final_pvals)

final_pvals_np = np.array(final_pvals)[np.newaxis]
final = np.concatenate((starting_nodes, final_pvals_np.T), axis=1)

final_dataset = pd.DataFrame({'Title': final[:,0], 'ID': final[:,1], 'pval': final[:,2]})

final_table_name = 'to_plunker_' + input_csv
final_dataset.to_csv(final_table_name, index=False)
print(pd.read_csv(final_table_name))

df = pd.read_csv(final_table_name)
plunker_inputs = df.to_numpy()

new_cellLocation = new_html()
new_html_name = 'new_cellLocation_' + input_csv[:-4] + '.html'

file = open(new_html_name, 'w')
file.write(new_cellLocation)
file.close()
