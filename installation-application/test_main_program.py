import unittest
from unittest.mock import MagicMock, patch, call
from main import MainProgram 
from pathlib import Path # Import the class you want to test

# Define constants
BASE_PATH = Path.cwd()
NUMBER_OF_VECTORS = 4
CSV_PATH = BASE_PATH / 'data/system-dataset-gif-test.csv'
PURE_DATA_PATH =  'pure_data/semantic_synth(with-effects).pd'
EMBEDDINGS_PATH = BASE_PATH / 'data/tate_wellcome_SEA_text_embeddings.npy'
LED_MATRIX_PATH = Path('/dev/tty.usbmodem2101')
ARDUINO_PATH = Path('/dev/tty.usbmodem2201')
JSON_PATH = BASE_PATH / 'data/country_tracks.json'
DELAY = 1
GIFS_PATH = BASE_PATH / 'data/gifs/'
VIDS_PATH = BASE_PATH / 'data/vids/'

class TestMainProgram(unittest.TestCase):
    
    @patch('main.SemanticClient')
    @patch('main.SemanticModel')
    @patch('main.DataProcessor')
    @patch('main.SerialCommunication')
    @patch('main.DingModel')
    @patch('main.MediaPlayer')
    def test_initialization(self, MockMediaPlayer, MockDingModel, MockSerialCommunication, MockDataProcessor, MockSemanticModel, MockSemanticClient):
        # Initialize the program
        program = MainProgram()

        # Check if SemanticClient instances are initialized correctly
        calls = [call("127.0.0.1", 9000), call("127.0.0.1", 10000)]
        MockSemanticClient.assert_has_calls(calls, any_order=True)
        
        # Check the initialization of other components
        MockSemanticModel.assert_called_once_with(PURE_DATA_PATH, EMBEDDINGS_PATH, NUMBER_OF_VECTORS)
        MockDataProcessor.assert_called_once_with(CSV_PATH, MockSemanticModel())
        
        # Check the SerialCommunication calls
        MockSerialCommunication.assert_any_call(LED_MATRIX_PATH)
        MockSerialCommunication.assert_any_call(ARDUINO_PATH)
        MockSerialCommunication().connect_serial.assert_called()
        
        # Check DingModel initialization
        MockDingModel.assert_called_once_with(MockSerialCommunication(), JSON_PATH, base_path=BASE_PATH)
        
        # Check MediaPlayer initialization
        MockMediaPlayer.assert_called_once_with(GIFS_PATH, VIDS_PATH, fullscreen=False)
        MockMediaPlayer().start_on_new_process.assert_called()

if __name__ == '__main__':
    unittest.main()