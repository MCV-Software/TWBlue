# -*- coding: utf-8 -*-
""" Helpers to turn arbitrary image data into wx.Image objects.

wx only knows about the image formats its own handlers support. Fediverse
instances (and Bluesky) happily serve avatars and headers in formats such as
WebP, which makes wx.Image fail and pop up a modal "Unknown image format"
error dialog, blocking the user. Pillow understands many more formats, so we
decode everything with it and hand the raw pixel data over to wx.
"""
from io import BytesIO
from logging import getLogger
from typing import Optional, Tuple, Union

import wx
from PIL import Image as PILImage

log = getLogger("mysc.image_utils")

ImageSource = Union[bytes, bytearray, str]

#: Pillow modes that carry per pixel transparency.
_TRANSPARENT_MODES = ("RGBA", "LA", "PA")


def decode_image(source: ImageSource) -> Tuple[int, int, bytes, Optional[bytes]]:
    """ Decodes an image into raw pixel data suitable for wx.

    :param source: Raw image bytes or a path to an image file.
    :returns: A (width, height, rgb_data, alpha_data) tuple. alpha_data is None
        when the image has no transparency.
    :raises Exception: Whatever Pillow raises when the data cannot be decoded.
    """
    if isinstance(source, (bytes, bytearray)):
        source = BytesIO(bytes(source))
    with PILImage.open(source) as image:
        image.load()
        has_alpha = image.mode in _TRANSPARENT_MODES or (image.mode == "P" and "transparency" in image.info)
        if has_alpha:
            image = image.convert("RGBA")
            return image.width, image.height, image.convert("RGB").tobytes(), image.getchannel("A").tobytes()
        image = image.convert("RGB")
        return image.width, image.height, image.tobytes(), None


def load_image(source: ImageSource) -> Optional[wx.Image]:
    """ Builds a wx.Image from raw image bytes or a path to an image file.

    :param source: Raw image bytes or a path to an image file.
    :returns: The decoded wx.Image, or None if the data could not be decoded.
        Callers are expected to skip drawing when None is returned, instead of
        letting wx show its own error dialog.
    """
    try:
        width, height, rgb_data, alpha_data = decode_image(source)
    except Exception:
        log.exception("Unable to decode image data.")
        return None
    image = wx.Image(width, height)
    image.SetData(rgb_data)
    if alpha_data is not None:
        image.SetAlpha(alpha_data)
    return image


def load_scaled_image(source: ImageSource, width: int, height: int) -> Optional[wx.Image]:
    """ Same as load_image, but rescales the result to the given size.

    :param source: Raw image bytes or a path to an image file.
    :param width: Width, in pixels, of the resulting image.
    :param height: Height, in pixels, of the resulting image.
    :returns: The rescaled wx.Image, or None if the data could not be decoded.
    """
    image = load_image(source)
    if image is None:
        return None
    image.Rescale(width, height, wx.IMAGE_QUALITY_HIGH)
    return image
