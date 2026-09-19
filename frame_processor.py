from collections import deque

import cv2
import numpy as np

from filter_config import Color, FilterConfig


class FrameProcessor:
    def __init__(self, config: FilterConfig):
        self.config = config
        self.frames = deque(maxlen=config.history_size)

    def set_history_size(self, history_size: int):
        self.config.history_size = history_size
        self.frames = deque(self.frames, maxlen=history_size)

    def apply_blur(self, frame):
        blur_kernel = max(1, self.config.blur_kernel)
        if blur_kernel <= 1:
            return frame

        if blur_kernel % 2 == 0:
            blur_kernel += 1

        return cv2.GaussianBlur(
            frame,
            (blur_kernel, blur_kernel),
            self.config.sigma,
        )

    @staticmethod
    def convert_to_rgb(frame):
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def average_frames(self, frame):
        self.frames.append(frame.astype(np.float32))
        return np.clip(np.mean(self.frames, axis=0), 0, 255).astype(np.uint8)

    @staticmethod
    def apply_power(img, value):
        img = img / 1
        img -= np.min(img)
        maximum = np.max(img)
        if maximum > 0:
            img = img / maximum
        img = img ** value
        img = img * 255
        return np.clip(np.round(img), 0, 255)

    def apply_grayscale(self, frame):
        if not self.config.grayscale:
            return frame

        grayscale = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        return cv2.cvtColor(grayscale, cv2.COLOR_GRAY2RGB)

    def apply_color_filter(self, frame):
        color = self.config.color

        match color:
            case Color.NO:
                pass
            case Color.RED:
                frame[:, :, 1:] = 0
            case Color.ORANGE:
                frame[:, :, 1] = (frame[:, :, 1] * 0.5).astype(np.uint8)
                frame[:, :, 2] = 0
            case Color.YELLOW:
                frame[:, :, 2] = 0
            case Color.GREEN:
                frame[:, :, [0, 2]] = 0
            case Color.CYAN:
                frame[:, :, 0] = 0
            case Color.BLUE:
                frame[:, :, :2] = 0
            case Color.MAGENTA:
                frame[:, :, 1] = 0
            case Color.CUSTOM:
                custom_factors = np.array(self.config.custom_color, dtype=np.float32) / 255.0
                frame = np.clip(
                    frame.astype(np.float32) * custom_factors,
                    0,
                    255,
                ).astype(np.uint8)

        return frame

    def apply_threshold(self, frame, original_frame):
        threshold = self.config.color_threshold
        if threshold <= 0:
            return frame

        brightness = original_frame.max(axis=2)
        if self.config.invert_color_threshold:
            mask = brightness <= threshold
        else:
            mask = brightness > threshold

        for channel in range(3):
            frame[:, :, channel] = np.where(
                mask,
                frame[:, :, channel],
                original_frame[:, :, channel],
            )

        return frame

    def process(self, frame):
        frame = self.apply_blur(frame)
        frame = self.convert_to_rgb(frame)
        output = self.average_frames(frame)
        output = self.apply_power(output, self.config.power).astype(np.uint8)

        if self.config.invert_colors:
            output = 255 - output

        output = self.apply_grayscale(output)

        original_output = output.copy()
        output = self.apply_color_filter(output)
        return self.apply_threshold(output, original_output)
