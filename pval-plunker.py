from __future__ import print_function
from ontobio.ontol_factory import OntologyFactory

import obonet

import pandas as pd
import numpy as np

from bs4 import BeautifulSoup, SoupStrainer
import inflect
import math
import json
import simplejson

p = inflect.engine()

input_csv = 'breast_cancer_sig.csv'
data = pd.read_csv(input_csv)
data = data.to_numpy()

html_file = open('templates/cellLocation.html', 'r')
cellLocation = html_file.read()
html_file.close()
soup  = BeautifulSoup(cellLocation,'html.parser') 

ofactory = OntologyFactory()
ont = ofactory.create('go.json')

def has_class_but_no_id(tag):
    return tag.has_attr('title')

def get_starting_nodes():
    node_titles = []
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
        if name.lower() not in node_titles:
            node_titles.append(name.lower())
#     print(starting_node_titles)

    graph = obonet.read_obo('go.obo')
    name_to_id = {data['name'].lower(): id_ for id_, data in graph.nodes(data=True) if 'name' in data}
    node_ids = []
    for name in node_titles:
        try:
            node_ids.append(name_to_id[name])
        except:
            node_ids.append(None)

    node_titles_np = np.array(node_titles)[np.newaxis]
    node_ids_np = np.array(node_ids)[np.newaxis]

    nodes = np.concatenate((node_titles_np.T, node_ids_np.T),axis=1)

    return nodes, node_titles, node_ids

def bfs(source):
    explored = []
    queue = [source]
    while queue:
        node = queue.pop(0)
        # what if the starting node is None? then ont.children(source) returns nothing
        if node not in explored:
            explored.append(node)
            children = ont.children(node)
            queue.extend(children)
    return explored


def bfs_with_depth(source):
    level = 0
    depths = []
    explored = []
    queue = [source]
    while queue:
        level_size = len(queue)
        while level_size > 0:
            node = queue.pop(0)
            if node not in explored:
                explored.append(node)
                depths.append(level)
                children = ont.children(node)
                queue.extend(children)
            level_size -= 1
        level += 1
    res = np.concatenate(((np.array(explored, dtype='object')[np.newaxis]).T, (np.array(depths)[np.newaxis]).T),
                         axis=1)
    return res

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


def get_pvals_and_children_with_depth():
    pvals = np.empty([len(starting_node_ids), 4], dtype='object')
    for i in range(len(starting_node_ids)):
        node = starting_node_ids[i]
        res = bfs_with_depth(node)
        
        pvals[i,0] = min_pval(res[:,0])
        for j in range(len(data[:,0])):
            if node == data[j,0]:
                pvals[i,1] = data[j,4]
                break
                
        d = get_graph(node)
        d = goid_to_label_and_pval(d)
        d_str = "\n".join(("{}: {}".format(*j) for j in d.items()))
        pvals[i,3] = d_str
        
        non_represented_res = [x for x in res[:,0] if x not in starting_node_ids]
        pvals[i,2] = min_pval(non_represented_res)
        
    return pvals

def get_graph(node):
    res = bfs_with_depth(node)
    graph = {}
    for i in range(np.amax(res[:,1]) + 1):
        graph['level ' + str(i)] = [x for ind, x in np.ndenumerate(res[:,0]) 
                                    if res[ind[0],1] == i] 
    return graph

def goid_to_label_and_pval(d):
    for k, v in d.items():
        new_v = []
        for x in v:
            lbl = ont.label(x)
            pval = '--'
            for i in range(data.shape[0]):
                if x == data[i,0]:
                    pval = round(data[i,4],6)
            if lbl:
                x = lbl + ", pval = " + str(pval)
            else:
                x = None
            new_v.append(x)
        d.update([(k, new_v)])
    return d
            

def log_arr(arr, base=10, includeNone=False):
    res = [-math.log(x, base) if x is not None else None for x in arr]
    if includeNone:
        return res #keeps None values
    else: 
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
    mx = mx_log
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
        for i in [x + 2 for x in range(3)]:
            if pd.isnull(final[int(idx/2), i]):
                final[int(idx / 2), i] = "--"
        titles[idx]['min-pval'] = round(final[int(idx/2), 2], 6) if isinstance(final[int(idx/2), 2], float) else final[int(idx/2), 2]
        titles[idx]['init-pval'] = round(final[int(idx/2), 3], 6) if isinstance(final[int(idx/2), 3], float) else final[int(idx/2), 3]
        titles[idx]['min-pval-children'] = round(final[int(idx/2), 4], 6) if isinstance(final[int(idx/2), 4], float) else final[int(idx/2), 4]
        titles[idx]['descendants'] = final[int(idx/2), -1]
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
    r_str = 'ff'
    if np.isnan(pval):
        return 'ffffff'
    x = -math.log(pval, base)
    
    scale = 255 / mx
    y = int(round(x*scale))
    gb = 255 - y
    if gb < 0:
        gb = 0
        
    gb_str = format(gb,'x')
    if len(gb_str) < 2:
        gb_str = '0' + gb_str
    
    rgb = r_str + gb_str + gb_str
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

final_pvals = get_pvals_and_children_with_depth()

log_min_pvals = log_arr(final_pvals[:,0].tolist(),includeNone=True)
mx_log = max(log_arr(final_pvals[:,0].tolist()))

# interpolate_vals = np.array(log_min_pvals)[:, np.newaxis] / mx_log
interpolate_vals = np.array([round(x / mx_log, 6) if x is not None else None for x in log_min_pvals])[:, np.newaxis]
final_pvals = np.concatenate([final_pvals[:,:-1], 
                              interpolate_vals,
                              np.array(log_min_pvals)[:, np.newaxis],
                              (final_pvals[:,-1])[:, np.newaxis]], axis=1)

# final_pvals_np = np.array(final_pvals)[np.newaxis]
# final = np.concatenate((starting_nodes, final_pvals_np.T), axis=1)
final = np.concatenate((starting_nodes, final_pvals), axis=1)

for i, n in np.ndenumerate(final[:,0]):
    final[i[0],0] = n.replace(' ', '_')
final_dataset = pd.DataFrame({'Title': final[:,0], 'ID': final[:,1], 'min_pval': final[:,2], 
                              'init_pval': final[:,3], 'min_pval_children': final[:,4],
                              'interpolate': final[:,5], 'log_min_pval': final[:,6],
                              'descendants': final[:,-1]})

final_table_name = 'to_plunker_' + input_csv
final_dataset.to_csv(final_table_name, index=False)
print(pd.read_csv(final_table_name))

df = pd.read_csv(final_table_name)
plunker_inputs = df.to_numpy()


json_attrs = ['Title', 'ID', 'min_pval', 'init_pval',
              'min_pval_children', 'interpolate', 'log_min_pval', 'descendants']

ld = [{x: plunker_inputs[i,j] for (j, x) in enumerate(json_attrs)}
      for i in range(plunker_inputs.shape[0])]

json_filename = 'plunker_inputs_' + input_csv.split('.')[0] + '.json'
with open('Project/' + json_filename, 'w') as file:
    simplejson.dump(ld, file, ignore_nan=True)

new_cellLocation = new_html()
new_html_name = 'new_cellLocation_' + input_csv.split('.')[0] + '.html'

file = open(new_html_name, 'w')
file.write(new_cellLocation)
file.close()
