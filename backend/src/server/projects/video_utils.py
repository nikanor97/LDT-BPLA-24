import os
from concurrent.futures import ThreadPoolExecutor

import cv2

import settings


def save_frame(frame, frame_filename):
    cv2.imwrite(frame_filename, frame)


def extract_frames(video_path, output_folder, name_prefix='', frame_step=2):
    # Создаем выходную папку, если она не существует
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Открываем видеофайл
    video_capture = cv2.VideoCapture(video_path)

    frame_count = 0
    saved_frame_count = 0
    success = True
    frame_filenames = []

    # Используем ThreadPoolExecutor для параллельного сохранения кадров
    with ThreadPoolExecutor(max_workers=settings.VIDEO_FRAMING_WORKERS) as executor:
        while success:
            # Читаем кадр
            success, frame = video_capture.read()
            if success:
                # Сохраняем только каждый второй кадр
                if frame_count % frame_step == 0:
                    frame_filename = os.path.join(output_folder, f"frame_{saved_frame_count:05d}.jpg")
                    executor.submit(save_frame, frame, frame_filename)
                    frame_filenames.append(frame_filename)
                    saved_frame_count += 1
                frame_count += 1

    # Освобождаем видеофайл
    video_capture.release()

    return frame_filenames
