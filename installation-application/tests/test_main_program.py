import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import pandas as pd
from main import MainProgram
from data_processor import DataProcessor
from semantic_init import SemanticModel
# from semantic_client import SemanticClient, SerialCommunication, DingModel, MediaPlayer

class TestMainProgram(unittest.TestCase):
    
    @patch('main.SemanticClient')
    @patch('semantic_init.SemanticModel')
    @patch('data_processor.DataProcessor')
    @patch('main.SerialCommunication')
    @patch('main.DingModel')
    @patch('main.MediaPlayer')
    def test_initialization(self, MockMediaPlayer, MockDingModel, MockSerialCommunication, MockDataProcessor, MockSemanticModel, MockSemanticClient):
        # Mock instances
        mock_semantic_client = MockSemanticClient.return_value
        mock_semantic_model = MockSemanticModel.return_value
        mock_data_processor = MockDataProcessor.return_value
        mock_serial_com = MockSerialCommunication.return_value
        mock_ding_model = MockDingModel.return_value
        mock_media_player = MockMediaPlayer.return_value

        # Initialize the MainProgram
        program = MainProgram()

        # Check if instances are created properly
        MockSemanticClient.assert_any_call("127.0.0.1", 9000)
        MockSemanticClient.assert_any_call("127.0.0.1", 10000)
        MockSemanticModel.assert_called_once_with('pure_data/semantic_synth(with-effects).pd', Path.cwd() / 'data/tate_wellcome_SEA_text_embeddings.npy', 4)
        MockDataProcessor.assert_called_once_with(Path.cwd() / 'data/system-dataset-gif-test.csv', mock_semantic_model)
        MockSerialCommunication.assert_any_call(Path('/dev/tty.usbmodem2101'))
        MockSerialCommunication.assert_any_call(Path('/dev/tty.usbmodem2201'))
        MockDingModel.assert_called_once_with(mock_serial_com, Path.cwd() / 'data/country_tracks.json', base_path=Path.cwd())
        MockMediaPlayer.assert_called_once_with(Path.cwd() / 'data/gifs/', Path.cwd() / 'data/vids/', fullscreen=False)

    @patch('main.DataProcessor')
    @patch('main.SemanticClient')
    def test_run(self, MockSemanticClient, MockDataProcessor):
        # Mocking the DataProcessor and its method
        mock_data_processor = MockDataProcessor.return_value
        mock_data_processor.get_random_row.return_value = pd.Series({
            'Vectors': [0.1, 0.2, 0.3, 0.4],
            'Countries': ['Country1', 'Country2'],
            'Keywords': 'TestKeywords',
            'Media': 'TestMedia',
            'Label': 1
        })

        # Mocking other dependencies
        mock_semantic_client = MockSemanticClient.return_value

        program = MainProgram()
        program.data_processor = mock_data_processor 
        
        with patch('time.sleep', return_value=None):  # To avoid actual sleeping
            with patch('builtins.print') as mocked_print:  # To suppress and check print statements
                program.run()

                # Assertions based on mocked data
                mock_data_processor.get_random_row.assert_called_once()
                mock_semantic_client.send_vectors.assert_called_once_with("/positive", [0.1, 0.2, 0.3, 0.4])
                mocked_print.assert_any_call('Found media TestMedia')

    @patch('main.SemanticModel')
    def test_cleanup(self, MockSemanticModel):
        # Mocking SemanticModel
        mock_semantic_model = MockSemanticModel.return_value

        # Initialize the MainProgram
        program = MainProgram()
        program.cleanup()

        # Check if the resources are being cleaned up properly
        mock_semantic_model.pure_data.terminate.assert_called_once()
        program.LED_matrix.close_serial.assert_called_once()
        program.arduino.close_serial.assert_called_once()

if __name__ == '__main__':
    unittest.main()
