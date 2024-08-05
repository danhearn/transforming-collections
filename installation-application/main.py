from time import sleep

import data_processor as dp
import semantic_init
import semantic_client
import serial_com

NUMBER_OF_VECTORS = 4
CSV_PATH = '/Users/erika/Documents/GitHub/transforming-collections/installation-application/data/system-dataset-gif-test.csv'
PURE_DATA_PATH = '/Users/erika/Documents/GitHub/data-sonification/semantic_synth(with-effects).pd'
EMBEDDINGS_PATH = '/Users/erika/Documents/GitHub/transforming-collections/data/input/tate_wellcome_SEA_text_embeddings.npy'
LED_MATRIX_PATH = '/dev/ttyACM0'
ARUDUINO_PATH = ''
DELAY = 5

class MainProgram: 
    def __init__(self, CSV_path, num_vectors, pure_data_path, embeddings_path, led_matrix_path, arduino_path, delay): 
        self.positive_client = semantic_client.SemanticClient("127.0.0.1", 9000)
        self.negative_client = semantic_client.SemanticClient("127.0.0.1", 10000)
        self.semantic_init = semantic_init.SemanticModel(pure_data_path, embeddings_path, num_vectors)
        self.data_processor = dp.DataProcessor(CSV_path, self.semantic_init)
        self.LED_matrix = serial_com.SerialCommunication(led_matrix_path)
        self.LED_matrix.connect_serial()
        self.delay = delay
        
    def run(self):
        while True:
            row = self.data_processor.get_random_row()
            vectors = [float(value) for value in row['Vectors']]
            print(f"Processing index: {row.name}, Countries: {row['Countries']}, Keywords: {row['Keywords']}  Label and vectors: {[row['Label']] +  list(row['Vectors'])}")
            
            # this is just for testing, but I've added about 64 indexes with gifs
            for i in range(64):
                if row['Gifs'] == f"gif-{i}":
                    print(f"Found gif-{i}")

            # -------------------- SEMANTIC VECTOR OSC MESSAGES ------------------------
            if row['Label'] == 1:
                self.positive_client.send_vectors("/positve", vectors)
            else:
                self.negative_client.send_vectors("/negative", vectors)

            sleep(self.delay) 
            
if __name__ == "__main__":
    try: 
        main_program = MainProgram(CSV_PATH, NUMBER_OF_VECTORS, PURE_DATA_PATH, EMBEDDINGS_PATH, LED_MATRIX_PATH, ARUDUINO_PATH ,DELAY)
        main_program.run()
    except KeyboardInterrupt:
        main_program.semantic_init.pure_data.terminate()
