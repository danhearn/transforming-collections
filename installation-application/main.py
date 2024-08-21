from multiprocessing import Process, Queue
from time import sleep
import pandas as pd
from pathlib import Path

import data_processor
import semantic_init
import semantic_client
import serial_com
import ding
import media_player

BASE_PATH = Path.cwd()
NUMBER_OF_VECTORS = 4
CSV_PATH = BASE_PATH/'system-dataset-gif-test.csv'
PURE_DATA_PATH = BASE_PATH/'../pure-data/semantic_synth(with-effects).pd'
EMBEDDINGS_PATH = BASE_PATH/'data/tate_wellcome_SEA_text_embeddings.npy'
LED_MATRIX_PATH = Path('/dev/tty.usbmodem2101')
ARDUINO_PATH = Path('/dev/tty.usbmodem2201')
JSON_PATH = BASE_PATH/'data/country_tracks.json'
DELAY = 1
GIFS_PATH = BASE_PATH/'data/gifs/'
VIDS_PATH = BASE_PATH/'data/vids/'

class MainProgram: 
    def __init__(self, CSV_path = CSV_PATH, num_vectors = NUMBER_OF_VECTORS, pure_data_path = PURE_DATA_PATH, embeddings_path = EMBEDDINGS_PATH, led_matrix_path = LED_MATRIX_PATH, arduino_path = ARDUINO_PATH, json_path = JSON_PATH, delay = DELAY): 
        try:  
            self.delay = delay
            self.positive_client = semantic_client.SemanticClient("127.0.0.1", 9000)
            self.negative_client = semantic_client.SemanticClient("127.0.0.1", 10000)
            self.semantic_init = semantic_init.SemanticModel(pure_data_path, embeddings_path, num_vectors)
            self.data_processor = data_processor.DataProcessor(CSV_path, self.semantic_init)
            self.LED_matrix = serial_com.SerialCommunication(led_matrix_path)
            self.LED_matrix.connect_serial()
            self.arduino = serial_com.SerialCommunication(arduino_path)
            self.arduino.connect_serial()
            self.ding_model = ding.DingModel(self.arduino, json_path, base_path=BASE_PATH)
            self.media_player = media_player.MediaPlayer(gifs_path=GIFS_PATH, vids_path=VIDS_PATH)
            self.media_player.start_on_new_process()
        except Exception as e:
            print(f'Error initialising main program! {e}')

    def semantic_model(self, label, vectors):
        if label == 1:
            self.positive_client.send_vectors("/positve", vectors)
        else:
            self.negative_client.send_vectors("/negative", vectors)

    def cleanup(self):
        self.semantic_init.pure_data.terminate()
        self.LED_matrix.close_serial()
        self.arduino.close_serial()

    def run(self):
        try:
            while True:
                try:
                    row = self.data_processor.get_random_row()
                    vectors = [float(value) for value in row['Vectors']]
                    print(f"Processing index: {row.name}, Countries: {row['Countries']}, Keywords: {row['Keywords']}  Label and vectors: {[row['Label']] +  list(row['Vectors'])}")

                    if pd.notnull(row['Keywords']): self.LED_matrix.send_serial(row['Keywords'])
            
                    if pd.notnull(row['Media']): 
                        self.media_player.queue_media(row['Media']) 
                        print(f'found media {row["Media"]}')

                    self.semantic_model(row['Label'], vectors)

                    if isinstance(row['Countries'], list) and len(row['Countries']) > 0: self.ding_model.run(row['Countries'])

                    sleep(self.delay) 
                except Exception as e:
                    print(f"Error processing row: {e}")
        except KeyboardInterrupt:
            print('user ending program!')
        except Exception as e:
            print(f'Error running main loop: {e}')
        finally:
            self.cleanup()
            
if __name__ == "__main__":
    try: 
        main_program = MainProgram()
        main_program.run()
    except Exception as e:
        print(f'Error running main program: {e}')
