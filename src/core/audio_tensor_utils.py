from typing import Any, Optional, Tuple


def upmix_mono_to_stereo(wav_data: Any) -> Tuple[Any, Optional[str]]:
    """
    Upmix mono tensors to stereo for supported Demucs input layouts.

    Args:
        wav_data: Tensor-like object (typically torch.Tensor) exposing `shape`
            and `repeat(*dims)`.

    Returns:
        (possibly_updated_tensor, layout_tag)
        layout_tag is:
          - "2d" for [1, samples] -> [2, samples]
          - "3d" for [batch, 1, samples] -> [batch, 2, samples]
          - None when no conversion is needed
    """
    shape = getattr(wav_data, "shape", None)
    if shape is None:
        raise TypeError("wav_data must expose a shape attribute")

    if len(shape) == 2 and shape[0] == 1:
        return wav_data.repeat(2, 1), "2d"

    if len(shape) == 3 and shape[1] == 1:
        return wav_data.repeat(1, 2, 1), "3d"

    return wav_data, None
