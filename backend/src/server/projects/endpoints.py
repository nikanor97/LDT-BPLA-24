import io
import os
import re
import tempfile
import uuid
import zipfile
from collections import defaultdict
from decimal import Decimal
from typing import Optional, Annotated
from datetime import datetime

import aiofiles
import ffmpeg  # type: ignore
import pika
from PIL import Image
from loguru import logger

import settings
from fastapi import Header, HTTPException, UploadFile, Depends
from sqlalchemy.exc import NoResultFound

from common.rabbitmq.publisher import Publisher
from common.rabbitmq.sync_publisher import SyncPublisher

from src.db.exceptions import ResourceAlreadyExists
from src.db.main_db_manager import MainDbManager
from src.db.projects.models import (
    Frame,
    FrameMarkup,
    Label,
    LabelBase,
    Video,
    Project,
    ProjectBase,
    VerificationTag,
    VerificationTagBase,
    VideoStatusOption,
    Photo, FrameContentTypeOption,
)
from src.db.users.models import User
from src.server.auth_utils import oauth2_scheme, get_user_id_from_token
from src.server.common import UnifiedResponse, exc_to_str
from src.server.constants import tag_translation, colors, tag_translation_eng_rus, label_map, confidence_thresholds
from src.server.projects.models import (
    FramesWithMarkupRead,
    ProjectCreate,
    ProjectRead,
    ProjectWithUsers,
    BplaProjectStats,
    Content,
    ContentTypeOption,
    ProjectContentTypeOption,
    FrameMarkupReadMassive,
    VerificationTagWithConfidence,
    ChangeMarkupsOnFrame,
)
from starlette.requests import Request
from starlette.responses import Response, FileResponse
from starlette.templating import Jinja2Templates

from src.server.projects.video_utils import extract_frames

# TODO: remove templates after testing
templates = Jinja2Templates(directory="templates")


class ProjectsEndpoints:
    def __init__(self, main_db_manager: MainDbManager, publisher: Publisher) -> None:
        self._main_db_manager = main_db_manager
        self._publisher = publisher

    async def create_labels(
        self, project_id: uuid.UUID, labels: list[LabelBase]
    ) -> UnifiedResponse[list[Label]]:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                new_labels = await self._main_db_manager.projects.create_labels(
                    session, project_id, labels
                )
                return UnifiedResponse(data=new_labels)
            except ResourceAlreadyExists as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=409)
            except NoResultFound as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=404)

    async def get_labels_by_project_TMP(
        self, project_id: uuid.UUID
    ) -> UnifiedResponse[list[Label]]:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                labels = await self._main_db_manager.projects.get_labels_by_project(
                    session, project_id
                )
            except NoResultFound as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=404)
        for idx, label in enumerate(labels):
            if label.name in tag_translation_eng_rus:
                labels[idx].name = tag_translation_eng_rus[label.name]
        return UnifiedResponse(data=labels)

    async def delete_project(self, project_id: uuid.UUID) -> UnifiedResponse[Project]:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                project = await self._main_db_manager.projects.delete_project(
                    session, project_id
                )
                return UnifiedResponse(data=project)
            except NoResultFound as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=404)

    async def get_video_file(self, video_id: uuid.UUID, request: Request):
        try:
            async with self._main_db_manager.projects.make_autobegin_session() as session:
                video_db = await self._main_db_manager.projects.get_video(session, video_id)
                # TODO: make source_url not None in models and remove type ignore below
                video_src = settings.MEDIA_DIR / "video" / video_db.source_url  # type: ignore
                os.makedirs(settings.MEDIA_DIR / "video", exist_ok=True)
        except NoResultFound as e:
            raise HTTPException(status_code=404, detail=e.args)

        file_size = os.path.getsize(video_src)
        range_header = request.headers.get('Range')
        if range_header:
            range_match = re.search(r'bytes=(\d+)-(\d+)?', range_header)
            if range_match:
                start = int(range_match.group(1))
                end = range_match.group(2)
                if end is None:
                    end = file_size - 1
                else:
                    end = int(end)
                chunk_size = (end - start) + 1

                with open(video_src, 'rb') as video_file:
                    video_file.seek(start)
                    data = video_file.read(chunk_size)

                headers = {
                    'Content-Range': f'bytes {start}-{end}/{file_size}',
                    'Accept-Ranges': 'bytes',
                    'Content-Length': str(chunk_size),
                    'Content-Type': 'video/mp4',
                }
                return Response(content=data, status_code=206, headers=headers)

        headers = {
            'Content-Length': str(file_size),
            'Content-Type': 'video/mp4',
        }
        return FileResponse(video_src, headers=headers)

    async def create_verification_tags(
        self, tags: list[VerificationTagBase]
    ) -> UnifiedResponse[list[VerificationTag]]:
        # TODO: check creation of multiple objects where some of them already exist
        try:
            async with self._main_db_manager.projects.make_autobegin_session() as session:
                new_tags = (
                    await self._main_db_manager.projects.create_verification_tags(
                        session, tags
                    )
                )
        except ResourceAlreadyExists as e:
            return UnifiedResponse(error=exc_to_str(e), status_code=409)
        return UnifiedResponse(data=new_tags)

    async def get_all_verification_tags(
        self,
    ) -> UnifiedResponse[list[VerificationTagWithConfidence]]:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            tags = await self._main_db_manager.projects.get_all_verification_tags(
                session
            )
            res = [VerificationTagWithConfidence(
                id=tag.id,
                tagname=tag.tagname,
                groupname=tag.groupname,
                default_confidence=confidence_thresholds[label_map[tag_translation[tag.tagname]]]
            ) for tag in tags]
        return UnifiedResponse(data=res)

    async def _get_user_or_error(self, user_id: uuid.UUID) -> User | NoResultFound:
        """
        Method should be used only inside endpoints class.
        :return: User if user with user_id exists else NoResultFound error
        """
        async with self._main_db_manager.users.make_autobegin_session() as session:
            try:
                user = await self._main_db_manager.users.get_user(
                    session, user_id=user_id
                )
                return user
            except (NoResultFound, AssertionError) as e:
                return e

    async def get_frames_with_markups(
        self, content_id: uuid.UUID
    ) -> UnifiedResponse[list[FramesWithMarkupRead]]:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                frames = await self._main_db_manager.projects.get_frames_with_markups(
                    session, content_id
                )
                project_id = await self._main_db_manager.projects.get_project_id_by_content_id(
                    session, content_id
                )
                tags = await self._main_db_manager.projects.get_tags_by_project(
                    session, project_id
                )
                label_to_verification_tag_mapping: dict[uuid.UUID, uuid.UUID] = await self._main_db_manager.projects.get_label_to_verification_tag_mapping(
                    session, [t[0].id for t in tags]
                )
                tag_id_to_confidence = {t[0].id: t[1] for t in tags}
                frame_id_to_markups: defaultdict[uuid.UUID, list[FrameMarkupReadMassive]] = defaultdict(list)
                # TODO: ненужная логика. надо пересмотреть подход с verification_tag и лейблами
                for idx, frame in enumerate(frames):
                    for idx_markup, markup in enumerate(frame.markups):
                        if markup.label_id in label_to_verification_tag_mapping:
                            verification_tag_id = label_to_verification_tag_mapping[markup.label_id]
                            if verification_tag_id in tag_id_to_confidence and markup.confidence >= tag_id_to_confidence[verification_tag_id]:
                                frame_id_to_markups[frame.id].append(FrameMarkupReadMassive(**markup.dict()))
                resp = [FramesWithMarkupRead(**fr.dict(), markups=frame_id_to_markups[fr.id]) for fr in frames]

                return UnifiedResponse(data=resp)
            except NoResultFound as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=404)

    async def create_project(
        self, project: ProjectCreate, token: Annotated[str, Depends(oauth2_scheme)]
    ) -> UnifiedResponse[ProjectRead]:

        proj = ProjectBase.parse_obj(project)
        if proj.msg_receiver is not None:
            if proj.msg_receiver[0] == '@':
                proj.msg_receiver = proj.msg_receiver[1:]
        user_id = get_user_id_from_token(token)

        # Checking whether user with user_id exists
        user = await self._get_user_or_error(user_id)
        if isinstance(user, NoResultFound):
            return UnifiedResponse(error=exc_to_str(user), status_code=404)

        async with self._main_db_manager.projects.make_autobegin_session() as session:
            # async with AsyncTransaction(session.connection) as trans:
            try:
                new_project = await self._main_db_manager.projects.create_project(
                    session, proj, user_id
                )

                await self._main_db_manager.projects.create_project_tags(
                    session, new_project.id, [(pt.tag_id, pt.conf) for pt in project.tags]
                )

                tags = await self._main_db_manager.projects.get_tags_by_project(
                    session, new_project.id
                )
                tags = [tag[0] for tag in tags]

                labels = []
                for idx, (tag_rus, tag_eng) in enumerate(tag_translation.items()):
                    labels.append(
                        Label(
                            color=colors[idx],
                            name=tag_eng,
                            description=tag_rus,
                            project_id=new_project.id,
                        )
                    )

                await self._main_db_manager.projects.create_labels(
                    session, new_project.id, labels
                )

                new_project_read = ProjectRead(tags=tags, **new_project.dict())
                new_project_read.tags = tags

            except NoResultFound as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=404)
            except Exception as e:
                raise e

        return UnifiedResponse(data=new_project_read)

    async def get_project_stats(
        self,
        project_id: uuid.UUID,
    ) -> UnifiedResponse[BplaProjectStats]:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            content = await self._main_db_manager.projects.get_content_by_project(
                session, project_id
            )
        photos = [c for c in content if type(c) == Photo]
        videos = [c for c in content if type(c) == Video]

        photos_with_det = [p for p in photos if p.status != VideoStatusOption.created]
        videos_with_det = [v for v in videos if v.status != VideoStatusOption.created]

        res = BplaProjectStats(
            photo_count=len(photos),
            video_count=len(videos),
            photo_with_det_count=len(photos_with_det),
            video_with_det_count=len(videos_with_det)
        )
        return UnifiedResponse(data=res)

    async def get_projects_all_stats(
        self,
        token: Annotated[str, Depends(oauth2_scheme)]
    ) -> UnifiedResponse[BplaProjectStats]:
        user_id = get_user_id_from_token(token)
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            projects_with_users = await self._main_db_manager.projects.get_projects_with_users_ids(session, user_id)
            content = await self._main_db_manager.projects.get_content_by_projects(session, [p.id for p in projects_with_users])

        photos = [c for c in content if type(c) == Photo]
        videos = [c for c in content if type(c) == Video]

        photos_with_det = [p for p in photos if p.status != VideoStatusOption.created]
        videos_with_det = [v for v in videos if v.status != VideoStatusOption.created]

        res = BplaProjectStats(
            photo_count=len(photos),
            video_count=len(videos),
            photo_with_det_count=len(photos_with_det),
            video_with_det_count=len(videos_with_det)
        )
        return UnifiedResponse(data=res)

    async def get_projects_with_users(
        self, token: Annotated[str, Depends(oauth2_scheme)]
    ) -> UnifiedResponse[list[ProjectWithUsers]]:
        user_id = get_user_id_from_token(token)
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            projects_with_users_ids = (
                await self._main_db_manager.projects.get_projects_with_users_ids(
                    session, user_id
                )
            )

        users_ids: set[uuid.UUID] = set()
        for pwu in projects_with_users_ids:
            users_ids.add(pwu.author_id)

        async with self._main_db_manager.users.make_autobegin_session() as session:
            users = await self._main_db_manager.users.get_users(session, users_ids)

        project_id_to_detected_count: dict[uuid.UUID, int] = dict()
        project_id_to_content_type: dict[uuid.UUID, ProjectContentTypeOption] = dict()
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            for pwu in projects_with_users_ids:
                content = await self._main_db_manager.projects.get_content_by_project(
                    session, pwu.id
                )
                project_id_to_detected_count[pwu.id] = len(
                    [c for c in content if c.status != VideoStatusOption.created]
                )
                videos = [c for c in content if type(c) == Video]
                photos = [c for c in content if type(c) == Photo]
                if len(videos) > 0 and len(photos) > 0:
                    project_id_to_content_type[pwu.id] = ProjectContentTypeOption.mixed
                elif len(videos) > 0:
                    project_id_to_content_type[pwu.id] = ProjectContentTypeOption.video
                elif len(photos) > 0:
                    project_id_to_content_type[pwu.id] = ProjectContentTypeOption.photo
                else:
                    project_id_to_content_type[pwu.id] = ProjectContentTypeOption.mixed

        users_by_ids: dict[uuid.UUID, User] = dict()
        for user in users:
            users_by_ids[user.id] = user

        async with self._main_db_manager.projects.make_autobegin_session() as session:
            projects_with_users: list[ProjectWithUsers] = []
            for project_with_users_ids in projects_with_users_ids:
                author = users_by_ids[project_with_users_ids.author_id]
                content_type = project_id_to_content_type[project_with_users_ids.id]
                content_with_markups_count = await self._main_db_manager.projects.get_content_with_markups_count_by_project(
                    session, project_with_users_ids.id
                )
                total_markup_count = sum([c[1] for c in content_with_markups_count])
                project_with_users = ProjectWithUsers(
                    author=author,
                    content_type=content_type,
                    detected_count=total_markup_count,
                    **project_with_users_ids.dict(),
                )
                projects_with_users.append(project_with_users)

        return UnifiedResponse(data=projects_with_users)

    async def get_project(self, project_id: uuid.UUID) -> UnifiedResponse[ProjectRead]:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                project = await self._main_db_manager.projects.get_project(
                    session, project_id
                )
                tags = await self._main_db_manager.projects.get_tags_by_project(
                    session, project_id
                )
                tags = [tag[0] for tag in tags]

            except NoResultFound as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=404)

        project = ProjectRead(tags=tags, **project.dict())
        return UnifiedResponse(data=project)

    async def get_video_info(self, video_id: uuid.UUID) -> UnifiedResponse[Video]:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                video = await self._main_db_manager.projects.get_video(
                    session, video_id
                )
            except NoResultFound as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=404)
        return UnifiedResponse(data=video)

    async def get_photo_info(self, photo_id: uuid.UUID) -> UnifiedResponse[Photo]:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                photo = await self._main_db_manager.projects.get_photo(
                    session, photo_id
                )
            except NoResultFound as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=404)
        return UnifiedResponse(data=photo)

    async def get_content_info(
        self,
        content_id: uuid.UUID
    ) -> UnifiedResponse[Content]:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                content = await self._main_db_manager.projects.get_content(
                    session, content_id
                )
            except NoResultFound as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=404)
        res = Content.from_video_or_photo(content, detected_count=0)
        return UnifiedResponse(data=res)

    async def get_content_by_project(
        self,
        project_id: uuid.UUID,
    ) -> UnifiedResponse[list[Content]]:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                items_with_cnt = await self._main_db_manager.projects.get_content_with_markups_count_by_project(
                    session, project_id
                )
            except NoResultFound as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=404)

        content_items: list[Content] = [
            Content.from_video_or_photo(item, detected_count=markup_cnt) for item, markup_cnt in items_with_cnt
        ]
        return UnifiedResponse(data=content_items)

    async def get_content_ids_by_project(
        self,
        project_id: uuid.UUID,
    ) -> UnifiedResponse[list[uuid.UUID]]:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                items: list[Video | Photo] = await self._main_db_manager.projects.get_content_by_project(
                    session, project_id
                )
            except NoResultFound as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=404)

        content_ids = [item.id for item in items]
        return UnifiedResponse(data=content_ids)

    async def upload_content(
        self,
        # name: str,
        # description: str,
        project_id: uuid.UUID,
        files: list[UploadFile],
        token: Annotated[str, Depends(oauth2_scheme)],
    ) -> UnifiedResponse[list[Content]]:
        owner_id = get_user_id_from_token(token)

        # Определение MIME-типов для видео и фото
        PHOTO_MIME_TYPES = ["image/jpeg", "image/png", "image/gif"]
        VIDEO_MIME_TYPES = ["video/mp4", "video/avi", "video/mpeg"]

        content_items: list[Content] = []

        async with self._main_db_manager.projects.make_autobegin_session() as session:
            labels = await self._main_db_manager.projects.get_labels_by_project(
                session, project_id
            )
        labels_ids = [l.id for l in labels]

        # Настройка соединения с RabbitMQ
        # credentials = pika.PlainCredentials(settings.RABBIT_LOGIN, settings.RABBIT_PASSWORD)
        # connection = pika.BlockingConnection(pika.ConnectionParameters(
        #     settings.RABBIT_HOST, settings.RABBIT_PORT, '/', credentials)
        # )
        # channel = connection.channel()
        # channel.confirm_delivery()
        # exchange_name = "ToModels"
        # channel.exchange_declare(exchange=exchange_name, exchange_type='direct', durable=True)
        # sync_publisher = SyncPublisher(channel, exchange_name)

        for file in files:
            content_type: ContentTypeOption | None = None
            if file.content_type in PHOTO_MIME_TYPES:
                content_type = ContentTypeOption.photo
            elif file.content_type in VIDEO_MIME_TYPES:
                content_type = ContentTypeOption.video
            else:
                return UnifiedResponse(error=f"Unsupported file type: {file.content_type}", status_code=404)

            if content_type == ContentTypeOption.video:
                video_id = uuid.uuid4()
                if file.filename is not None:
                    filename = file.filename.replace(' ', '_')
                    video_name = f'{".".join(filename.split(".")[:-1])}_{video_id}.mp4'
                else:
                    video_name = f"{video_id}.mp4"
                video_path = settings.MEDIA_DIR / "video" / video_name
                os.makedirs(settings.MEDIA_DIR / "video", exist_ok=True)

                async with aiofiles.open(video_path, "wb") as f:
                    await f.write(await file.read())

                try:
                    video_meta_raw = ffmpeg.probe(video_path)["streams"]
                    video_meta = None
                    for meta_part in video_meta_raw:
                        if meta_part["codec_type"] == "video":
                            video_meta = meta_part
                            break
                    assert video_meta is not None
                except Exception as e:
                    raise ValueError(
                        "Provided file does not contain video or metadata for video is not available"
                    )

                video_ = Video(
                    id=video_id,
                    name=file.filename,
                    description="",
                    owner_id=owner_id,
                    length_sec=Decimal(video_meta["duration"]),
                    n_frames=video_meta["nb_frames"],
                    height=video_meta["height"],
                    width=video_meta["width"],
                    source_url=video_name,
                    project_id=project_id,
                    status=VideoStatusOption.created
                )

                async with self._main_db_manager.projects.make_autobegin_session() as session:
                    video = await self._main_db_manager.projects.create_video(
                        session, video_
                    )

                video_path = settings.MEDIA_DIR / "video" / video_name
                base_video_frames_dir = settings.MEDIA_DIR / "video" / "frames"
                base_video_frames_dir.mkdir(exist_ok=True)
                video_frames_dir = base_video_frames_dir / video_name
                video_frames_dir.mkdir(exist_ok=True)
                start_time = datetime.now()
                frames_filenames = extract_frames(
                    video_path=video_path,
                    output_folder=video_frames_dir,
                    name_prefix='',
                    frame_step=settings.FRAME_STEP
                )
                logger.info(f"Frames extracted in {(datetime.now() - start_time).seconds} seconds")
                # print(frames_filenames)
                filenames = ["video/" + f.split('/')[-1] for f in frames_filenames]

                frames = [Frame(
                    content_id=video.id,
                    content_type=FrameContentTypeOption.video,
                    frame_offset=offset
                ) for offset in range(len(filenames))]
                logger.info("Frames constructed")

                async with self._main_db_manager.projects.make_autobegin_session() as session:
                    session.add_all(frames)
                logger.info("Frames created in DB")

                for filename, frame in list(zip(frames_filenames, frames)):
                    data_to_send = {
                        "image_path": filename,
                        "frame_id": str(frame.id),
                        "project_id": str(project_id),
                        "frames_in_content": str(len(filenames)),
                        "type": "video"
                    }

                    await self._publisher.publish(
                        routing_key="to_yolo_model",
                        exchange_name="ToModels",
                        data={'data': data_to_send},
                        ensure=False,
                    )
                    # sync_publisher.publish(
                    #     routing_key="to_yolo_model",
                    #     exchange_name="ToModels",
                    #     data={'data': data_to_send},
                    #     mandatory=True  # Включаем mandatory для гарантии доставки
                    # )
                logger.info(f"Message for video {video.id} sent to detector")

                video_.status = VideoStatusOption.created

            elif content_type == ContentTypeOption.photo:

                photo_id = uuid.uuid4()
                if file.filename is not None:
                    photo_name = f'{".".join(file.filename.split(".")[:-1])}_{photo_id}.jpg'
                else:
                    photo_name = f"{photo_id}.jpg"
                photo_path = settings.MEDIA_DIR / "photo" / photo_name
                os.makedirs(settings.MEDIA_DIR / "photo", exist_ok=True)

                file_data = file.read()
                image = Image.open(io.BytesIO(await file_data))
                width, height = image.size
                file.file.seek(0)  # Вернуть указатель в начало файла

                async with aiofiles.open(photo_path, "wb") as f:
                    await f.write(await file.read())

                photo_ = Photo(
                    id=photo_id,
                    name=file.filename,
                    description="",
                    owner_id=owner_id,
                    height=height,
                    width=width,
                    source_url=photo_name,
                    project_id=project_id,
                    status=VideoStatusOption.created
                )

                photo_.status = VideoStatusOption.created

                try:
                    async with self._main_db_manager.projects.make_autobegin_session() as session:
                        photo = await self._main_db_manager.projects.create_photo(
                            session, photo_
                        )
                        frame = Frame(
                            content_id=photo.id,
                            content_type=FrameContentTypeOption.photo,
                            frame_offset=0
                        )
                        session.add(frame)

                    data_to_send = {
                        "image_path": f"photo/{photo_.source_url}",
                        "frame_id": str(frame.id),
                        "project_id": str(project_id),
                        "frames_in_content": "1",
                        "type": "photo"
                    }

                    message = await self._publisher.publish(
                        routing_key="to_yolo_model",
                        exchange_name="ToModels",
                        data={'data': data_to_send},
                        ensure=False,
                    )
                    logger.info(f"Message for photo detection sent: {message}")

                except NoResultFound as e:
                    return UnifiedResponse(error=exc_to_str(e), status_code=404)

                content_items.append(Content.from_photo(photo, detected_count=0))

        return UnifiedResponse(data=content_items)

    async def download_detect_result(
        self,
        content_ids: list[uuid.UUID],
    ) -> FileResponse:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            temp_files = []
            for content_id in content_ids:
                content: Photo | Video = await self._main_db_manager.projects.get_content(session, content_id)
                frames: list[Frame] = await self._main_db_manager.projects.get_frames_with_markups(session, content_id)
                labels = await self._main_db_manager.projects.get_labels_by_project(session, content.project_id)
                label_id_to_name = {label.id: label.name for label in labels}
                resp = [FramesWithMarkupRead.parse_obj(fr) for fr in frames]

                yolov8_annotations = []
                if isinstance(content, Photo):
                    for markup in resp[0].markups:
                        label_id = label_map[label_id_to_name[markup.label_id]]
                        coord_top_left_x = markup.coord_top_left_x
                        coord_top_left_y = markup.coord_top_left_y
                        coord_bottom_right_x = markup.coord_bottom_right_x
                        coord_bottom_right_y = markup.coord_bottom_right_y

                        # Вычисление центра и размеров
                        center_x = (coord_top_left_x + coord_bottom_right_x) / 2 / content.width
                        center_y = (coord_top_left_y + coord_bottom_right_y) / 2 / content.height
                        width = (coord_bottom_right_x - coord_top_left_x) / content.width
                        height = (coord_bottom_right_y - coord_top_left_y) / content.height

                        yolov8_annotations.append(f"{label_id} {center_x} {center_y} {width} {height}")
                elif isinstance(content, Video):
                    for frame in resp:
                        for markup in frame.markups:
                            label_id = label_map[label_id_to_name[markup.label_id]]
                            coord_top_left_x = markup.coord_top_left_x
                            coord_top_left_y = markup.coord_top_left_y
                            coord_bottom_right_x = markup.coord_bottom_right_x
                            coord_bottom_right_y = markup.coord_bottom_right_y

                            # Вычисление центра и размеров
                            center_x = (coord_top_left_x + coord_bottom_right_x) / 2 / content.width
                            center_y = (coord_top_left_y + coord_bottom_right_y) / 2 / content.height
                            width = (coord_bottom_right_x - coord_top_left_x) / content.width
                            height = (coord_bottom_right_y - coord_top_left_y) / content.height

                            yolov8_annotations.append(
                                f"{frame.frame_offset} {label_id} {center_x} {center_y} {width} {height}")

                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
                async with aiofiles.open(temp_file.name, mode='w', encoding='utf-8') as f:
                    await f.write("\n".join(yolov8_annotations))
                temp_files.append((content.name, temp_file.name))

            if len(temp_files) == 1:
                filename = '.'.join(temp_files[0][0].split('.')[:-1])
                return FileResponse(temp_files[0][1], media_type='text/plain', filename=f"{filename}.txt")
            else:
                zip_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
                with zipfile.ZipFile(zip_temp_file.name, 'w') as zipf:
                    for title, file_path in temp_files:
                        filename = '.'.join(title.split('.')[:-1])
                        zipf.write(file_path, arcname=f"{filename}.txt")
                return FileResponse(zip_temp_file.name, media_type='application/zip', filename='annotations.zip')

    async def change_content_status(
        self, content_id: uuid.UUID, new_status: VideoStatusOption
    ) -> UnifiedResponse[Video]:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                content = await self._main_db_manager.projects.change_content_status(
                    session, content_id, new_status
                )
            except NoResultFound as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=404)

            res = Content.from_video_or_photo(content)
        return UnifiedResponse(data=res)

    async def send_image_to_model_service(
        self, image_path: str
    ) -> Response:

        data_to_send = {
            "image_path": image_path,
            "frame_id": str(uuid.uuid4())
        }

        message = await self._publisher.publish(
            routing_key="to_yolo_model",
            exchange_name="ToModels",
            data={'data': data_to_send},
            ensure=False,
        )

        return Response(content=str(message), media_type="application/json")

    async def update_markup_for_frame(
        self,
        data: list[ChangeMarkupsOnFrame],
    ):
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            for data_item in data:
                new_markups = [FrameMarkup(
                    frame_id=data_item.frame_id,
                    label_id=raw_markup.label_id,
                    coord_top_left_x=raw_markup.coord_top_left_x,
                    coord_top_left_y=raw_markup.coord_top_left_y,
                    coord_bottom_right_x=raw_markup.coord_bottom_right_x,
                    coord_bottom_right_y=raw_markup.coord_bottom_right_y,
                    confidence=Decimal(1),
                    created_by_model=False,
                ) for raw_markup in data_item.new_markups]
                markups = await self._main_db_manager.projects.update_markups_for_frame(
                    session, data_item.frame_id, data_item.deleted_markups, new_markups
                )
        return Response(content="Markups updated")
