import unittest
from unittest.mock import MagicMock, patch
from main import MainProgram

class TestMainProgramInitialization(unittest.TestCase):

    @patch('main.SemanticClient')
    @patch('main.SemanticModel')
    @patch('main.DataProcessor')
    @patch('main.SerialCommunication')
    @patch('main.DingModel')
    @patch('main.MediaPlayer')
    def test_initialization(self, MockMediaPlayer, MockDingModel, MockSerialCommunication, MockDataProcessor, MockSemanticModel, MockSemanticClient):
        # Initialize the program
        program = MainProgram()

        # Assertions for proper initialization
        MockSemanticClient.assert_called()
        MockSemanticModel.assert_called_once()
        MockDataProcessor.assert_called_once()
        MockSerialCommunication.assert_called()
        MockDingModel.assert_called_once()
        MockMediaPlayer.assert_called_once()

if __name__ == '__main__':
    unittest.main()
