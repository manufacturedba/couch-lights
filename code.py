import time
import board
import neopixel
import adafruit_lis3dh


# MatrixPortalM4
PIXEL_PIN = board.A3

MAX_BRIGHTNESS = 1

# NeoPixels count
NUM_PIXELS = 240

# Color order
COLOR_ORDER = neopixel.GRBW

PURPLE_RGB = (180, 0, 255)
GREEN_RGB = (0, 255, 0)
ALL_COLORS = [PURPLE_RGB, GREEN_RGB]

pixels = neopixel.NeoPixel(
    PIXEL_PIN, NUM_PIXELS, brightness=0.1, pixel_order=COLOR_ORDER
)

i2c = board.I2C()

# Accelerometer
lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x19)


# Set range of accelerometer (can be RANGE_2_G, RANGE_4_G, RANGE_8_G or RANGE_16_G).
lis3dh.range = adafruit_lis3dh.RANGE_2_G

lastx, lasty, lastz = [
    value / adafruit_lis3dh.STANDARD_GRAVITY for value in lis3dh.acceleration
]

timestamp = time.time()
current_color_index = 0
cooldown = 30
threshold = 0.03

pixels.fill(ALL_COLORS[current_color_index])
pixels.show()


def color_chase(color, wait):
    for i in range(NUM_PIXELS):
        pixels[i] = color
        time.sleep(wait)
        pixels.show()


current_brightness = MAX_BRIGHTNESS

while True:
    x, y, z = [
        value / adafruit_lis3dh.STANDARD_GRAVITY for value in lis3dh.acceleration
    ]

    largest = max([abs(x - lastx), abs(y - lasty), abs(z - lastz)])
    xdiff = abs(x - lastx)

    print('xdiff %s' % xdiff)

    brightness = round(min([abs(x), 1]), 3)

    print('brightness %s' % brightness)

    # Step up brightness
    while current_brightness < min([brightness, MAX_BRIGHTNESS]):
        current_brightness += 0.02
        pixels.brightness = current_brightness
        time.sleep(0.001)

    # Step down brightness
    while current_brightness > max([brightness, 0.1]):
        current_brightness -= 0.02
        pixels.brightness = current_brightness
        time.sleep(0.001)

    if xdiff >= threshold and time.time() - stamp > cooldown:
        stamp = time.time()
        current_color_index = (current_color_index + 1) % len(ALL_COLORS)
        color_chase(ALL_COLORS[current_color_index], 0.01)

    print("x = %0.3f G, y = %0.3f G, z = %0.3f G" % (x, y, z))
    # Small delay to keep things responsive but give time for interrupt processing.
    time.sleep(0.3)

    lastx = x
    lasty = y
    lastz = z
