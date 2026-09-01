# Gesture Recoginser

## by: Patryk Siutkowski

### About:
A basic gesture recogniser using the media pipeline to control actions on a Linux based system.
Specfically: volume, brightness and suspend mode

## Description of the Algorithm

### `get_volume`

Fetches current volume level and trims output down to the number itself.

### `get_brightness`

Gets the current brightness level

### `get_external_monitor`

Checks if there are internal or external monitors

### `print_result`

Outputs the detected gesture

### `match_gesture`

Matches gesture via match case

### `livestream_mode`

Implements the livestream mode of mediapipe 

### `args_to_bool`

Converts the true and false args from str to bool
