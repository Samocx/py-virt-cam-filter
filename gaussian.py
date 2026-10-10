import cv2
import pyvirtualcam
import threading

from filter_config import Color, FilterConfig
from frame_processor import FrameProcessor

cap = cv2.VideoCapture("/dev/video0")

# TODO execute setup if no camera
if not cap.isOpened():
    print("No camera found. Please set up a virtual camera.")
    exit(1)


width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = 60


running = True
paused = False
config = FilterConfig()
processor = FrameProcessor(config)


def input_listener(config: FilterConfig, processor: FrameProcessor):
    """Listen cli and update params"""
    global running, paused
    pending_command = None

    while running:
        try:
            user_input = input().strip().lower()
            if not user_input:
                continue

            if pending_command is None:
                if user_input == 'b':
                    pending_command = 'blur'
                    print("Enter blur kernel size (odd integer >= 1):")
                elif user_input == 's':
                    pending_command = 'sigma'
                    print("Enter sigma value (float > 0):")
                elif user_input == 'h':
                    pending_command = 'history'
                    print("Enter history size (integer >= 1):")
                elif user_input == 'p':
                    pending_command = 'power'
                    print("Enter power value (float > 0):")
                elif user_input == 'g':
                    config.grayscale = not config.grayscale
                    print(f"Grayscale: {'On' if config.grayscale else 'Off'}")
                elif user_input == 'i':
                    config.invert_colors = not config.invert_colors
                    print(f"Invert Colors: {'On' if config.invert_colors else 'Off'}")
                elif user_input == 'c':
                    config.color = Color((config.color.value + 1) % len(Color))
                    print(f"Color: {config.color.name}")
                elif user_input == 'l':
                    pending_command = 'custom_color'
                    print("Enter custom color as R,G,B (0-255 each):")
                elif user_input == 't':
                    pending_command = 'color_threshold'
                    print("Enter color threshold (integer > 0):")
                elif user_input == 'z':
                    config.invert_color_threshold = not config.invert_color_threshold
                    print(f"Invert Color Threshold: {'On' if config.invert_color_threshold else 'Off'}")
                elif user_input == 'v':
                    paused = not paused
                    print(f"Virtual camera: {'Paused' if paused else 'Running'}")
                elif user_input in ('e', 'exit'):
                    running = False
                    print("Exiting...")
                else:
                    print("Unknown. Enter: b, s, h, p, g, i, c, t, z, e")
            else:
                try:
                    if pending_command == 'blur':
                        value = int(user_input)
                        config.blur_kernel = max(1, value)
                        if config.blur_kernel % 2 == 0:
                            config.blur_kernel += 1
                        print(f"Blur kernel: {config.blur_kernel}")
                    elif pending_command == 'sigma':
                        value = float(user_input)
                        config.sigma = max(0.01, value)
                        print(f"Sigma: {config.sigma}")
                    elif pending_command == 'history':
                        value = int(user_input)
                        processor.set_history_size(max(1, value))
                        print(f"History size: {config.history_size}")
                    elif pending_command == 'power':
                        value = float(user_input)
                        config.power = max(0.01, value)
                        print(f"Power: {config.power}")
                    elif pending_command == 'color_threshold':
                        value = int(user_input)
                        config.color_threshold = max(0, value)
                        print(f"Color Threshold: {config.color_threshold}")
                    elif pending_command == 'custom_color':
                        r, g, b = map(int, user_input.split(','))
                        config.custom_color = (r, g, b)
                        print(f"Custom Color: {config.custom_color}")
                except ValueError:
                    print("Invalid value. Enter valid number.")
                pending_command = None
        except EOFError:
            running = False

print("Controls:")
print("  b - Gaussian blur kernel")
print("  s - Gaussian sigma")
print("  h - history frame count")
print("  p - power transform")
print()
print("  g - Toggle grayscale")
print("  i - Toggle invert colors")
print("  c - Rotate color")
print("  l - Custom color")
print("  t - color threshold")
print("  z - invert color threshold")
print("  v - pause/resume virtual camera")
print()
print("  e or 'exit' - Exit")
print()

# listener thread
input_thread = threading.Thread(
    target=input_listener,
    args=(config, processor),
    daemon=True,
)
input_thread.start()

with pyvirtualcam.Camera(
    width=width,
    height=height,
    fps=fps,
    device="/dev/video10"
) as cam:
    last_output = None

    while running:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame. Exiting.")
            break

        if not paused or last_output is None:
            last_output = processor.process(frame)
        output = last_output

        # text overlay
        output_display = cv2.flip(cv2.cvtColor(output, cv2.COLOR_RGB2BGR), 1)
        cv2.putText(output_display, f"Blur: {config.blur_kernel}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.putText(output_display, f"Sigma: {config.sigma:.2f}", (10, 70), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.putText(output_display, f"History: {config.history_size}", (10, 110), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.putText(output_display, f"power: {config.power:.1f}", (10, 150), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.putText(output_display, f"grayscale: {'Yes' if config.grayscale else 'No'}", (10, 190), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.putText(output_display, f"invert: {'Yes' if config.invert_colors else 'No'}", (10, 230), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.putText(output_display, f"color: {config.color.name}", (10, 270), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.putText(output_display, f"threshold: {config.color_threshold} ({'inv' if config.invert_color_threshold else 'norm'})", (10, 310), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.imshow("Preview", output_display)
        cv2.waitKey(1)  # window refresh
        
        cam.send(output)
        cam.sleep_until_next_frame()

# Cleanup
cap.release()
cv2.destroyAllWindows()
print("Camera released. Exiting.")
