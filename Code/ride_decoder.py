# Run Length Decoder

import numpy as np
from enum import Enum, auto


class Code(Enum):
    COUNT = auto()
    COPY = auto()
    DUPLICATE = auto()


def leftBitRotate(n, d):
    return (n << d) | (n >> (32 - d))


def bytes_to_int(bytes):
    result = 0

    for b in bytes:
        result = result * 256 + int(b)

    return result


def int_to_bytes(value, length):
    result = []

    for i in range(0, length):
        result.append(value >> (i * 8) & 0xff)

    result.reverse()

    return result


def decode_ride(ride_name):
    #track_file = "test_raw.TD6"
    raw_ride_file = ride_name + ".TD6"
    encoded_bytes = np.fromfile(raw_ride_file, dtype=np.uint8)

    # Extract checksum
    checksum = encoded_bytes[-4:]
    encoded_bytes = encoded_bytes[0:-4]

    # Checksum Verification
    # TODO FIX
    print(bytes_to_int(checksum))
    # summation = [0, 0, 0, 0]
    # for b in encoded_bytes:
    #     summation[3] += b
    #     summation = int_to_bytes(leftBitRotate(
    #         bytes_to_int(summation), 3) - 108156, 4)

    # summation = 0
    # for b in encoded_bytes:
    #     summation += b

    summation = 0
    for b in encoded_bytes:
        #b2 = ((summation & 0xFF) + b) & 0xFF
        summation = (summation & 0xFFFFFF00) + (b & 0xFF)
        summation = leftBitRotate(summation, 3)

    print(summation)

    decoded_bytes = []
    counter = 0
    mode = Code.COUNT
    for b in encoded_bytes:
        if mode == Code.COUNT:
            counter = b
            # Check if Most Significant Bit is 0
            if (counter >> 7) == 0:
                mode = Code.COPY
                counter += 1
            else:
                mode = Code.DUPLICATE
                # Convert Unsigned Byte to Signed for Proper Count
                if counter > 127:
                    counter = (256 - counter) * (-1)
                counter = -counter + 1
        elif mode == Code.COPY:
            counter -= 1
            decoded_bytes.append(b)
            if counter == 0:
                mode = Code.COUNT
        elif mode == Code.DUPLICATE:
            for i in range(counter):
                decoded_bytes.append(b)
            mode = Code.COUNT

    # print(decoded_bytes)

    with open("decoded_" + ride_name + ".TD6", "wb") as f:
        f.write(bytes(decoded_bytes))
