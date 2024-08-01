import semantic
import random
import pandas as pd
from ast import literal_eval

class DataProcessor:
    def __init__(self, csv_path, number_of_vectors):
        self.df = pd.read_csv(csv_path)
        self.df['Countries'] = self.df['Countries'].apply(lambda x: literal_eval(x) if pd.notnull(x) else x)
        #self.df['Vectors'] = semantic.make_vectors(number_of_vectors)
    
    def get_random_row(self):
        random_index = random.randint(0, len(self.df) - 1)
        return self.df.iloc[random_index]
