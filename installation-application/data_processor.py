import semantic_init
import random
import pandas as pd
from ast import literal_eval

class DataProcessor:
    def __init__(self, csv_path, semantic_model):
        self.df = pd.read_csv(csv_path)
        self.df['Countries'] = self.df['Countries'].apply(lambda x: literal_eval(x) if pd.notnull(x) else x)
        self.df['Vectors'] = semantic_model.make_vectors()
    
    def get_random_row(self):
        random_index = random.randint(0, len(self.df) - 1)
        return self.df.iloc[random_index]
