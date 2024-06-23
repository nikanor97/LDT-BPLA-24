import ast
import json
from uuid import UUID

from loguru import logger
from telegram.ext import Application

import settings
from common.rabbitmq.publisher import Publisher
from src.db.exceptions import ResourceAlreadyExists
from src.db.main_db_manager import MainDbManager
from src.db.projects.models import FrameMarkup, VerificationTag, Label, LabelBase, VideoStatusOption, Video, Project
from src.server.telegram_bot import notify_user

# quadcopter_uav
# airplane
# helicopter
# bird
# fixed-wing_uav
# SHIT

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


async def yolo_markup_processor(
    data: dict, publisher: Publisher, main_db_manager: MainDbManager, **kwargs
) -> None:
    INTERVAL_THRESHOLD = 15
    CONFIDENCE_THRESHOLD = 0.6

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

        content = await main_db_manager.projects.get_content_by_frame_id(session, frame_id)
        project = await Project.by_id(session, project_id)

        if content.notification_sent is False and project.msg_receiver is not None:
            application = Application.builder().token(settings.TELEGRAM_TOKEN).build()
            if isinstance(content, Video):
                base_path = settings.MEDIA_DIR / "video"
            else:
                base_path = settings.MEDIA_DIR / "photo"
            notification_success = await notify_user(application, project.msg_receiver, base_path / content.source_url)
            if notification_success:
                await main_db_manager.projects.set_notification_sent_status(session, content.id, status=True)

        labels: list[Label] = await main_db_manager.projects.get_labels_by_project(session, project_id)

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

    logger.info(f"New {len(frame_markup_items)} frame markup items created")