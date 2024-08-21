import glob
import pandas as pd
import numpy as np

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler

import subprocess

class SemanticModel: 
    def __init__(self, pure_data_path, embeddings_path, vector_length):
        self.pd_executable = self.find_pd_executable()
        if not self.pd_executable:
            raise Exception("Pure Data not found! Please install Pure Data!")
        self.pure_data = subprocess.Popen([self.pd_executable, "-nogui", pure_data_path])
        self.bert = np.load(embeddings_path)
        self.vector_length = vector_length
    
    def find_pd_executable(self):
        pd_apps = glob.glob('/Applications/Pd-*.app/Contents/Resources/bin/pd')
        
        if pd_apps:
            return pd_apps[0]
        
        return None

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