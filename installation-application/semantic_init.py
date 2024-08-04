import pandas as pd
import numpy as np

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler

import subprocess

class SemanticModel: 
    def __init__(self, pure_data_path, embeddings_path, vector_length):
        self.pd_executable = '/Applications/Pd-0.55-0.app/Contents/Resources/bin/pd'
        self.pure_data = subprocess.Popen([self.pd_executable, "-nogui", pure_data_path])
        self.bert = np.load(embeddings_path)
        self.vector_length = vector_length

    def make_vectors(self):
        #normalise first
        x = StandardScaler().fit_transform(self.bert)
        #PCA
        pca = PCA(n_components= self.vector_length)
        x = pca.fit_transform(x)
        #turn into percentages 
        x = MinMaxScaler().fit_transform(x)
        #turn vectors into list for df
        x = list(x)
        return x