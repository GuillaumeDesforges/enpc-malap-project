from sklearn.datasets import fetch_covtype, fetch_rcv1, fetch_lfw_people
from sklearn.preprocessing import scale, normalize, MinMaxScaler
import pandas as pd


def load_sklearn_dataset(data_set_name="covtype", n=1000, d=10):
    if data_set_name == "covtype":
        covtype = fetch_covtype()
        X = normalize(covtype.data[:n])
        y = covtype.target[:n]
        return X, y

    if data_set_name == "rcv1":
        rcv1 = fetch_rcv1()
        X = normalize(rcv1.data[:n])
        y = rcv1.target[:n]
        return X, y

    if data_set_name == "lfw":
        lfw = fetch_lfw_people()
        print(lfw.data.shape)
        print(lfw.target.shape)
        X = normalize(lfw.data[:n], axis=1)
        # MinMaxScaler().transform(lfw.data[:n])
        # scale(lfw.data[:n])

        y = lfw.target[:n]
        return X, y


def load_adults_dataset():
    df = pd.read_csv('datasets/Adults/adult.data.txt', )
    # TODO categorical

    x = df.pop('salary')
    y = df['salary'].values
