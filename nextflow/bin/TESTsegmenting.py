#!/usr/bin/env python3

import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree
from mpl_toolkits.mplot3d import Axes3D

# create data
data = np.random.binomial(1, 0.1, 1000)
data = data.reshape((10,10,10))

data = [[[1 1 1]
  [1 1 1]
  [1 1 1]]

 [[0 0 0]
  [0 0 0]
  [0 0 0]]

 [[2 2 2]
  [2 2 2]
  [2 2 2]]]

# find coordinates
cs = np.argwhere(data > 0)

# build k-d tree
kdt = cKDTree(cs)
edges = kdt.query_pairs(1)

# create graph
G = nx.from_edgelist(edges)

# find connected components
ccs = nx.connected_components(G)
node_component = {v:k for k,vs in enumerate(ccs) for v in vs}

# visualize
df = pd.DataFrame(cs, columns=['x','y','z'])
df['c'] = pd.Series(node_component)




# to include single-node connected components
# df.loc[df['c'].isna(), 'c'] = df.loc[df['c'].isna(), 'c'].isna().cumsum() + df['c'].max()

fig = plt.figure(figsize=(10,10))
ax = fig.add_subplot(111, projection='3d')
cmhot = plt.get_cmap("hot")
#ax.scatter(df['x'], df['y'], df['z'], c=df['c'], s=50, cmap=cmhot)
ax.scatter(df['x'], df['y'], df['z'], s=50, cmap=cmhot)

plt.show()


print(df)
