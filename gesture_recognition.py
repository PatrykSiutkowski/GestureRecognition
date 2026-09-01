#!/usr/bin/env python3

import mediapipe as mp
import cv2
import time
import argparse
import subprocess
import re
import time

# Argument Parsing
parser = argparse.ArgumentParser()
parser.add_argument("--mode"     , type=str, default="livestream", help="choose between livestream or image mode")
parser.add_argument("--gui"      , type=str, default="true"      , help="choose visible GUI for livestream mode")
parser.add_argument("--volumebar", type=str, default="false"     , help="choose visible volumebar for livestream mode")
parser.add_argument("--printgest", type=str, default="true"      , help="choose visible volumebar for livestream mode")
args = parser.parse_args()

# MediaPipe Tasks
BaseOptions              = mp.tasks.BaseOptions
GestureRecognizer        = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
VisionRunningMode        = mp.tasks.vision.RunningMode

# Paths
model_path = "gesture_recognizer.task"
image_path = "photo_from_2026_03_21_22_51_51.094174.jpeg"

# Flags
running         = True 
terminal_opened = False

# Get current volume level using pactl
def get_volume():
  result = subprocess.run(['pactl', 'get-sink-volume', '@DEFAULT_SINK@'], capture_output=True, text=True)
  output = result.stdout
  
  match = re.search(r"(\d+)%", output)
  if match:
    print(f"Current volume: {match.group(1)}%")
    return int(match.group(1))
  
  return 0  # Fallback safety return if no volume is found

def get_brightness():
  result = subprocess.run(['brightnessctl', 'get'], capture_output=True, text=True)
  output = result.stdout.strip()
  
  if output.isdigit():
    print(f"Current brightness: {output}")
    return int(output)
  
  return 0  # Fallback safety return if no brightness is found

def get_internal_monitor():
  get_internal_monitor_status = subprocess.run(['xrandr', '--listmonitors'], capture_output=True, text=True)
  for line in get_internal_monitor_status.splitlines():
    if line.startswith(' '):
      parts = line.split()
      print(parts[-1])

  if parts == "HDMI-1" or parts == "DP-1" or parts == "DP-2":
    return False  # Return False if the monitor is external

  else:
    return True  # Return True if the monitor is internal

# Print the result of gesture recognition and perform actions based on detected gestures
def print_result(result):
  global terminal_opened, running, gui_bool

  detected = False

  if result.gestures:
    for gesture_list in result.gestures:
      for gesture in gesture_list:
        
        if printgest_bool == True: 
          print(f"{gesture.category_name}")

  elif not detected:
    terminal_opened = False

  else:
    print("No gestures detected")

# Match detected gestures with corresponding actions
def match_gesture(result, output_image, timestamp_ms):
    global terminal_opened, running, gui_bool, detected, volumebar_bool

    # No gesture detected
    if not result.gestures or not result.gestures[0]:
      return

    # Get the first detected gesture
    gesture = result.gestures[0][0].category_name
    print_result(result)


    match (gesture, volumebar_bool):
      case ("Pointing_Up", True | False):
          detected = True

          if not terminal_opened:
            terminal_opened = True
            gui_bool = not gui_bool

      case ("Open_Palm", True | False):
        if get_internal_monitor() == True and get_brightness() < 100:
            subprocess.run([
            'brightnessctl',
            'set',
            '10%+'])
        
        else:
          subprocess.run(['ddcutil', 'setvcp', '10', '+', '2'], capture_output=True, text=True)

      case ("Closed_Fist", True | False):
        if get_internal_monitor() == True and get_brightness() > 0:
          subprocess.run([
          'brightnessctl',
          'set',
          '10%-'])

        else:
          subprocess.run(['ddcutil', 'setvcp', '10', '-', '2'], capture_output=True, text=True)

      case ("Thumb_Up", True | False):
          # Volume change without volume bar
          if get_volume() < 100:
              subprocess.run([
                  'pactl',
                  'set-sink-volume',
                  '@DEFAULT_SINK@',
                  '+2%'
                ])

      case ("Thumb_Down", True | False):
          # Volume change without volume bar
          if get_volume() > 0:
              subprocess.run([
                  'pactl',
                  'set-sink-volume',
                  '@DEFAULT_SINK@',
                  '-2%',
              ])

      case ("ILoveYou", True | False):
          detected = True

          if not terminal_opened:
              terminal_opened = True
              subprocess.run(
                  'systemctl suspend',
                  shell=True
              )

      case ("Victory", True | False):
          print("Exiting program via gesture.")
          running = False
          return

      case ("None", True | False):
            pass

# Recognize gestures in livestream mode
def livestream_mode():
  options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=match_gesture)


  # Alternative camera indices to try if the default camera is not available
  camera_indices = [0, 1, 2]
  cap = None

  for index in camera_indices:
    test_cap = cv2.VideoCapture(index)

    if test_cap.isOpened():
      ret, frame = test_cap.read()

      if ret:
        cap = test_cap
        print(f"Using camera {index}")
        break

      test_cap.release()

  if cap is None:
      raise RuntimeError("No working camera found")

  with GestureRecognizer.create_from_options(options) as recognizer:
    while cap.isOpened() and running:
      ret, frame = cap.read()
      if not ret:
        break
  
      rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # Convert BGR (OpenCV) to RGB (MediaPipe)

      mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame)

      timestamp_ms = int(time.time() * 1000) # Timestamp required for live mode
      recognizer.recognize_async(mp_image, timestamp_ms)
      
      if gui_bool == True:
        cv2.imshow("Gesture Recognition", frame) # Show camera feed
      else:
        cv2.destroyAllWindows()
      
      if cv2.waitKey(1) & 0xFF == 27:  # exit using ESC key
        break

  cap.release()
  cv2.destroyAllWindows()

# Convert string arguments to boolean values
def args_to_bool(gui, volumebar, printgest):
  if gui == "true":
    gui_bool = True
  else:
    gui_bool = False

  if volumebar == "true":
    volumebar_bool = True
  else:
    volumebar_bool = False

  if printgest == "true":
    printgest_bool = True
  else:
    printgest_bool = False

  return volumebar_bool, gui_bool, printgest_bool

if __name__ == "__main__":
  mode      = args.mode
  gui       = args.gui
  volumebar = args.volumebar
  printgest = args.printgest

  volumebar_bool, gui_bool, printgest_bool = args_to_bool(gui, volumebar, printgest)
  
  if mode.lower() == "livestream":
    last_brightness_change = 0
    brightness_cooldown = 0.5
    current_time = time.time()

    if current_time - last_brightness_change >= brightness_cooldown:
      livestream_mode()

  else:
    raise TypeError("Invalid mode selected, rerun and enter either: \"image\" or \"livestream\"") # Handling for invalid args
