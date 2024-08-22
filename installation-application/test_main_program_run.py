import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from main import MainProgram

class TestMainProgramRun(unittest.TestCase):

    @patch('main.sleep', return_value=None)  # Mock sleep to speed up the test
    @patch('main.DataProcessor.get_random_row')
    @patch('main.SerialCommunication')
    def test_run_single_row(self, MockSerialCommunication, MockGetRandomRow, MockSleep):
        # Setup a mock row as a Pandas Series
        mock_row = pd.Series({
            'Vectors': [0.1, 0.2, 0.3, 0.4],
            'Countries': ['Country1', 'Country2'],
            'Keywords': 'Keyword1',
            'Media': 'media_file',
            'Label': 1
        }, name=0)  # The 'name' attribute represents the index of the row

        MockGetRandomRow.return_value = mock_row

        # Mock the SerialCommunication instance
        mock_serial_instance = MockSerialCommunication.return_value
        mock_serial_instance.send_serial = MagicMock()

        # Initialize the program
        program = MainProgram()

        # Mock methods that interact with external resources
        program.LED_matrix = mock_serial_instance
        program.media_player.queue_media = MagicMock()
        program.ding_model.run = MagicMock()

        # Simulate the loop to process a single row
        program.run_once = True  # Custom attribute to control loop
        try:
            while program.run_once:
                program.run_once = False
                program.run()  # Run one iteration
        except StopIteration:
            pass

        # Assertions to check if methods were called with expected values
        mock_serial_instance.send_serial.assert_called_once_with('Keyword1')
        program.media_player.queue_media.assert_called_once_with('media_file')
        program.ding_model.run.assert_called_once_with(['Country1', 'Country2'])

if __name__ == '__main__':
    unittest.main()
