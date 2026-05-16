import importlib.util
import unittest
from pathlib import Path

try:
    import torch
except ModuleNotFoundError:
    torch = None


MODULE_PATH = (
    Path(__file__).resolve().parents[1] / "src" / "core" / "audio_tensor_utils.py"
)
SPEC = importlib.util.spec_from_file_location("audio_tensor_utils", MODULE_PATH)
audio_tensor_utils = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audio_tensor_utils)
upmix_mono_to_stereo = audio_tensor_utils.upmix_mono_to_stereo


class MockTensor:
    def __init__(self, shape):
        self.shape = shape
        self.repeat_calls = []

    def repeat(self, *dims):
        self.repeat_calls.append(dims)
        repeated_shape = tuple(size * repeat for size, repeat in zip(self.shape, dims))
        return MockTensor(repeated_shape)


class UpmixMonoToStereoTests(unittest.TestCase):
    def test_raises_for_invalid_input_without_shape(self):
        with self.assertRaises(TypeError):
            upmix_mono_to_stereo(object())

    def test_upmixes_2d_mono(self):
        wav_data = MockTensor((1, 48000))

        converted, layout = upmix_mono_to_stereo(wav_data)

        self.assertEqual(layout, "2d")
        self.assertEqual(wav_data.repeat_calls, [(2, 1)])
        self.assertEqual(converted.shape, (2, 48000))

    def test_upmixes_3d_mono_batch(self):
        wav_data = MockTensor((1, 1, 48000))

        converted, layout = upmix_mono_to_stereo(wav_data)

        self.assertEqual(layout, "3d")
        self.assertEqual(wav_data.repeat_calls, [(1, 2, 1)])
        self.assertEqual(converted.shape, (1, 2, 48000))

    def test_keeps_2d_stereo_unchanged(self):
        wav_data = MockTensor((2, 48000))

        converted, layout = upmix_mono_to_stereo(wav_data)

        self.assertIsNone(layout)
        self.assertIs(converted, wav_data)
        self.assertEqual(wav_data.repeat_calls, [])

    def test_keeps_3d_stereo_batch_unchanged(self):
        wav_data = MockTensor((1, 2, 48000))

        converted, layout = upmix_mono_to_stereo(wav_data)

        self.assertIsNone(layout)
        self.assertIs(converted, wav_data)
        self.assertEqual(wav_data.repeat_calls, [])

    @unittest.skipIf(torch is None, "torch is not installed")
    def test_upmixes_torch_2d_mono_preserving_dtype_and_device(self):
        wav_data = torch.ones((1, 48000), dtype=torch.float64)

        converted, layout = upmix_mono_to_stereo(wav_data)

        self.assertEqual(layout, "2d")
        self.assertEqual(tuple(converted.shape), (2, 48000))
        self.assertEqual(converted.dtype, wav_data.dtype)
        self.assertEqual(converted.device, wav_data.device)
        self.assertTrue(torch.equal(converted[0], wav_data[0]))
        self.assertTrue(torch.equal(converted[1], wav_data[0]))

    @unittest.skipIf(torch is None, "torch is not installed")
    def test_upmixes_torch_3d_mono_batch_preserving_dtype_and_device(self):
        wav_data = torch.ones((1, 1, 48000), dtype=torch.float32)

        converted, layout = upmix_mono_to_stereo(wav_data)

        self.assertEqual(layout, "3d")
        self.assertEqual(tuple(converted.shape), (1, 2, 48000))
        self.assertEqual(converted.dtype, wav_data.dtype)
        self.assertEqual(converted.device, wav_data.device)
        self.assertTrue(torch.equal(converted[:, 0], wav_data[:, 0]))
        self.assertTrue(torch.equal(converted[:, 1], wav_data[:, 0]))

    @unittest.skipIf(torch is None, "torch is not installed")
    def test_keeps_torch_stereo_tensors_unchanged(self):
        stereo_2d = torch.zeros((2, 48000), dtype=torch.float32)
        stereo_3d = torch.zeros((1, 2, 48000), dtype=torch.float32)

        converted_2d, layout_2d = upmix_mono_to_stereo(stereo_2d)
        converted_3d, layout_3d = upmix_mono_to_stereo(stereo_3d)

        self.assertIsNone(layout_2d)
        self.assertIs(converted_2d, stereo_2d)
        self.assertIsNone(layout_3d)
        self.assertIs(converted_3d, stereo_3d)


if __name__ == "__main__":
    unittest.main()
