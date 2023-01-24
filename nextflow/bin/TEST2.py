import numpy as np
from sklearn.cluster import AgglomerativeClustering

N = 1500
box_size = 10

points = np.random.rand(N, 3) * box_size
# array([[5.93688935, 6.63209391], [2.6182196 , 8.33040083], [4.35061433, 7.21399521], ..., [4.09271753, 2.3614302 ], [5.69176382, 1.78457418], [9.76504841, 1.38935121]])
print(points)

clustering = AgglomerativeClustering(n_clusters=None, distance_threshold=1).fit(points)

print('Number of clusters:', clustering.n_clusters_)
# Number of clusters: 224
