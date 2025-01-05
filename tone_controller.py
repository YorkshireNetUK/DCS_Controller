import numpy as np
import pyaudio
from scipy.fftpack import fft
import RPi.GPIO as GPIO
import json
import time

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
THRESHOLD = 500

STATUS_FILE = "/var/www/html/tone_status.json"  # Accessible by PHP

GPIO.setmode(GPIO.BCM)

def load_tone_config(file_path):
    """Load tones, output GPIOs, input GPIOs, and callsigns from configuration file."""
    tone_map = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):  # Skip comments and blank lines
                continue
            try:
                parts = line.split(',')
                tone, output_gpio, input_gpio = map(int, parts[:3])
                callsign = parts[3] if len(parts) > 3 else "Unknown"
                tone_map.append((tone, output_gpio, input_gpio, callsign))
            except ValueError:
                print(f"Skipping invalid line: {line}")
    return tone_map

def setup_gpio_pins(tone_map):
    """Set up GPIO pins as outputs and inputs."""
    configured_pins = set()
    for _, output_gpio, input_gpio, _ in tone_map:
        if output_gpio not in configured_pins:
            GPIO.setup(output_gpio, GPIO.OUT)
            GPIO.output(output_gpio, GPIO.LOW)
            configured_pins.add(output_gpio)
        if input_gpio not in configured_pins:
            GPIO.setup(input_gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            configured_pins.add(input_gpio)

def detect_tone(data, target_freq):
    """Detect if the target frequency is present in the audio."""
    audio_data = np.frombuffer(data, dtype=np.int16)
    fft_data = fft(audio_data)
    magnitude = np.abs(fft_data[:CHUNK // 2])
    frequencies = np.fft.fftfreq(len(audio_data), 1 / RATE)[:CHUNK // 2]
    target_index = np.where((frequencies > target_freq - 10) & (frequencies < target_freq + 10))
    return np.max(magnitude[target_index]) > THRESHOLD

def update_status_file(callsign, status, timestamp):
    """Update the status JSON file."""
    try:
        # Read current status
        try:
            with open(STATUS_FILE, 'r') as file:
                current_status = json.load(file)
        except (IOError, json.JSONDecodeError):
            current_status = {}

        # Update the status for this callsign
        current_status[callsign] = {"status": status, "timestamp": timestamp}

        # Write updated status back to file
        with open(STATUS_FILE, 'w') as file:
            json.dump(current_status, file)
    except IOError as e:
        print(f"Error updating status file: {e}")

def main():
    tone_map = load_tone_config("/home/pi/tones_config.txt")
    setup_gpio_pins(tone_map)
    print(f"Loaded configuration: {tone_map}")

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    active_tones = {}

    try:
        print("Listening for tones...")
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            gpio_states = {}

            for tone, output_gpio, input_gpio, callsign in tone_map:
                if detect_tone(data, tone):
                    if GPIO.input(input_gpio) == GPIO.LOW:
                        gpio_states[output_gpio] = gpio_states.get(output_gpio, False) or True
                        if tone not in active_tones:
                            active_tones[tone] = time.strftime("%Y-%m-%d %H:%M:%S")
                            update_status_file(callsign, "active", active_tones[tone])
                            print(f"Tone {tone} ({callsign}) detected: Active.")
                    else:
                        print(f"Tone {tone} ({callsign}) detected, but input HIGH.")
                elif tone in active_tones:
                    finish_time = time.strftime("%Y-%m-%d %H:%M:%S")
                    update_status_file(callsign, "inactive", finish_time)
                    print(f"Tone {tone} ({callsign}) finished: Inactive.")
                    del active_tones[tone]

            # Update GPIO outputs
            for output_gpio in set(output_gpio for _, output_gpio, _, _ in tone_map):
                if gpio_states.get(output_gpio, False):
                    GPIO.output(output_gpio, GPIO.HIGH)
                else:
                    GPIO.output(output_gpio, GPIO.LOW)

    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        GPIO.cleanup()

if __name__ == "__main__":
    main()
