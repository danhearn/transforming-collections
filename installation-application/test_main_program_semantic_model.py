import unittest
from unittest.mock import MagicMock, patch
from main import MainProgram

class TestMainProgramSemanticModel(unittest.TestCase):

    @patch('subprocess.Popen')  # Correctly mock subprocess.Popen
    @patch('main.SemanticClient')  # Mock the SemanticClient class
    @patch('main.SerialCommunication.connect_serial', return_value=None)  # Prevent real serial connections
    @patch('main.SerialCommunication.close_serial', return_value=None)  # Prevent real serial disconnections
    @patch('main.MainProgram.cleanup', return_value=None)  # Prevent actual cleanup
    @patch('main.sleep', return_value=None)  # Mock sleep to speed up tests
    def test_semantic_model_positive_label(self, MockSleep, MockCleanup, MockCloseSerial, MockConnectSerial, MockSemanticClient, MockPopen):
        # Mock subprocess to avoid actual process creation
        mock_popen_instance = MockPopen.return_value
        mock_popen_instance.terminate.return_value = None
        mock_popen_instance.communicate.return_value = (b'output', b'error')
        mock_popen_instance.returncode = 0

        # Initialize the program with mocked components
        program = MainProgram()

        # Simulate calling the semantic_model method with a positive label
        vectors = [0.1, 0.2, 0.3, 0.4]
        program.semantic_model(1, vectors)

        # Ensure the send_vectors method on the positive_client was called with the correct parameters
        program.positive_client.send_vectors.assert_called_once_with('/positive', vectors)

    @patch('subprocess.Popen')  # Correctly mock subprocess.Popen
    @patch('main.SemanticClient')  # Mock the SemanticClient class
    @patch('main.SerialCommunication.connect_serial', return_value=None)  # Prevent real serial connections
    @patch('main.SerialCommunication.close_serial', return_value=None)  # Prevent real serial disconnections
    @patch('main.MainProgram.cleanup', return_value=None)  # Prevent actual cleanup
    @patch('main.sleep', return_value=None)  # Mock sleep to speed up tests
    def test_semantic_model_negative_label(self, MockSleep, MockCleanup, MockCloseSerial, MockConnectSerial, MockSemanticClient, MockPopen):
        # Mock subprocess to avoid actual process creation
        mock_popen_instance = MockPopen.return_value
        mock_popen_instance.terminate.return_value = None
        mock_popen_instance.communicate.return_value = (b'output', b'error')
        mock_popen_instance.returncode = 0

        # Initialize the program with mocked components
        program = MainProgram()

        # Simulate calling the semantic_model method with a negative label
        vectors = [0.1, 0.2, 0.3, 0.4]
        program.semantic_model(0, vectors)

        # Ensure the send_vectors method on the negative_client was called with the correct parameters
        program.negative_client.send_vectors.assert_called_once_with('/negative', vectors)

if __name__ == '__main__':
    unittest.main()
