import unittest
from unittest.mock import patch, MagicMock
import serial
from serial_com import SerialCommunication 

class TestSerialCommunication(unittest.TestCase):

    @patch('serial_com.os.path.exists')
    @patch('serial_com.serial.Serial')
    def test_connect_serial_success(self, mock_serial, mock_exists):
        # Mock the os.path.exists to return True (simulate device path exists)
        mock_exists.return_value = True

        # Initialize SerialCommunication
        serial_comm = SerialCommunication('/dev/ttyUSB0')

        # Call connect_serial and check that serial.Serial was called with correct parameters
        serial_comm.connect_serial()
        mock_serial.assert_called_once_with('/dev/ttyUSB0', 9600)
        self.assertTrue(serial_comm.serial_connected)

    @patch('serial_com.os.path.exists')
    @patch('serial_com.serial.Serial')
    def test_connect_serial_failure(self, mock_serial, mock_exists):
        # Mock the os.path.exists to return False (simulate device path does not exist)
        mock_exists.return_value = False

        # Initialize SerialCommunication
        serial_comm = SerialCommunication('/dev/ttyUSB0')

        # Call connect_serial and ensure serial.Serial was never called
        serial_comm.connect_serial()
        mock_serial.assert_not_called()
        self.assertFalse(serial_comm.serial_connected)

    @patch('serial_com.serial.Serial')
    def test_send_serial_success(self, mock_serial):
        # Mock the Serial object and its write method
        mock_ser_instance = MagicMock()
        mock_serial.return_value = mock_ser_instance

        # Initialize and connect the serial communication
        serial_comm = SerialCommunication('/dev/ttyUSB0')
        serial_comm.ser = mock_ser_instance
        serial_comm.serial_connected = True

        # Call send_serial and check that write was called with the correct parameters
        serial_comm.send_serial('test message')
        mock_ser_instance.write.assert_called_once_with(b'test message\n')

    @patch('serial_com.serial.Serial')
    def test_send_serial_not_connected(self, mock_serial):
        # Initialize SerialCommunication but do not connect
        serial_comm = SerialCommunication('/dev/ttyUSB0')

        # Call send_serial and ensure that write was not called because it's not connected
        serial_comm.send_serial('test message')
        mock_serial.return_value.write.assert_not_called()

    @patch('serial_com.serial.Serial')
    def test_send_serial_serial_exception(self, mock_serial):
        # Mock the Serial object and simulate a SerialException
        mock_ser_instance = MagicMock()
        mock_ser_instance.write.side_effect = serial.SerialException("Test SerialException")
        mock_serial.return_value = mock_ser_instance

        # Initialize and connect the serial communication
        serial_comm = SerialCommunication('/dev/ttyUSB0')
        serial_comm.ser = mock_ser_instance
        serial_comm.serial_connected = True

        # Call send_serial and ensure that the exception is handled
        with self.assertLogs(level='ERROR') as log:
            serial_comm.send_serial('test message')
            self.assertIn("Test SerialException", log.output[0])

    @patch('serial_com.serial.Serial')
    def test_close_serial_success(self, mock_serial):
        # Mock the Serial object and its close method
        mock_ser_instance = MagicMock()
        mock_serial.return_value = mock_ser_instance
        mock_ser_instance.is_open = True

        # Initialize and connect the serial communication
        serial_comm = SerialCommunication('/dev/ttyUSB0')
        serial_comm.ser = mock_ser_instance

        # Call close_serial and check that close was called
        serial_comm.close_serial()
        mock_ser_instance.close.assert_called_once()

    @patch('serial_com.serial.Serial')
    def test_close_serial_not_open(self, mock_serial):
        # Mock the Serial object with is_open set to False
        mock_ser_instance = MagicMock()
        mock_ser_instance.is_open = False
        mock_serial.return_value = mock_ser_instance

        # Initialize and connect the serial communication
        serial_comm = SerialCommunication('/dev/ttyUSB0')
        serial_comm.ser = mock_ser_instance

        # Call close_serial and ensure close was not called since is_open is False
        serial_comm.close_serial()
        mock_ser_instance.close.assert_not_called()

if __name__ == '__main__':
    unittest.main()
