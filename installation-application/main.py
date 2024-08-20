from time import sleep

import data_processor as dp
import gif_player as gp
import media_player as mp

from multiprocessing import Process, Queue

NUMBER_OF_VECTORS = 4
GIFS_PATH  = "./data/gifs/"
VIDS_PATH = "./data/vids/"

# please create a new module and class in the gif_player.py file and incoporate it into this program.

class MainProgram: 
    def __init__(self, CSV_path, num_vectors): 
        self.data_processor = dp.DataProcessor(CSV_path, num_vectors)
        # self.queue = Queue()
        # self.gif_player = gp.GifPlayer(queue=self.queue)
        # self.gif_player_thread = Process(target=self.gif_player.run)
        # self.gif_player_thread.start()
        self.media_player = mp.MediaPlayer(GIFS_PATH, VIDS_PATH)
        self.media_player.start_on_new_process()
    
    def run(self):
        while True:
            # if not self.queue.empty():
            #     message = self.queue.get()
            #     if message == "terminate":
            #         self.gif_player.terminate()
            row = self.data_processor.get_random_row()
            print(f"Processing index: {row.name}, Countries: {row['Countries']}, Keywords: {row['Keywords']}") #, Label and vectors: {[row['Label']] +  list(row['Vectors'])}
            if isinstance(row['Gifs'], str):
                print(f"Found {row['Gifs']}")
                self.media_player.queue_media(f"{row['Gifs']}")
            sleep(1) # you can change this, but in the actual running of the system there will be around 5 - 10 seconds of delay whilst the midi file is played

if __name__ == "__main__":
    # Normal data set main_program = MainProgram('/Users/erika/Documents/GitHub/transforming-collections/prototype-scripts/app/data/tanc-etan_system-dataset.csv', NUMBER_OF_VECTORS)
    main_program = MainProgram('./data/test.csv', NUMBER_OF_VECTORS)
    main_program.run()
