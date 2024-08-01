from time import sleep

import data_processor as dp

# please create a new module and class in the gif_player.py file and incoporate it into this program.

class MainProgram: 
    def __init__(self, CSV_path): 
        self.data_processor = dp.DataProcessor(CSV_path)
    
    def run(self):
        while True:
            row = self.data_processor.get_random_row()
            print(f"Processing index: {row.name}, Countries: {row['Countries']}")
            
            # this is just for testing, but I've added about 64 indexes with gifs
            for i in range(64):
                if row['Gifs'] == f"gif-{i}":
                    print(f"Found gif-{i}")

            sleep(0.5) # you can change this, but in the actual running of the system there will be around 5 - 10 seconds of delay whilst the midi file is played

if __name__ == "__main__":
    # Normal data set main_program = MainProgram('/Users/erika/Documents/GitHub/transforming-collections/prototype-scripts/app/data/tanc-etan_system-dataset.csv')
    main_program = MainProgram('/Users/erika/Documents/GitHub/transforming-collections/installation-application/data/system-dataset-gif-test.csv')
    main_program.run()