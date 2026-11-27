import unittest
import cv2
import numpy as np

from face_validation import extract_single_face


class FaceValidationTest(unittest.TestCase):
    def test_non_image_and_non_face_are_rejected(self):
        self.assertIsNone(extract_single_face(b"not an image"))
        ok, encoded = cv2.imencode(".jpg", np.zeros((256, 256, 3), dtype=np.uint8))
        self.assertTrue(ok)
        self.assertIsNone(extract_single_face(encoded.tobytes()))
