import unittest
from unittest.mock import patch, MagicMock
from ding import DingModel  # Replace 'ding' with the actual module name

class TestDingModel(unittest.TestCase):

    @patch('ding.json.load')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('ding.MidiFile')
    def setUp(self, MockMidiFile, mock_open, mock_json_load):
        # Mock data for json.load
        mock_json_load.return_value = {
            "malaysia": {
                "track1": "malaysia_track1.mid",
                "track2": "malaysia_track2.mid"
            },
            "no-country": {
                "track1": "no_country_track1.mid"
            }
        }

        # Mock Arduino object
        self.mock_arduino = MagicMock()

        # Mock MidiFile constructor to return a mock object instead of loading a file
        self.mock_midi_file_instance = MagicMock()
        MockMidiFile.return_value = self.mock_midi_file_instance

        # Mock the play method of the MidiFile instance
        self.mock_midi_file_instance.play.return_value = [
            MagicMock(type='note_on', note=60),
            MagicMock(type='note_on', note=70),
        ]

        # Initialize the DingModel with the mocked data
        self.ding_model = DingModel(self.mock_arduino, "fake_path_to_json")

    def test_read_midi(self):
        # Call the method
        self.ding_model.read_midi(self.mock_midi_file_instance)

        # Check if the correct notes were sent to the Arduino
        self.mock_arduino.send_serial.assert_any_call(18)  # 60 - 42 = 18
        self.mock_arduino.send_serial.assert_any_call(28)  # 70 - 42 = 28
        self.assertEqual(self.mock_arduino.send_serial.call_count, 2)

    @patch('ding.random.random', return_value=0.4)  # Mock random to always return 0.4
    def test_track_selector_two_tracks_first(self, mock_random):
        # Test track_selector with two tracks and random selecting the first track
        self.ding_model.track_selector("malaysia", 2)
        
        # Ensure the correct file was "opened" by MidiFile
        self.mock_midi_file_instance.assert_called_once_with("malaysia_track1.mid")

    @patch('ding.random.random', return_value=0.6)  # Mock random to always return 0.6
    def test_track_selector_two_tracks_second(self, mock_random):
        # Test track_selector with two tracks and random selecting the second track
        self.ding_model.track_selector("malaysia", 2)
        
        # Ensure the correct file was "opened" by MidiFile
        self.mock_midi_file_instance.assert_called_once_with("malaysia_track2.mid")

    def test_track_selector_one_track(self):
        # Test track_selector with one track
        self.ding_model.track_selector("no-country", 1)
        
        # Ensure the correct file was "opened" by MidiFile
        self.mock_midi_file_instance.assert_called_once_with("no_country_track1.mid")

    @patch.object(DingModel, 'track_selector')  # Patch track_selector to avoid calling read_midi
    def test_run(self, mock_track_selector):
        # Test run with a list of countries
        countries = ["Malaysia", "Myanmar", "Unknown"]
        
        self.ding_model.run(countries)
        
        # Check if the correct calls were made to track_selector
        mock_track_selector.assert_any_call("malaysia", 2)
        mock_track_selector.assert_any_call("myanmar", 1)
        mock_track_selector.assert_any_call("no-country", 1)

if __name__ == '__main__':
    unittest.main()
