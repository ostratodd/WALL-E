import numpy as np
from scipy.optimize import linear_sum_assignment


cost = np.array([[4, 1, 3], [2, 0, 5], [3, 2, 2]])
row_ind, col_ind = linear_sum_assignment(cost)
print(col_ind)
print (cost[row_ind, col_ind].sum())

print(cost)
