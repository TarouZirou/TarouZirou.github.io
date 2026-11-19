import math
import struct
import wave

sample_rate = 48000
count = round(1.6 * sample_rate)
fade = round(0.020 * sample_rate)
pcm = bytearray()
for n in range(count):
    t = n / sample_rate
    env = min(1.0, n / fade, (count - 1 - n) / fade)
    x = 0.12 * env * (math.sin(math.tau * 440 * t)
                    + math.sin(math.tau * 442 * t))
    pcm.extend(struct.pack("<h", round(x * 32767)))

with wave.open("beats-2hz.wav", "wb") as output:
    output.setnchannels(1)
    output.setsampwidth(2)
    output.setframerate(sample_rate)
    output.writeframes(pcm)
