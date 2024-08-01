import pandas as pd
import numpy as np

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler

import subprocess

#launch pure data
pureData_synth_path = "/home/tanc/Documents/transforming-collections-erika-tan/app/data/semantic/semantic_synth.pd" #add pure data patch here!
#subprocess.Popen(["pd", "-nogui", pureData_synth_path])

bert = np.load('data/input/tate_wellcome_SEA_text_embeddings.npy')

#this takes the full embeddings and squashes them down to a smaller vector of length n, e.g. 10
def make_vectors(vector_length, embeddings=bert):
    #normalise first
    x = StandardScaler().fit_transform(bert)
    #PCA
    pca = PCA(n_components=vector_length)
    x = pca.fit_transform(x)
    #turn into percentages 
    x = MinMaxScaler().fit_transform(x)
    #turn vectors into list for df
    x = list(x)
    
    return x
