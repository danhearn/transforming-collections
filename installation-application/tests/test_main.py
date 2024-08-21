import unittest
from unittest.mock import patch, MagicMock
from main import MainProgram  

NUMBER_OF_VECTORS = 4
CSV_PATH = '/Users/erika/Documents/GitHub/transforming-collections/installation-application/data/system-dataset-gif-test.csv'
PURE_DATA_PATH = '/Users/erika/Documents/GitHub/data-sonification/semantic_synth(with-effects).pd'
EMBEDDINGS_PATH = '/Users/erika/Documents/GitHub/transforming-collections/data/input/tate_wellcome_SEA_text_embeddings.npy'
LED_MATRIX_PATH = '/dev/tty.usbmodem2101'
ARUDUINO_PATH = '/dev/tty.usbmodem2201'
JSON_PATH = '/Users/erika/Documents/GitHub/transforming-collections/installation-application/data/country_tracks.json'
DELAY = 5

class TestMainProgramRun(unittest.TestCase):

    @patch('main.sleep', return_value=None)  # Mock sleep to avoid actual delays
    @patch('main.data_processor.DataProcessor')  # Mock DataProcessor
    @patch('main.serial_com.SerialCommunication')  # Mock SerialCommunication
    @patch('main.semantic_client.SemanticClient')  # Mock SemanticClient
    @patch('main.ding.DingModel')  # Mock DingModel
    @patch('main.semantic_init.SemanticModel')  # Mock SemanticModel
    def test_run(self, MockSemanticModel, MockDingModel, MockSemanticClient, MockSerialCom, MockDataProcessor, mock_sleep):
        # Mock instances
        mock_data_processor_instance = MockDataProcessor.return_value
        mock_serial_instance = MockSerialCom.return_value
        mock_ding_instance = MockDingModel.return_value
        
        # Mocking the return value of get_random_row to simulate one iteration
        mock_row = {
            'name': '1',
            'Countries': ['Country1'],
            'Keywords': 'Keyword',
            'Label': 1,
            'Vectors': [0.1, 0.2, 0.3, 0.4],
            'Gifs': 'gif-1'
        }
        mock_data_processor_instance.get_random_row.return_value = mock_row

        # Initialize the MainProgram instance
        main_program = MainProgram(
            CSV_PATH, NUMBER_OF_VECTORS, PURE_DATA_PATH, 
            EMBEDDINGS_PATH, LED_MATRIX_PATH, 
            ARUDUINO_PATH, JSON_PATH ,DELAY
        )

        # Use a side effect to stop the infinite loop after one iteration
        with patch('builtins.print') as mock_print:
            with self.assertRaises(KeyboardInterrupt):  # Simulate Ctrl+C after one loop
                main_program.run()

            # Assertions to verify the internal method calls
            mock_serial_instance.send_serial.assert_called_once_with('Keyword')
            mock_serial_instance.send_serial.assert_called_once_with('Keyword')
            mock_serial_instance.send_serial.assert_called_once_with('Keyword')
            mock_ding_instance.run.assert_called_once_with(['Country1'])
            mock_print.assert_any_call(f"Processing index: 1, Countries: {mock_row['Countries']}, Keywords: {mock_row['Keywords']}  Label and vectors: {[mock_row['Label']] +  list(mock_row['Vectors'])}")
            mock_print.assert_any_call('user ending program!')

if __name__ == '__main__':
    unittest.main()
