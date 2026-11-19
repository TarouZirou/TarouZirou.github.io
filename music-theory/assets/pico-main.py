from machine import ADC, PWM, Pin
from time import sleep_ms

NOTES = (60, 62, 64, 65, 67, 69, 71, 72)
FREQUENCIES = tuple(round(440 * 2 ** ((n - 69) / 12))
                    for n in NOTES)
STEP = 8192
MARGIN = 320

knob = ADC(Pin(26))
button = Pin(14, Pin.IN, Pin.PULL_UP)
speaker = PWM(Pin(15), freq=FREQUENCIES[0], duty_u16=0)

index = knob.read_u16() // STEP
previous = None
try:
    while True:
        value = knob.read_u16()
        while index < 7 and value >= (index + 1) * STEP + MARGIN:
            index += 1
        while index > 0 and value < index * STEP - MARGIN:
            index -= 1

        target = index if button.value() == 0 else None
        if target != previous:
            speaker.duty_u16(0)
            if target is not None:
                speaker.freq(FREQUENCIES[target])
                speaker.duty_u16(32768)
            previous = target
        sleep_ms(8)
finally:
    speaker.duty_u16(0)
    speaker.deinit()

