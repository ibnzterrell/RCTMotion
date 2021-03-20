
import numpy as np


def extract_track(ride_name):
    ride_file = "decoded_" + ride_name + ".TD6"
    ride_bytes = np.fromfile(ride_file, dtype=np.uint8)

    track_bytes = []

    i = 0xA3

    # Extract Track Data
    while i < len(ride_bytes) - 1:
        if ride_bytes[i] == 0xFF:
            break
        track_bytes.append(ride_bytes[i])
        track_bytes.append(ride_bytes[i+1])
        i += 2

    # Reset Track Layout to Station
    i = 0
    while i < len(track_bytes) - 1:
        # Find Begin Station 1: Track (0x02) with Qualifier (0x00)
        if (track_bytes[i] == 0x02 and track_bytes[i + 1] == 0x00):
            break
        i += 1
    # Re-Align Track
    track_bytes = track_bytes[i:] + track_bytes[:i]

    with open("extracted_" + ride_name + ".TD6", "wb") as f:
        f.write(bytes(track_bytes))
