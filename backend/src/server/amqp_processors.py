import ast
import json
import tempfile
from collections import defaultdict
from pathlib import Path
from uuid import UUID
import aiofiles.os

from PIL import Image
from PIL import ImageDraw
from loguru import logger
from telegram.ext import Application

import settings
from common.rabbitmq.publisher import Publisher
from src.db.exceptions import ResourceAlreadyExists
from src.db.main_db_manager import MainDbManager
from src.db.projects.models import FrameMarkup, VerificationTag, Label, LabelBase, VideoStatusOption, Video, Project
from src.server.constants import tag_translation_eng_rus
from src.server.telegram_bot import notify_user


label_map = {
    "quadcopter_uav" : 0,
    "airplane" : 1,
    "helicopter": 2,
    "bird" : 3,
    "fixed-wing_uav" : 4
}

colors = [
    "#4f3721",
    "#395470",
    "#d62a80",
    "#d60aaa",
    "#6add23",
]

confidence_thresholds = {
    0: 0.5,
    1: 0.3,  # может, 0.4
    2: 0.3,
    3: 0.3,
    4: 0.4,
}


def add_annotations(image: Image, annotations: list[dict], label_by_id: dict[UUID, Label]):
    draw = ImageDraw.Draw(image)
    for annotation in annotations:
        top_left = (annotation["coord_top_left_x"], annotation["coord_top_left_y"])
        bottom_right = (annotation["coord_bottom_right_x"], annotation["coord_bottom_right_y"])
        confidence = annotation.get("confidence", None)

        # Рисуем прямоугольник
        draw.rectangle([top_left, bottom_right], outline="red", width=2)

        # Добавляем текст с confidence, если он есть
        if confidence is not None:
            label_name = label_by_id[annotation['label_id']].name
            text = f"{label_name}: {confidence:.2f}"
            draw.text((top_left[0], top_left[1] - 10), text, fill="red")


async def yolo_markup_processor(
    data: dict, publisher: Publisher, main_db_manager: MainDbManager, **kwargs
) -> None:

    # {'markup': '[(802, 305, 839, 336, 0, 0.7806294560432434)]', 'frame_id': 'a1425b2d-cfc5-4156-aaf9-a3d52662837e'}
    logger.info(f"Received from model: {data}")

    project_id = UUID(data["project_id"])
    frame_id = UUID(data["frame_id"])
    frames_in_content = int(data["frames_in_content"])
    markups = ast.literal_eval(data['markup'])

    labels_names = set(label_map.keys())
    labels_to_create = [LabelBase(
        name=label_name,
        description=label_name,
        color=color
    ) for label_name, color in list(zip(labels_names, colors))]

    async with main_db_manager.projects.make_autobegin_session() as session:
        labels: list[Label] = await main_db_manager.projects.get_labels_by_project(session, project_id)
        labels_to_create = [label for label in labels_to_create if label.name not in {label.name for label in labels}]
        try:
            await main_db_manager.projects.create_labels(session, project_id, labels_to_create)
        except ResourceAlreadyExists:
            pass
        await session.flush()

        labels: list[Label] = await main_db_manager.projects.get_labels_by_project(session, project_id)
        label_by_id = {label.id: label for label in labels}

    label_class_to_id = {label_map[label.name]: label.id for label in labels if label.name in label_map}

    frame_markup_items: list[FrameMarkup] = []
    for markup in markups:
        if markup[4] not in label_map.values():
            continue
        if markup[5] < confidence_thresholds[markup[4]]:
            continue
        frame_markup = FrameMarkup(
            frame_id=frame_id,
            label_id=label_class_to_id[markup[4]],
            coord_top_left_x=markup[0],
            coord_top_left_y=markup[1],
            coord_bottom_right_x=markup[2],
            coord_bottom_right_y=markup[3],
            confidence=markup[5],
        )
        frame_markup_items.append(frame_markup)

    async with main_db_manager.projects.make_autobegin_session() as session:
        content = await main_db_manager.projects.get_content_by_frame_id(session, frame_id)

        content_frames_counter = kwargs['content_frames_counter']
        content_frames_counter[content.id] += 1

        if content_frames_counter[content.id] == frames_in_content:
            content.status = VideoStatusOption.extracted
        else:
            content.status = VideoStatusOption.in_progress

        session.add_all(frame_markup_items)
        # тут обновлять еще счетчик маркапов в объектах контента

        content = await main_db_manager.projects.get_content_by_frame_id(session, frame_id)
        project = await Project.by_id(session, project_id)

        tags = await main_db_manager.projects.get_tags_by_project(
            session, project_id
        )
        label_to_verification_tag_mapping: dict[
            UUID, UUID] = await main_db_manager.projects.get_label_to_verification_tag_mapping(
            session, [t[0].id for t in tags]
        )
        tag_id_to_confidence = {t[0].id: t[1] for t in tags}

        for markup in markups:
            if label_class_to_id[markup[4]] in label_to_verification_tag_mapping:
                verification_tag_id = label_to_verification_tag_mapping[label_class_to_id[markup[4]]]
                if verification_tag_id in tag_id_to_confidence and markup[5] >= tag_id_to_confidence[verification_tag_id]:
                    if content.notification_sent is False and project.msg_receiver is not None:
                        await main_db_manager.projects.set_notification_sent_status(session, content.id, status=True)
                        await session.flush()
                        application = Application.builder().token(settings.TELEGRAM_TOKEN).build()
                        if isinstance(content, Video):
                            image_path = settings.MEDIA_DIR / data["image_path"]
                        else:
                            image_path = settings.MEDIA_DIR / data["image_path"]

                        # image_path = base_path / content.source_url
                        # Открыть изображение
                        image = Image.open(image_path)
                        draw = ImageDraw.Draw(image)

                        if image.mode == 'RGBA':
                            image = image.convert('RGB')

                        annotations = [fm.dict() for fm in frame_markup_items]

                        # Добавить разметку к изображению
                        add_annotations(image, annotations, label_by_id)

                        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
                            temp_image_path = tmp_file.name
                            image.save(temp_image_path)

                            if len(frame_markup_items) == 1:
                                caption = "Обнаружен объект!"
                            else:
                                caption = "Обнаружены объекты!"
                            for fm in frame_markup_items:
                                caption += f"\n{tag_translation_eng_rus[label_by_id[fm.label_id].name]}: {fm.confidence:.2f}"

                            notification_success = await notify_user(application, project.msg_receiver, temp_image_path, caption)
                            # if notification_success:

    if data["type"] == "video":
        # Path(settings.MEDIA_DIR / data["image_path"]).unlink()
        await aiofiles.os.remove(settings.MEDIA_DIR / data["image_path"])
    # Path(settings.MEDIA_DIR / (".".join(data["image_path"].split('.')[:-1]) + ".txt")).unlink()
    await aiofiles.os.remove(settings.MEDIA_DIR / (".".join(data["image_path"].split('.')[:-1]) + ".txt"))

    logger.info(f"New {len(frame_markup_items)} frame markup items created")
