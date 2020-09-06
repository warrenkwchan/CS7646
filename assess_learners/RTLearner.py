import numpy as np
import pandas as pd
import math

import util


class RTLearner:
	def author(self):
		return 'tkim338'

	def __init__(self, leaf_size=1, verbose=False):
		self.tree = np.empty((1, 5)) # columns: split_feature | split_val | left_node_index | right_node_index | leaf_val
		self.leaf_size = leaf_size
		self.verbose = verbose

	def add_evidence(self, x_train, y_train):
		self.split(0, x_train, y_train)

	def split(self, node_index, X, y):
		if len(y) <= self.leaf_size:
			self.tree[node_index] = [None, None, None, None, np.median(y)]
			return

		split_attribute, split_value = find_best_split_feature(X, y)
		X_left, X_right, y_left, y_right = partition_classes(X, y, split_attribute, split_value)

		if len(y_left) == 0 or len(y_right) == 0:
			self.tree[node_index] = [None, None, None, None, np.median(y)]
			return

		self.tree = np.append(self.tree, np.empty((1,5)), axis=0)
		left_node_index = len(self.tree)-1

		self.tree = np.append(self.tree, np.empty((1,5)), axis=0)
		right_node_index = len(self.tree)-1

		self.tree[node_index] = np.array([split_attribute, split_value, left_node_index, right_node_index, None])

		self.split(left_node_index, X_left, y_left)
		self.split(right_node_index, X_right, y_right)

	def traverse(self, record, node_index):
		if not np.isnan(self.tree[node_index, 4]): # if not NaN, is leaf node
			return self.tree[node_index, 4]

		split_attribute = int(self.tree[node_index, 0])
		split_value = self.tree[node_index, 1]

		if record[split_attribute] <= split_value:
			return self.traverse(record, int(self.tree[node_index, 2]))
		else:
			return self.traverse(record, int(self.tree[node_index, 3]))

	def query(self, Xtest):
		Y = []
		for x in Xtest:
			Y.append(self.traverse(x, 0))
		return Y

def find_best_split_feature(X, y):
	num_features = X.shape[1]
	max_corr_col = np.random.randint(0, num_features)
	return max_corr_col, np.median(X[:,max_corr_col])

def partition_classes(X, y, split_attribute, split_val):
	X_left = X[X[:, split_attribute] <= split_val, :]
	X_right = X[X[:, split_attribute] > split_val, :]
	y_left = y[X[:, split_attribute] <= split_val]
	y_right = y[X[:, split_attribute] > split_val]

	return X_left, X_right, y_left, y_right

# train_x = np.array([[4, 2],[6, 4],[7, 7]])
# train_y = np.array([1,2,3])
# test_x = np.array([[4, 2],[6, 4],[7, 7]])
# test_y = np.array([1,2,3])

# f = util.get_learner_data_file('Istanbul.csv')
f = util.get_learner_data_file('ripple.csv')
data = np.genfromtxt(f, delimiter=",")
# data = data[1:, 1:]

# compute how much of the data is training and testing
train_rows = int(0.6 * data.shape[0])
test_rows = data.shape[0] - train_rows

# separate out training and testing data
train_x = data[:train_rows, 0:-1]
train_y = data[:train_rows, -1]
test_x = data[train_rows:, 0:-1]
test_y = data[train_rows:, -1]

print(f"{test_x.shape}")
print(f"{test_y.shape}")

# create a learner and train it
learner = RTLearner(verbose=True)
learner.add_evidence(train_x, train_y)  # train it
print(learner.author())

# evaluate in sample
pred_y = learner.query(train_x)  # get the predictions
rmse = math.sqrt(((train_y - pred_y) ** 2).sum() / train_y.shape[0])
print()
print("In sample results")
print(f"RMSE: {rmse}")
c = np.corrcoef(pred_y, y=train_y)
print(f"corr: {c[0, 1]}")

# evaluate out of sample
pred_y = learner.query(test_x)  # get the predictions
rmse = math.sqrt(((test_y - pred_y) ** 2).sum() / test_y.shape[0])
print()
print("Out of sample results")
print(f"RMSE: {rmse}")
c = np.corrcoef(pred_y, y=test_y)
print(f"corr: {c[0, 1]}")

learner.query([[-0.47516621, 0.71684211]])
