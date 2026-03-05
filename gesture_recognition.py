#!/usr/bin/env python3

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

model_path = "/home/patryksiutkowski/GitHub/GestureRecognition/gesture_recognizer.task"
mp_image = mp.Image.create_from_file("/home/patryksiutkowski/GitHub/GestureRecognition/Photo_from_2026-03-05_18-28-41.977291.jpeg")
#mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=numpy_image)

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Create a gesture recognizer instance with the image mode:
options = GestureRecognizerOptions(
  base_options=BaseOptions(model_asset_path=model_path),
  running_mode=VisionRunningMode.IMAGE)

with GestureRecognizer.create_from_options(options) as recognizer:
  gesture_recognition_result = recognizer.recognize(mp_image)
  print(gesture_recognition_result)