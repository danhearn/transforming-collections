from time import sleep

import data_processor as dp
import gif_player as gp

import threading
import queue

NUMBER_OF_VECTORS = 4

# please create a new module and class in the gif_player.py file and incoporate it into this program.

class MainProgram: 
    def __init__(self, CSV_path, num_vectors): 
        self.data_processor = dp.DataProcessor(CSV_path, num_vectors)
        self.queue = queue.Queue()
        self.gif_player = gp.GifPlayer("./data/gifs", self.queue)
        self.gif_player_thread = threading.Thread(target=self.gif_player.run)
        self.gif_player_thread.start()
    
    def run(self):
        while True:
            if not self.queue.empty():
                message = self.queue.get()
                if message == "terminate":
                    self.gif_player.terminate()
            self.gif_player.impl_poll_events()
            row = self.data_processor.get_random_row()
            print(f"Processing index: {row.name}, Countries: {row['Countries']}, Keywords: {row['Keywords']}") #, Label and vectors: {[row['Label']] +  list(row['Vectors'])}
            
            # this is just for testing, but I've added about 64 indexes with gifs
            # for i in range(64):
            #     if row['Gifs'] == f"gif-{i}":
            #         print(f"Found gif-{i}")
            #         self.queue.put(f"gif-{i}")

            # sleep(0.1) # you can change this, but in the actual running of the system there will be around 5 - 10 seconds of delay whilst the midi file is played

if __name__ == "__main__":
    # Normal data set main_program = MainProgram('/Users/erika/Documents/GitHub/transforming-collections/prototype-scripts/app/data/tanc-etan_system-dataset.csv', NUMBER_OF_VECTORS)
    main_program = MainProgram('./data/system-dataset-gif-test.csv', NUMBER_OF_VECTORS)
    main_program.run()
