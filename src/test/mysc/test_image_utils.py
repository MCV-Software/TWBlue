# -*- coding: utf-8 -*-
""" Tests for mysc.image_utils.

These are regression tests for the "Unknown image format" modal error dialog
that wx raised when a Mastodon instance served profile pictures in a format
wx cannot decode by itself, such as WebP.
"""
from io import BytesIO

import pytest
import wx
from PIL import Image as PILImage

from mysc import image_utils


@pytest.fixture(scope="module")
def app():
    """ wx needs an application object before image objects can be created. """
    application = wx.App()
    yield application
    application.Destroy()


def make_image_bytes(image_format, mode="RGB", size=(64, 32), color=(10, 20, 30)):
    """ Generates an in memory image in the requested format. """
    image = PILImage.new(mode, size, color)
    buffer = BytesIO()
    image.save(buffer, format=image_format)
    return buffer.getvalue()


@pytest.mark.parametrize("image_format", ["PNG", "JPEG", "GIF", "WEBP", "BMP"])
def test_decode_image_supports_common_formats(image_format):
    """ All formats served by fediverse instances should decode, WebP included. """
    width, height, rgb_data, alpha_data = image_utils.decode_image(make_image_bytes(image_format))
    assert (width, height) == (64, 32)
    assert len(rgb_data) == 64 * 32 * 3
    assert alpha_data is None


def test_decode_image_keeps_alpha_channel():
    """ Transparent images should keep their alpha channel separated for wx. """
    data = make_image_bytes("PNG", mode="RGBA", color=(10, 20, 30, 128))
    width, height, rgb_data, alpha_data = image_utils.decode_image(data)
    assert len(rgb_data) == width * height * 3
    assert alpha_data is not None
    assert len(alpha_data) == width * height
    assert set(alpha_data) == {128}


def test_decode_image_accepts_a_path(tmp_path):
    """ Images picked by the user are passed around as filesystem paths. """
    path = tmp_path / "avatar.webp"
    path.write_bytes(make_image_bytes("WEBP"))
    width, height, rgb_data, alpha_data = image_utils.decode_image(str(path))
    assert (width, height) == (64, 32)
    assert len(rgb_data) == 64 * 32 * 3


def test_decode_image_raises_on_invalid_data():
    with pytest.raises(Exception):
        image_utils.decode_image(b"this is definitely not an image")


@pytest.mark.parametrize("image_format", ["PNG", "JPEG", "GIF", "WEBP"])
def test_load_image_returns_a_wx_image(app, image_format):
    image = image_utils.load_image(make_image_bytes(image_format))
    assert image is not None
    assert image.IsOk()
    assert (image.GetWidth(), image.GetHeight()) == (64, 32)


def test_load_image_sets_alpha_on_transparent_images(app):
    image = image_utils.load_image(make_image_bytes("PNG", mode="RGBA", color=(10, 20, 30, 128)))
    assert image is not None
    assert image.HasAlpha()


def test_load_image_returns_none_on_invalid_data(app):
    """ Broken or unsupported data must not raise, so no error dialog is shown. """
    assert image_utils.load_image(b"not an image at all") is None


def test_load_image_returns_none_on_empty_data(app):
    """ Servers answering with an empty body should not break profile dialogs. """
    assert image_utils.load_image(b"") is None


def test_load_scaled_image_rescales(app):
    image = image_utils.load_scaled_image(make_image_bytes("WEBP"), 150, 150)
    assert image is not None
    assert (image.GetWidth(), image.GetHeight()) == (150, 150)


def test_load_scaled_image_returns_none_on_invalid_data(app):
    assert image_utils.load_scaled_image(b"nope", 150, 150) is None
