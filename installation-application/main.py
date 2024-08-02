from time import sleep

import data_processor as dp
import gif_player as gp
from gif_player import run_gif_player

import _thread as thread

NUMBER_OF_VECTORS = 4

# please create a new module and class in the gif_player.py file and incoporate it into this program.

class MainProgram: 
    def __init__(self, CSV_path, num_vectors): 
        self.data_processor = dp.DataProcessor(CSV_path, num_vectors)
        # self.gif_player = gp.GifPlayer("./data/gifs/")
        thread.start_new_thread(run_gif_player, ())

    
    def run(self):
        while True:
            row = self.data_processor.get_random_row()
            print(f"Processing index: {row.name}, Countries: {row['Countries']}, Keywords: {row['Keywords']}") #, Label and vectors: {[row['Label']] +  list(row['Vectors'])}
            
            # this is just for testing, but I've added about 64 indexes with gifs
            for i in range(64):
                if row['Gifs'] == f"gif-{i}":
                    print(f"Found gif-{i}")

            sleep(0.5) # you can change this, but in the actual running of the system there will be around 5 - 10 seconds of delay whilst the midi file is played

if __name__ == "__main__":
    # Normal data set main_program = MainProgram('/Users/erika/Documents/GitHub/transforming-collections/prototype-scripts/app/data/tanc-etan_system-dataset.csv', NUMBER_OF_VECTORS)
    main_program = MainProgram('./data/system-dataset-gif-test.csv', NUMBER_OF_VECTORS)
    main_program.run()
