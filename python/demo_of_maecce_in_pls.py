# -*- coding: utf-8 -*- 
# %reset -f
"""
@author: Hiromasa Kaneko
"""
# Demonstration of MAEcce in PLS modeling

import matplotlib.pyplot as plt
import numpy as np
from sklearn import datasets
from sklearn import model_selection
from sklearn.cross_decomposition import PLSRegression
from sklearn.model_selection import train_test_split

# settings
number_of_training_samples = 50  # 30, 50, 100, 300, 500, 1000, 3000, for example
number_of_test_samples = 10000
number_of_x_variables = 30  # 10, 30, 50, 100, 300, 500, 1000, 3000, for example
number_of_y_randomization = 100
max_number_of_pls_components = 20
fold_number = 5

# generate sample dataset
x, y = datasets.make_regression(n_samples=number_of_training_samples + number_of_test_samples,
                                n_features=number_of_x_variables, n_informative=10, noise=30,
                                random_state=number_of_training_samples + number_of_x_variables)
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=number_of_test_samples, random_state=0)

# autoscaling
autoscaled_x_train = (x_train - x_train.mean(axis=0)) / x_train.std(axis=0, ddof=1)
autoscaled_y_train = (y_train - y_train.mean()) / y_train.std(ddof=1)
autoscaled_x_test = (x_test - x_train.mean(axis=0)) / x_train.std(axis=0, ddof=1)

# modeling and prediction
pls_components = np.arange(1, min(np.linalg.matrix_rank(autoscaled_x_train), max_number_of_pls_components + 1), 1)
mae_all_cv = list()
for pls_component in pls_components:
    pls_model_in_cv = PLSRegression(n_components=pls_component)
    pls_model_in_cv.fit(autoscaled_x_train, autoscaled_y_train)
    calculated_y_in_cv = np.ndarray.flatten(pls_model_in_cv.predict(autoscaled_x_train))
    estimated_y_in_cv = np.ndarray.flatten(
        model_selection.cross_val_predict(pls_model_in_cv, autoscaled_x_train, autoscaled_y_train, cv=fold_number))
    calculated_y_in_cv = calculated_y_in_cv * y_train.std(ddof=1) + y_train.mean()
    estimated_y_in_cv = estimated_y_in_cv * y_train.std(ddof=1) + y_train.mean()
    mae_all_cv.append(float(sum(abs(y_train - estimated_y_in_cv)) / len(y_train)))
optimal_pls_component_number = np.where(mae_all_cv == np.min(mae_all_cv))
optimal_pls_component_number = optimal_pls_component_number[0][0] + 1
regression_model = PLSRegression(n_components=optimal_pls_component_number)
regression_model.fit(autoscaled_x_train, autoscaled_y_train)
estimated_y_train = np.ndarray.flatten(regression_model.predict(autoscaled_x_train))
estimated_y_train = estimated_y_train * y_train.std(ddof=1) + y_train.mean()
estimated_y_train_cv = np.ndarray.flatten(
    model_selection.cross_val_predict(regression_model, autoscaled_x_train, autoscaled_y_train, cv=fold_number))
estimated_y_train_cv = estimated_y_train_cv * y_train.std(ddof=1) + y_train.mean()
predicted_y_test = np.ndarray.flatten(regression_model.predict(autoscaled_x_test))
predicted_y_test = predicted_y_test * y_train.std(ddof=1) + y_train.mean()

# save results
statistics = []
statistics.append(float(1 - sum((y_train - estimated_y_train) ** 2) / sum((y_train - y_train.mean()) ** 2)))
statistics.append(float((sum((y_train - estimated_y_train) ** 2) / len(y_train)) ** 0.5))
statistics.append(float(sum(abs(y_train - estimated_y_train)) / len(y_train)))
statistics.append(float(1 - sum((y_train - estimated_y_train_cv) ** 2) / sum((y_train - y_train.mean()) ** 2)))
statistics.append(float((sum((y_train - estimated_y_train_cv) ** 2) / len(y_train)) ** 0.5))
statistics.append(float(sum(abs(y_train - estimated_y_train_cv)) / len(y_train)))
statistics.append(float(1 - sum((y_test - predicted_y_test) ** 2) / sum((y_test - y_test.mean()) ** 2)))
statistics.append(float((sum((y_test - predicted_y_test) ** 2) / len(y_test)) ** 0.5))
statistics.append(float(sum(abs(y_test - predicted_y_test)) / len(y_test)))
statistics.append(float((sum((y_train - y_train.mean()) ** 2) / len(y_train)) ** 0.5))
statistics.append(float(sum(abs(y_train - y_train.mean())) / len(y_train)))

# y-randomization
statistics_yrand = np.empty([number_of_y_randomization, 6])
for y_rand_num in range(number_of_y_randomization):
    print('{0} / {1}'.format(y_rand_num + 1, number_of_y_randomization))
    autoscaled_y_train_rand = np.random.permutation(autoscaled_y_train)
    y_train_rand = autoscaled_y_train_rand * y_train.std(ddof=1) + y_train.mean()
    mae_all_cv = list()
    for pls_component in pls_components:
        pls_model_in_cv = PLSRegression(n_components=pls_component)
        pls_model_in_cv.fit(autoscaled_x_train, autoscaled_y_train_rand)
        calculated_y_in_cv = np.ndarray.flatten(pls_model_in_cv.predict(autoscaled_x_train))
        estimated_y_in_cv = np.ndarray.flatten(
            model_selection.cross_val_predict(pls_model_in_cv, autoscaled_x_train, autoscaled_y_train_rand,
                                              cv=fold_number))
        calculated_y_in_cv = calculated_y_in_cv * y_train.std(ddof=1) + y_train.mean()
        estimated_y_in_cv = estimated_y_in_cv * y_train.std(ddof=1) + y_train.mean()
        mae_all_cv.append(float(sum(abs(y_train_rand - estimated_y_in_cv)) / len(y_train)))
    optimal_pls_component_number_rand = np.where(mae_all_cv == np.min(mae_all_cv))
    optimal_pls_component_number_rand = optimal_pls_component_number_rand[0][0] + 1
    regression_model = PLSRegression(n_components=optimal_pls_component_number_rand)
    regression_model.fit(autoscaled_x_train, autoscaled_y_train_rand)
    estimated_y_train_rand = np.ndarray.flatten(regression_model.predict(autoscaled_x_train))
    estimated_y_train_rand = estimated_y_train_rand * y_train.std(ddof=1) + y_train.mean()
    estimated_y_in_cv_rand = np.ndarray.flatten(
        model_selection.cross_val_predict(regression_model, autoscaled_x_train, autoscaled_y_train_rand,
                                          cv=fold_number))
    estimated_y_in_cv_rand = estimated_y_in_cv_rand * y_train.std(ddof=1) + y_train.mean()
    # save results
    statistics_yrand[y_rand_num, 0] = float(
        1 - sum((y_train_rand - estimated_y_train_rand) ** 2) / sum((y_train_rand - y_train.mean()) ** 2))
    statistics_yrand[y_rand_num, 1] = float((sum((y_train_rand - estimated_y_train_rand) ** 2) / len(y_train)) ** 0.5)
    statistics_yrand[y_rand_num, 2] = float(sum(abs(y_train_rand - estimated_y_train_rand)) / len(y_train))
    statistics_yrand[y_rand_num, 3] = float(
        1 - sum((y_train_rand - estimated_y_in_cv_rand) ** 2) / sum((y_train_rand - y_train.mean()) ** 2))
    statistics_yrand[y_rand_num, 4] = float((sum((y_train_rand - estimated_y_in_cv_rand) ** 2) / len(y_train)) ** 0.5)
    statistics_yrand[y_rand_num, 5] = float(sum(abs(y_train_rand - estimated_y_in_cv_rand)) / len(y_train))

# check results
print('')
print('r2: {0}'.format(statistics[0]))
print('RMSE: {0}'.format(statistics[1]))
print('MAE: {0}'.format(statistics[2]))
print('')
print('r2cv: {0}'.format(statistics[3]))
print('RMSEcv: {0}'.format(statistics[4]))
print('MAEcv: {0}'.format(statistics[5]))
print('')
print('r2p: {0}'.format(statistics[6]))
print('RMSEp: {0}'.format(statistics[7]))
print('MAEp: {0}'.format(statistics[8]))
print('')
print('RMSEmean: {0}'.format(statistics[9]))
print('MAEmean: {0}'.format(statistics[10]))
print('')

MAEcce = statistics[2] + statistics[10] - statistics_yrand[:, 2]

plt.rcParams["font.size"] = 18
plt.hist(MAEcce, bins=30)
plt.plot(statistics[8], 0.2, 'r.')
plt.xlabel('MAEcce(histgram), MAEp(red point)')
plt.ylabel('frequency')
plt.show()
