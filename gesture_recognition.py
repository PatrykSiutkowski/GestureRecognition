#!/usr/bin/env python3

import mediapipe as mp
import cv2
import time
import argparse
import subprocess
import re

# Argument Parsing
parser = argparse.ArgumentParser()
parser.add_argument("--mode"      , type=str, default="livestream", help="choose between livestream or image mode")
parser.add_argument("--gui"       , type=str, default="true"      , help="choose visible GUI for livestream mode")
parser.add_argument("--volumebar" , type=str, default="false"     , help="choose visible volumebar for livestream mode")
parser.add_argument("--printgest" , type=str, default="true"      , help="choose visible volumebar for livestream mode")
args = parser.parse_args()

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

def get_volume():
    result = subprocess.run(['pactl', 'get-sink-volume', '@DEFAULT_SINK@'], capture_output=True, text=True)
    output = result.stdout
    
    match = re.search(r"(\d+)%", output)
    if match:
      return int(match.group(1))
    
    return 0  # Fallback safety return if no volume is found

def print_result(result, output_image, timestamp_ms):
  global terminal_opened, running, gui_bool

  detected = False

  if result.gestures:
    for gesture_list in result.gestures:
      for gesture in gesture_list:
        
        if printgest_bool == True: 
          print(f"{gesture.category_name}")
        
        match (gesture.category_name, volumebar_bool):
            
          case ("Pointing_Up", True | False):
            detected = True
            if not terminal_opened:
              terminal_opened = True
              gui_bool = not gui_bool

          case ("Open_Palm", True | False):
            subprocess.run(['brightnessctl', 'set', '10%+'])

          case ("Closed_Fist", True | False):
            subprocess.run(['brightnessctl', 'set', '10%-'], capture_output=True,text=True)

          case ("Thumb_Up", False): # volume change without volumebar
            if get_volume() < 100:
              subprocess.run(['pactl', 'set-sink-volume', '@DEFAULT_SINK@', '+2%'])
              subprocess.run(['pactl', 'get-sink-volume', '@DEFAULT_SINK@'])          
          
          case ("Thumb_Down", False): # volume change without volumebar
            if get_volume() > 0:
              subprocess.run(['pactl', 'set-sink-volume', '@DEFAULT_SINK@', '-2%'])
              subprocess.run(['pactl', 'get-sink-volume', '@DEFAULT_SINK@'])
          
          case ("Thumb_Up", True): # volume change with volumebar, by larger increments
            subprocess.run('xdotool key XF86AudioRaiseVolume',shell=True)
            # TODO: change the increments by which it increase/ decreases

          case ("Thumb_Down", True): # volume change with volumebar, by larger increments
            subprocess.run('xdotool key XF86AudioLowerVolume',shell=True)

            # TODO: change the increments by which it increase/ decreases

          case ("ILoveYou", True | False):
            detected = True
            if not terminal_opened:
              terminal_opened = True
              subprocess.run('systemctl suspend', shell=True)
          
          case ("Victory", True | False):
            print("Exiting program via gesture.")
            running = False
            return

          case "None":
            pass

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
    print_result(result, output_image=..., timestamp_ms=..., volumebar_bool=...)

def livestream_mode():
  options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=print_result)

  cap = cv2.VideoCapture(0)

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

  if mode.lower() == "image":
    image_mode()
  
  elif mode.lower() == "livestream":
    livestream_mode()

  else:
    print("Invalid mode selected, rerun and enter either: \"image\" or \"livestream\"") # Handling for invalid args
