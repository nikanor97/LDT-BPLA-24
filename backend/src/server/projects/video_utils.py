import os

import cv2


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

    while success:
        # Читаем кадр
        success, frame = video_capture.read()
        if success:
            # Сохраняем только каждый второй кадр
            if frame_count % frame_step == 0:
                frame_filename = os.path.join(output_folder, f"{name_prefix}frame_{saved_frame_count:05d}.jpg")
                cv2.imwrite(frame_filename, frame)
                # Проверка, был ли кадр успешно сохранен
                if not os.path.isfile(frame_filename):
                    print(f"Не удалось сохранить кадр {frame_filename}")
                frame_filenames.append(frame_filename)
                saved_frame_count += 1
            frame_count += 1

    # Освобождаем видеофайл
    video_capture.release()


    # # Проверка существования видеофайла
    # if not os.path.isfile(video_path):
    #     print(f"Видео файл {video_path} не существует.")
    #     return []
    #
    # # Создаем выходную папку, если она не существует
    # if not os.path.exists(output_folder):
    #     os.makedirs(output_folder)
    #
    # # Открываем видеофайл
    # video_capture = cv2.VideoCapture(video_path)
    #
    # # Проверяем, удалось ли открыть видео
    # if not video_capture.isOpened():
    #     print(f"Не удалось открыть видео файл {video_path}")
    #     return []
    #
    # frame_count = 0
    # saved_frame_count = 0
    # frame_filenames = []
    #
    # while True:
    #     # Читаем кадр
    #     success, frame = video_capture.read()
    #     if not success:
    #         break
    #
    #     # Сохраняем только каждый второй кадр
    #     if frame_count % frame_step == 0:
    #         frame_filename = os.path.join(output_folder, f"frame_{saved_frame_count:05d}.jpg")
    #         cv2.imwrite(frame_filename, frame)
    #         frame_filenames.append(frame_filename)
    #         saved_frame_count += 1
    #
    #     frame_count += 1
    #
    # # Освобождаем видеофайл
    # video_capture.release()

    return frame_filenames
