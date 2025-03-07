import unittest
from unittest.mock import patch

from renardo_lib.Shabda import LOOP_PATH, SHABDA_URL, generate


class TestShabdaSamples(unittest.TestCase):
    @patch('renardo_lib.Shabda.urlretrieve')
    def test_download_sample(self, mock_urlretrieve):
        sample_name = 'test'
        sample_quantity = '1'

        definition = f'{sample_name}:{sample_quantity}'
        sample_filepath = f'{sample_name}/{sample_name}_0.wav'
        sample_urlpath = f'samples/{sample_filepath}'

        with patch(
            'renardo_lib.Shabda.get_sample_list',
            return_value={sample_name: [sample_urlpath]},
        ) as mock_get_sample_list:
            generate(definition)

        mock_get_sample_list.assert_called_once_with(definition, {'strudel': 1})
        mock_urlretrieve.assert_called_once_with(
            SHABDA_URL + sample_urlpath, LOOP_PATH / sample_filepath
        )


class TestShabdaSpeech(unittest.TestCase):
    @patch('renardo_lib.Shabda.urlretrieve')
    def test_download_sample(self, mock_urlretrieve):
        text_to_speech = 'magnifique'
        language = 'fr-FR'
        gender = 'm'

        sample_filepath = f'{text_to_speech}/{text_to_speech}_{language}_{gender}.wav'
        sample_urlpath = f'speech_samples/{sample_filepath}'

        definition = f'speech/{text_to_speech}'
        params = {'gender': gender, 'language': language, 'strudel': 1}

        with patch(
            'renardo_lib.Shabda.get_sample_list',
            return_value={text_to_speech: [sample_urlpath]},
        ) as mock_get_sample_list:
            generate(definition, params)

        mock_get_sample_list.assert_called_once_with(definition, params)
        mock_urlretrieve.assert_called_once_with(
            SHABDA_URL + sample_urlpath, LOOP_PATH / sample_filepath
        )


if __name__ == "__main__":
    unittest.main()
