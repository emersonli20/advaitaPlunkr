# -*- coding: utf-8 -*-
"""

@author: emers
"""

from __future__ import print_function
from ontobio.ontol_factory import OntologyFactory
from ontobio.assoc_factory import AssociationSetFactory

import pandas as pd
import numpy as np

ofactory = OntologyFactory()
ont = ofactory.create('go')

data = pd.read_csv('C:\\Users\\emers\\python-projects\\pval\\melanoma.csv')
print(data)

data = data.to_numpy()
print(data)

starting_node_titles = ['Cytosol', 'Intermediate filaments', 'Actin filaments', 'Focal adhesion sites', 'Microtubule organizing center'
                       , 'Centrosome', 'Microtubules', 'Microtubule ends', 'Secreted proteins', 'Lipid Droplets', 'Lysosomes',
                       'Peroxisomes', 'Endosomes', 'Endoplasmic reticulum', 'Golgi apparatus', 'Nucleoplasm', 'Nuclear membrane',
                       'Nuclear bodies', 'Nuclear speckles', 'Nucleoli', 'Nucleoli fibrillar center', 'Rods and rings', 'Mitochondria'
                       , 'Plasma membrane']

starting_node_ids = ['GO:0005829', 'GO:0044614', 'GO:0051764', None, 'GO:0005815', 'GO:0005813', 'GO:0005874', 'GO:1990752'
                    , None, 'GO:0005811', 'GO:0005764', 'GO:0005777', 'GO:0005768', 'GO:0005783', 'GO:0005794', 'GO:0005654',
                    'GO:0031965', 'GO:0016604', 'GO:0016607', 'GO:0005730', 'GO:0001650', None, 'GO:0005739', 'GO:0005886']

starting_node_titles_np = np.array(starting_node_titles)[np.newaxis]
starting_node_ids_np = np.array(starting_node_ids)[np.newaxis]

starting_nodes = np.concatenate((starting_node_titles_np.T, starting_node_ids_np.T),axis=1)
print(starting_nodes)
print(starting_nodes.shape)

# breadth first search
def bfs(source):
    explored = []
    queue = [source]
    match = None
    while queue:
        node = queue.pop(0)
        if node in data[:,0]:
            match = node
            break
        elif node not in explored:
            explored.append(node)
            neighbors = ont.neighbors(source)
            queue.extend(neighbors)
        #else statement in case a match is never found?
        #what if bfs returns None?
    return match

print("Starting Nodes")
for i in range(starting_nodes.shape[0]):
    print(starting_nodes[i][1])
    
print()
bfs_results = []
print("bfs results")
for i in range(starting_nodes.shape[0]):
    if starting_nodes is not None:
        print(bfs(starting_nodes[i][1]))
        bfs_results.append(bfs(starting_nodes[i][1]))

# get pvals
pvals = []
for i in range(len(bfs_results)):
    if bfs_results[i] is None:
            pvals.append(None)
    for j in range(data.shape[0]):
        if bfs_results[i] == data[j,0]:
            pvals.append(data[j,4])

print()
print('pvals:')
print(pvals)
