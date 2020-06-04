"""
authors: Emerson Li, Quoc Huynh

"""

from __future__ import print_function
from ontobio.ontol_factory import OntologyFactory
from ontobio.assoc_factory import AssociationSetFactory

import obonet

import pandas as pd
import numpy as np

from bs4 import BeautifulSoup as bs

def has_class_but_no_id(tag):
    return tag.has_attr('title')

html_file = open('cellLocation.html', 'r')
html_content = html_file.read()
html_file.close()
soup  = bs(html_content,'html.parser') 

ofactory = OntologyFactory()
ont = ofactory.create('go.json')

# data = pd.read_csv('melanoma.csv')
# data = data.to_numpy()

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
    if name[-1] is 's':
        if name[-2] is not 'u':
            name = name[:-1]
    if name[-1] is 'i':
        name = name[:-1]
        name = name + 'us'
    if name[-1] is 'a':
        name = name[:-1]
        name = name + 'on'
    if name.lower() not in starting_node_titles:
        starting_node_titles.append(name.lower())
print(starting_node_titles)
# print(len(starting_node_titles))

# # get ids from the melanoma.csv file
data = pd.read_csv('melanoma.csv')
data = data.to_numpy()
# starting_node_ids = []
# melanoma_ids = data[:,0]
# melanoma_titles = data[:,1].tolist()
# for name in starting_node_titles:
#     if name.lower() in melanoma_titles:
#         row_num = melanoma_titles.index(name.lower())
#         starting_node_ids.append(melanoma_ids[row_num])
#     else:
#         starting_node_ids.append(None)
# print(starting_node_ids)

## get ids from the go.obo file
graph = obonet.read_obo('go.obo')
name_to_id = {data['name'].lower(): id_ for id_, data in graph.nodes(data=True) if 'name' in data}
starting_node_ids = []
for name in starting_node_titles:
    try:
        starting_node_ids.append(name_to_id[name])
    except:
        starting_node_ids.append(None)

print(starting_node_ids)
    

starting_node_titles_np = np.array(starting_node_titles)[np.newaxis]
starting_node_ids_np = np.array(starting_node_ids)[np.newaxis]

starting_nodes = np.concatenate((starting_node_titles_np.T, starting_node_ids_np.T),axis=1)
print(starting_nodes)
print(starting_nodes.shape)

# breadth first search
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

# get pvals
def get_pvals():
    pvals = []
    for node in starting_node_ids:
        pvals.append(min_pval(bfs(node)))
    return pvals

# print("Starting Nodes")
# for i in range(starting_nodes.shape[0]):
#     print(starting_nodes[i,1])

# print(get_pvals())

final_pvals = get_pvals()

final_pvals_np = np.array(final_pvals)[np.newaxis]
final = np.concatenate((starting_nodes, final_pvals_np.T), axis=1)

final_dataset = pd.DataFrame({'Title': final[:,0], 'ID': final[:,1], 'pval': final[:,2]})

final_dataset.to_csv('to_plunker.csv', index=False)
print(pd.read_csv('to_plunker.csv'))