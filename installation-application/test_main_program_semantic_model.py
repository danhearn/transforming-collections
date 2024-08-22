import unittest
from unittest.mock import MagicMock, patch
from main import MainProgram

class TestMainProgramSemanticModel(unittest.TestCase):

    @patch('subprocess.Popen')  # Mock subprocess.Popen
    @patch('main.SemanticClient')  # Mock the SemanticClient class
    @patch('main.SerialCommunication.connect_serial', return_value=None)  # Prevent real serial connections
    @patch('main.SerialCommunication.close_serial', return_value=None)  # Prevent real serial disconnections
    @patch('main.MainProgram.cleanup', return_value=None)  # Prevent actual cleanup
    @patch('main.sleep', return_value=None)  # Mock sleep to speed up tests
    def setUp(self, MockSleep, MockCleanup, MockCloseSerial, MockConnectSerial, MockSemanticClient, MockPopen):
        # Mock subprocess to avoid actual process creation
        self.mock_popen_instance = MockPopen.return_value
        self.mock_popen_instance.terminate.return_value = None
        self.mock_popen_instance.communicate.return_value = (b'output', b'error')
        self.mock_popen_instance.returncode = 0

        # Initialize the program with mocked components
        self.program = MainProgram()

        # Ensure cleanup is registered to avoid issues
        self.addCleanup(self.program.cleanup)
        self.addCleanup(self.mock_popen_instance.terminate)

    def test_semantic_model_positive_label(self):
        vectors = [0.1, 0.2, 0.3, 0.4]
        self.program.semantic_model(1, vectors)
        self.program.positive_client.send_vectors.assert_called_once_with('/positive', vectors)

    def test_semantic_model_negative_label(self):
        vectors = [0.1, 0.2, 0.3, 0.4]
        self.program.semantic_model(0, vectors)
        self.program.negative_client.send_vectors.assert_called_once_with('/negative', vectors)

if __name__ == '__main__':
    unittest.main()
