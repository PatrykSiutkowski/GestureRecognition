#!/usr/bin/env python3

import mediapipe as mp
import os
import cv2
import time

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

model_path = "/home/patryksiutkowski/GitHub/GestureRecognition/gesture_recognizer.task"
image_path = "/home/patryksiutkowski/GitHub/GestureRecognition/photo_from_2026_03_21_22_51_51.094174.jpeg"

if not os.path.exists(model_path):
    raise FileNotFoundError("Model file not found")

if __name__ == "__main__":
  vision_running_mode_selection = input("IMAGE or LIVESTREAM?: ")

  if vision_running_mode_selection.lower() == "image":
    mp_image = mp.Image.create_from_file(image_path)
    
    options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.IMAGE)

    with GestureRecognizer.create_from_options(options) as recognizer:
      result = recognizer.recognize(mp_image)

    if result.gestures:
        for gesture_list in result.gestures:
            for gesture in gesture_list:
                print(f"{gesture.category_name}: {gesture.score}")
    else:
        print("No gestures detected")
  
  elif vision_running_mode_selection.lower() == "livestream":
    def print_result(result, output_image, timestamp_ms):
      if result.gestures:
          for gesture_list in result.gestures:
              for gesture in gesture_list:
                  print(f"{gesture.category_name}: {gesture.score:.2f}")

    options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=print_result)

    cap = cv2.VideoCapture(0)

    with GestureRecognizer.create_from_options(options) as recognizer:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Convert BGR (OpenCV) → RGB (MediaPipe)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb_frame
            )

            # Timestamp required for live mode
            timestamp_ms = int(time.time() * 1000)

            recognizer.recognize_async(mp_image, timestamp_ms)

            # Show camera feed
            cv2.imshow("Gesture Recognition", frame)

            if cv2.waitKey(1) & 0xFF == 27:  # ESC key
                break

    cap.release()
    cv2.destroyAllWindows()