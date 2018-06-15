import pickle
from typing import Union, Callable

import matplotlib.pyplot as plt
import numpy as np

from sklearn.model_selection import train_test_split

import engine.utils.projections as projections
from engine.estimators.logistic_regression import LogisticRegression
from engine.optimizers.sgd_logistic import LogisticSGD
from engine.optimizers.sdca_logistic import LogisticSDCA
from engine.utils.normalize import Normalizer

from engine.utils.data_sets import load_sklearn_dataset, load_adults_dataset


def compute_search(x_train: np.ndarray, y_train: np.ndarray, x_test: np.ndarray, y_test: np.ndarray,
                   param_name: str, param_values: Union[list, np.ndarray],
                   optimizer_type, optimizer_kwargs: dict=None,
                   projection: Callable[[np.ndarray], np.ndarray]=projections.identity_projection):
    scores_train = list()
    scores_test = list()

    #plt.ion()
    #plt.show()

    for param_value in param_values:
        np.random.seed(50307)

        # gather parameters
        param_kwarg = {param_name: param_value}
        if optimizer_kwargs is None:
            optimizer_kwargs = param_kwarg
        else:
            optimizer_kwargs.update(param_kwarg)

        # init optimizer and estimator
        optimizer = optimizer_type(**optimizer_kwargs)
        estimator = LogisticRegression(optimizer=optimizer, projection=projection)

        # fit estimator
        hist_w, hist_loss = estimator.fit(x_train, y_train, epochs=15, save_hist=True)

        '''# plot learning
        #plt.clf()
        plt.figure()
        plt.title(", ".join(map(lambda x: "{}={}".format(*x), optimizer_kwargs.items())))
        plt.plot(hist_loss)
        plt.draw()
        plt.pause(0.001)'''

        # evaluate
        score_train = estimator.score_accuracy(x_train, y_train)
        score_test = estimator.score_accuracy(x_test, y_test)
        scores_train.append(score_train)
        scores_test.append(score_test)

    #plt.close()
    #plt.ioff()

    return scores_train, scores_test


def plot_search(param_name: str, param_values: Union[list, np.ndarray], scores_train, scores_test, logarithmic: bool=False):
    plt.figure()
    plot_method = plt.semilogx if logarithmic else plt.plot
    plot_method(param_values, scores_train, label='Train set')
    plot_method(param_values, scores_test, label='Test set')

    plt.title("Accuracy vs hyper parameter")
    plt.xlabel(param_name)
    plt.ylim(0, 1)
    plt.ylabel("Accuracy")
    plt.legend()

    #plt.show()

def eval_C(data, labels, vect_param, nb_epoch, data_name, eps_base=10**-6):
    X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.15)
    
    vect_train_accuracy_sgd = []
    vect_train_accuracy_sdca = []
    
    vect_test_accuracy_sgd = []
    vect_test_accuracy_sdca = []
    
    for param in vect_param:
        # make estimator
        sgd = LogisticSGD(c=param, eps=eps_base)
        sgd_clf = LogisticRegression(optimizer=sgd)
        
        sdca = LogisticSDCA(c=param)
        sdca_clf = LogisticRegression(optimizer=sdca)
        
        # train estimators without history
        sgd_clf.fit(X_train, y_train, epochs=nb_epoch, save_hist=False)
        sdca_clf.fit(X_train, y_train, epochs=nb_epoch, save_hist=False)
        
        vect_train_accuracy_sgd.append(sgd_clf.score_accuracy(X_train, y_train))
        vect_train_accuracy_sdca.append(sdca_clf.score_accuracy(X_train, y_train))
        
        vect_test_accuracy_sgd.append(sgd_clf.score_accuracy(X_test, y_test))
        vect_test_accuracy_sdca.append(sdca_clf.score_accuracy(X_test, y_test))
    
    plt.figure()
    plt.semilogx(vect_param, vect_train_accuracy_sgd, 'b', label="train")
    plt.semilogx(vect_param, vect_test_accuracy_sgd, 'r', label="test")
    plt.title("SGD accuracy vs. hyperparameter C\n on data set " + data_name)
    plt.xlabel("C")
    plt.ylabel("Accuracy")
    plt.legend()
    
    plt.figure()
    plt.semilogx(vect_param, vect_train_accuracy_sdca, 'b', label="train")
    plt.semilogx(vect_param, vect_test_accuracy_sdca, 'r', label="test")
    plt.title("SDCA accuracy vs. hyperparameter C\n on data set " + data_name)
    plt.xlabel("C")
    plt.ylabel("Accuracy")
    plt.legend()

def eval_eps(data, labels, vect_param, nb_epoch, data_name, param_c=10**1):
    X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.15)
    
    vect_train_accuracy_sgd = []
    
    vect_test_accuracy_sgd = []
    
    for param in vect_param:
        # make estimator
        sgd = LogisticSGD(c=param_c, eps=param)
        sgd_clf = LogisticRegression(optimizer=sgd)
        
        # train estimators without history
        sgd_clf.fit(X_train, y_train, epochs=nb_epoch, save_hist=False)
        
        vect_train_accuracy_sgd.append(sgd_clf.score_accuracy(X_train, y_train))
        
        vect_test_accuracy_sgd.append(sgd_clf.score_accuracy(X_test, y_test))
    
    plt.figure()
    plt.semilogx(vect_param, vect_train_accuracy_sgd, 'b', label="train")
    plt.semilogx(vect_param, vect_test_accuracy_sgd, 'r', label="test")
    plt.title("Accuracy of SGD vs. hyperparameter epsilon \non data set " + data_name)
    plt.xlabel("Epsilon")
    plt.ylabel("Accuracy")
    plt.legend()

def import_data_arrhythmia():
    # importation of data
    with open("datasets/Heart_disease/heart_disease_data.pkl", 'rb') as file:
        x = pickle.load(file)
        y = pickle.load(file)

    # dividing data in 2 classes
    y = np.where(y == 1, 1, -1)
    
    return x, y


def main():
    x, y = load_adults_dataset()

    # normalisation
    normalizer = Normalizer(x)
    x = normalizer.normalize(x)

    # split
    n, d = x.shape
    n_train = int(n*0.9)
    x_train, y_train = x[:n_train], y[:n_train]
    x_test, y_test = x[n_train:], y[n_train:]

    # test setup
    param_name = 'eps'
    param_values = np.logspace(-7, 0, num=10)
    optimizer_type = LogisticSGD
    optimizer_kwargs = {'c': 1}

    # compute training
    projection = projections.identity_projection
    scores_train, scores_test = compute_search(x_train, y_train, x_test, y_test,
                                               param_name, param_values,
                                               optimizer_type, optimizer_kwargs,
                                               projection)

    # plot result
    plot_search(param_name, param_values, scores_train, scores_test, logarithmic=True)
    
    plt.show()


if __name__ == '__main__':
    #main()
    
    #x, y = import_data_arrhythmia()
    
    x, y = load_adults_dataset()
    N, dim = x.shape
    n_sample = 1200
    index = np.arange(N)
    np.random.shuffle(index)
    x = x[index[:n_sample],:]
    y = y[index[:n_sample]]
    
    #x, y = load_sklearn_dataset(data_set_name="lfw", n=20)
    
    # normalisation
    normalizer = Normalizer(x)
    x = normalizer.normalize(x)
    
    '''vect_C = 10**np.linspace(-5, 7, 50)
    nb_epoch = 30
    data_name = "Arrhythmia"
    eval_C(x, y, vect_C, nb_epoch, data_name)'''
    
    vect_eps = 10**np.linspace(-10, 0, 70)
    nb_epoch = 10
    data_name = "Adults"
    eval_eps(x, y, vect_eps, nb_epoch, data_name, param_c=10**4)
    
    plt.show()