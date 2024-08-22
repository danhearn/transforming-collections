import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from main import MainProgram

class TestMainProgram(unittest.TestCase):

    @patch('main.sleep', return_value=None)  # Mock sleep to speed up the test
    @patch('main.MainProgram.semantic_model')
    @patch('main.MainProgram.cleanup')
    @patch('main.SerialCommunication')  # Mock the SerialCommunication class
    @patch('main.DataProcessor.get_random_row')
    def test_run(self, MockGetRandomRow, MockSerialCommunication, MockCleanup, MockSemanticModel, MockSleep):
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
        mock_serial_instance.connect_serial.return_value = None
        mock_serial_instance.send_serial = MagicMock()

        # Initialize the program
        program = MainProgram()

        # Mock methods that interact with external resources
        program.LED_matrix = mock_serial_instance
        program.media_player.queue_media = MagicMock()
        program.ding_model.run = MagicMock()

        # Simulate a single iteration of the loop by forcing StopIteration
        def mock_run_once():
            program.run_once = True  # Custom attribute to control loop
            try:
                while program.run_once:
                    program.run_once = False
                    program.run()  # Run one iteration
            except StopIteration:
                pass

        with patch.object(program, 'run', side_effect=StopIteration):
            with self.assertRaises(StopIteration):
                mock_run_once()

        # Assertions to check if methods were called with expected values
        mock_serial_instance.send_serial.assert_called_once_with('Keyword1')
        program.media_player.queue_media.assert_called_once_with('media_file')
        program.ding_model.run.assert_called_once_with(['Country1', 'Country2'])
        MockSemanticModel.assert_called_once_with(1, [0.1, 0.2, 0.3, 0.4])

if __name__ == '__main__':
    unittest.main()
