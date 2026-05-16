import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1] / "src" / "core" / "audio_tensor_utils.py"
)
SPEC = importlib.util.spec_from_file_location("audio_tensor_utils", MODULE_PATH)
audio_tensor_utils = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audio_tensor_utils)
upmix_mono_to_stereo = audio_tensor_utils.upmix_mono_to_stereo


class TensorSpy:
    def __init__(self, shape):
        self.shape = shape
        self.repeat_calls = []

    def repeat(self, *dims):
        self.repeat_calls.append(dims)
        repeated_shape = tuple(size * repeat for size, repeat in zip(self.shape, dims))
        return TensorSpy(repeated_shape)


class UpmixMonoToStereoTests(unittest.TestCase):
    def test_upmixes_2d_mono(self):
        wav_data = TensorSpy((1, 48000))

        converted, layout = upmix_mono_to_stereo(wav_data)

        self.assertEqual(layout, "2d")
        self.assertEqual(wav_data.repeat_calls, [(2, 1)])
        self.assertEqual(converted.shape, (2, 48000))

    def test_upmixes_3d_mono_batch(self):
        wav_data = TensorSpy((1, 1, 48000))

        converted, layout = upmix_mono_to_stereo(wav_data)

        self.assertEqual(layout, "3d")
        self.assertEqual(wav_data.repeat_calls, [(1, 2, 1)])
        self.assertEqual(converted.shape, (1, 2, 48000))

    def test_keeps_2d_stereo_unchanged(self):
        wav_data = TensorSpy((2, 48000))

        converted, layout = upmix_mono_to_stereo(wav_data)

        self.assertIsNone(layout)
        self.assertIs(converted, wav_data)
        self.assertEqual(wav_data.repeat_calls, [])

    def test_keeps_3d_stereo_batch_unchanged(self):
        wav_data = TensorSpy((1, 2, 48000))

        converted, layout = upmix_mono_to_stereo(wav_data)

        self.assertIsNone(layout)
        self.assertIs(converted, wav_data)
        self.assertEqual(wav_data.repeat_calls, [])


if __name__ == "__main__":
    unittest.main()
