import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from seed_data import _ensure_seed_image


def test_seed_image_created():
    image_path = _ensure_seed_image()
    assert os.path.exists(image_path)
    assert image_path.endswith("seed_sheet_preview.png")
