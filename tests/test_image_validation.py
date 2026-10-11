from io import BytesIO

from PIL import Image

from services.vision_service import validate_image


def test_valid_image_is_accepted():
    output = BytesIO()
    Image.new("RGB", (4, 4), "green").save(output, format="PNG")
    assert validate_image(output.getvalue(), "image/png", 1)[0] is True


def test_invalid_image_and_type_are_rejected():
    assert validate_image(b"not an image", "image/png")[0] is False
    assert validate_image(b"data", "application/pdf")[0] is False
