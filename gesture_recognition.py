#!/usr/bin/env python3

import mediapipe as mp
import cv2
import time
import os
import subprocess

BaseOptions              = mp.tasks.BaseOptions
GestureRecognizer        = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
VisionRunningMode        = mp.tasks.vision.RunningMode

model_path = "gesture_recognizer.task"
image_path = "photo_from_2026_03_21_22_51_51.094174.jpeg"

terminal_opened = False

def print_result(result, output_image, timestamp_ms):
  global terminal_opened

  detected = False

  if result.gestures:
      for gesture_list in result.gestures:
          for gesture in gesture_list:
              print(f"{gesture.category_name}: {gesture.score:.2f}")

              if gesture.category_name == "Pointing_Up":
                  detected = True
                  if not terminal_opened:
                      terminal_opened = True
                      os.system('ptyxis -s')

  if not detected:
    terminal_opened = False

  else:
    print("No gestures detected")

def image_mode():
  mp_image = mp.Image.create_from_file(image_path)
    
  options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.IMAGE)

  with GestureRecognizer.create_from_options(options) as recognizer:
    result = recognizer.recognize(mp_image)
    print_result(result, output_image=..., timestamp_ms=...)

def livestream_mode():
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
  
      rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # Convert BGR (OpenCV) to RGB (MediaPipe)

      mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame)

      timestamp_ms = int(time.time() * 1000) # Timestamp required for live mode
      recognizer.recognize_async(mp_image, timestamp_ms)
      
      cv2.imshow("Gesture Recognition", frame) # Show camera feed

      if cv2.waitKey(1) & 0xFF == 27:  # exit using ESC key
        break

  cap.release()
  cv2.destroyAllWindows()

if __name__ == "__main__":
  vision_running_mode_selection = input("IMAGE or LIVESTREAM?: ")

  if vision_running_mode_selection.lower() == "image":
    image_mode()
  
  elif vision_running_mode_selection.lower() == "livestream":
    livestream_mode()

  else:
    quit