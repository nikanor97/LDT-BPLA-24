import io
import json
import os
import random
import tempfile
import uuid
from collections import Counter, defaultdict
from decimal import Decimal
from io import BytesIO
from os.path import isfile, join
from typing import Optional, Annotated
from datetime import datetime

import aiofiles
import ffmpeg  # type: ignore
import pandas as pd
from PIL import Image
from loguru import logger

import settings
from fastapi import Header, HTTPException, UploadFile, Depends
from sqlalchemy.exc import NoResultFound

from common.rabbitmq.publisher import Publisher

# from common.rabbitmq.client import RabbitClient
from src.db.exceptions import ResourceAlreadyExists
from src.db.main_db_manager import MainDbManager
from src.db.projects.models import (
    Frame,
    FrameBase,
    FrameMarkup,
    Label,
    LabelBase,
    Video,
    RoleTypeOption,
    Project,
    ProjectBase,
    UserRole,
    UserRoleBase,
    VerificationTag,
    VerificationTagBase,
    VideoStatusOption,
    Photo, FrameContentTypeOption,
)
from src.db.users.models import User
from src.server.auth_utils import oauth2_scheme, get_user_id_from_token
from src.server.common import UnifiedResponse, exc_to_str
from src.server.constants import tag_translation, colors, tag_translation_eng_rus
from src.server.projects.models import (
    FramesWithMarkupRead,
    ContentMarkupCreate,
    UserRoleWithProjectRead,
    ProjectCreate,
    ProjectRead,
    GpsCoords,
    ProjectsStats,
    ProjectWithUsers,
    ProjectStats,
    ScoreMapItem,
    ScoreMapDecorationTypes,
    ProjectScoredOneFloorStat,
    ProjectScoresForFloor,
    ProjectScores,
    ScoreMapItemWithLabels, BplaProjectStats, Content, ContentTypeOption, ProjectContentTypeOption,
    FramesWithMarkupCreate, MarkupListCreate,
)
from starlette.requests import Request
from starlette.responses import Response, FileResponse, StreamingResponse
from starlette.templating import Jinja2Templates

from src.server.projects.video_utils import extract_frames

# TODO: remove templates after testing
templates = Jinja2Templates(directory="templates")


class ProjectsEndpoints:
    def __init__(self, main_db_manager: MainDbManager, publisher: Publisher) -> None:
        self._main_db_manager = main_db_manager
        self._publisher = publisher
        # self._rabbit_client = RabbitClient()
        # await self._rabbit_client.connect()

    async def create_and_upload_video(
        self,
        name: str,
        description: str,
        file: UploadFile,
        token: Annotated[str, Depends(oauth2_scheme)],
        apartment_id: uuid.UUID,
    ) -> UnifiedResponse[Video]:
        owner_id = get_user_id_from_token(token)
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                apartment = await self._main_db_manager.projects.get_apartment(
                    session, apartment_id
                )
            except NoResultFound as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=404)

        video_id = uuid.uuid4()
        if file.filename is not None:
            video_name = f'{".".join(file.filename.split(".")[:-1])}_{video_id}.mp4'
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
            name=name,
            description=description,
            owner_id=owner_id,
            apartment_id=apartment_id,
            length_sec=Decimal(video_meta["duration"]),
            n_frames=video_meta["nb_frames"],
            height=video_meta["height"],
            width=video_meta["width"],
            source_url=video_name,
        )

        try:
            async with self._main_db_manager.projects.make_autobegin_session() as session:
                video = await self._main_db_manager.projects.create_video(
                    session, video_
                )
        except NoResultFound as e:
            return UnifiedResponse(error=exc_to_str(e), status_code=404)

        await self._get_clip_predictions(
            video_name, video_id, video_, apartment.project_id
        )

        return UnifiedResponse(data=video)

    async def create_frames_with_markups(
        self, video_markup: ContentMarkupCreate
    ) -> UnifiedResponse[list[FrameMarkup]]:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                frames = (
                    await self._main_db_manager.projects.create_frames_with_markups(
                        session, video_markup
                    )
                )
            except NoResultFound as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=404)

        return UnifiedResponse(data=frames)

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

    async def get_labels_by_project(
        self, project_id: uuid.UUID
    ) -> UnifiedResponse[list[Label]]:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                labels = await self._main_db_manager.projects.get_labels_by_project(
                    session, project_id
                )
                return UnifiedResponse(data=labels)
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


    async def get_video(self, video_id: uuid.UUID) -> UnifiedResponse[Video]:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                video = await self._main_db_manager.projects.get_video(
                    session, video_id
                )
                return UnifiedResponse(data=video)
            except NoResultFound as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=404)

    async def delete_project(self, project_id: uuid.UUID) -> UnifiedResponse[Project]:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                project = await self._main_db_manager.projects.delete_project(
                    session, project_id
                )
                return UnifiedResponse(data=project)
            except NoResultFound as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=404)

    async def get_videos_by_apartment(
        self, apartment_id
    ) -> UnifiedResponse[list[Video]]:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                videos = await self._main_db_manager.projects.get_videos_by_apartment(
                    session, apartment_id
                )
                return UnifiedResponse(data=videos)
            except NoResultFound as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=404)

    async def get_frame(self, frame_id: uuid.UUID) -> UnifiedResponse[Frame]:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                frame = await self._main_db_manager.projects.get_frame(
                    session, frame_id
                )
                return UnifiedResponse(data=frame)
            except NoResultFound as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=404)

    async def get_frames_by_video(
        self, video_id: uuid.UUID
    ) -> UnifiedResponse[list[Frame]]:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                frames = await self._main_db_manager.projects.get_frames_by_video(
                    session, video_id
                )
                return UnifiedResponse(data=frames)
            except NoResultFound as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=404)

    async def get_frame_markups(
        self,
        video_id: Optional[uuid.UUID] = None,
        frame_offset: Optional[Decimal] = None,
        frame_id: Optional[uuid.UUID] = None,
    ) -> UnifiedResponse[list[FrameMarkup]]:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                if video_id is not None and frame_offset is not None:
                    frame_ = FrameBase(video_id=video_id, frame_offset=frame_offset)
                else:
                    frame_ = None
                markups = await self._main_db_manager.projects.get_frame_markups(
                    session, frame_=frame_, frame_id=frame_id
                )
                return UnifiedResponse(data=markups)
            except (NoResultFound, AssertionError) as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=404)

    async def stream_video(self, video_id: uuid.UUID, range: str = Header(None)):
        # TODO: now works only for streaming from file-system

        try:
            async with self._main_db_manager.projects.make_autobegin_session() as session:
                video_db = await self._main_db_manager.projects.get_video(
                    session, video_id
                )
                # TODO: make source_url not None in models and remove type ignore bolow
                video_src = settings.MEDIA_DIR / "video" / video_db.source_url  # type: ignore
                os.makedirs(settings.MEDIA_DIR / "video", exist_ok=True)
        except NoResultFound as e:
            raise HTTPException(status_code=404, detail=e.args)

        CHUNK_SIZE = 1024 * 1024 * 10

        start_, end_ = range.replace("bytes=", "").split("-")
        start = int(start_)
        end = int(end_) if end_ else start + CHUNK_SIZE
        with open(video_src, "rb") as video:
            video.seek(start)
            data = video.read(end - start)
            filesize = str(video_src.stat().st_size)
            headers = {
                "Content-Range": f"bytes {str(start)}-{str(end)}/{filesize}",
                "Accept-Ranges": "bytes",
            }
            return Response(
                data, status_code=206, headers=headers, media_type="video/mp4"
            )

    async def get_video_file(self, video_id: uuid.UUID):
        try:
            async with self._main_db_manager.projects.make_autobegin_session() as session:
                video_db = await self._main_db_manager.projects.get_video(
                    session, video_id
                )
                # TODO: make source_url not None in models and remove type ignore bolow
                video_src = settings.MEDIA_DIR / "video" / video_db.source_url  # type: ignore
                os.makedirs(settings.MEDIA_DIR / "video", exist_ok=True)
        except NoResultFound as e:
            raise HTTPException(status_code=404, detail=e.args)

        return FileResponse(video_src, media_type="video/mp4")

    async def streaming_example(self, video_id: uuid.UUID, request: Request):
        try:
            async with self._main_db_manager.projects.make_autobegin_session() as session:
                await self._main_db_manager.projects.get_video(session, video_id)
        except NoResultFound as e:
            raise HTTPException(status_code=404, detail=e.args)
        return templates.TemplateResponse(
            "video_streaming_test.htm",
            context={"request": request, "video_id": video_id},
        )

    async def get_user_roles(
        self,
        user_id: Optional[uuid.UUID] = None,
        project_id: Optional[uuid.UUID] = None,
        role_type: Optional[RoleTypeOption] = None,
    ) -> UnifiedResponse[list[UserRoleWithProjectRead]]:
        # Checking whether user with user_id exists
        user = await self._get_user_or_error(user_id)
        if isinstance(user, NoResultFound):
            return UnifiedResponse(error=exc_to_str(user), status_code=404)

        # Retrieving user roles
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                user_roles = await self._main_db_manager.projects.get_user_roles(
                    session, user_id=user_id, project_id=project_id, role_type=role_type
                )
            except (NoResultFound, AssertionError) as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=404)

        # Adding users to results
        user_roles = [UserRoleWithProjectRead.parse_obj(ur) for ur in user_roles]
        user_ids = {ur.user_id for ur in user_roles}
        async with self._main_db_manager.users.make_autobegin_session() as session:
            users = await self._main_db_manager.users.get_users(session, user_ids)
        users_by_id: dict[uuid.UUID, User] = dict()
        for usr in users:
            users_by_id[usr.id] = usr
        for ur in user_roles:
            ur.user = users_by_id[ur.user_id]
        resp = [UserRoleWithProjectRead.parse_obj(ur) for ur in user_roles]
        return UnifiedResponse(data=resp)

    async def create_user_role(
        self, user_role: UserRoleBase
    ) -> UnifiedResponse[UserRole]:
        # Checking whether user with user_id exists
        user = await self._get_user_or_error(user_role.user_id)
        if isinstance(user, NoResultFound):
            return UnifiedResponse(error=exc_to_str(user), status_code=404)

        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                new_user_role = await self._main_db_manager.projects.create_user_role(
                    session, user_role
                )
                return UnifiedResponse(data=new_user_role)
            except ResourceAlreadyExists as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=409)
            except NoResultFound as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=404)

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
    ) -> UnifiedResponse[list[VerificationTag]]:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            tags = await self._main_db_manager.projects.get_all_verification_tags(
                session
            )
        return UnifiedResponse(data=tags)

    async def write_gps(
        self, video_id: uuid.UUID, gps_coords: GpsCoords
    ) -> UnifiedResponse[Video]:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                video = await self._main_db_manager.projects.write_gps_coords(
                    session, video_id, gps_coords
                )
            except NoResultFound as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=404)
        return UnifiedResponse(data=video)

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

    async def _get_clip_predictions(
        self, video_name: str, video_id: uuid.UUID, video: Video, project_id: uuid.UUID
    ):
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            labels = await self._main_db_manager.projects.get_labels_by_project(
                session, project_id
            )
        # from pprint import pprint
        #
        # pprint(labels)

        labels_names = [l.name for l in labels]
        label_id_by_name = dict()
        for label in labels:
            label_id_by_name[label.name] = label.id

        message = dict()
        message["data"] = {
            "video_name": video_name,
            "labels_names": labels_names,
            "project_id": str(project_id),
            "video_id": str(video_id),
        }
        rabbit_message = await self._publisher.publish(
            routing_key="data_for_models",
            exchange_name="ToModels",
            data=message,
            ensure=False,
        )
        print(rabbit_message)

# ----------------------------------------------
# ----------------------------------------------
# ----------------------------------------------

    async def get_frames_with_markups(
        self, content_id: uuid.UUID
    ) -> UnifiedResponse[list[FramesWithMarkupRead]]:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                frames = await self._main_db_manager.projects.get_frames_with_markups(
                    session, content_id
                )
                resp = [FramesWithMarkupRead.parse_obj(fr) for fr in frames]
                return UnifiedResponse(data=resp)
            except NoResultFound as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=404)

    # async def get_frames_with_markups(
    #     self, content_id: uuid.UUID
    # ) -> UnifiedResponse[list[FramesWithMarkupRead]]:
    #     async with self._main_db_manager.projects.make_autobegin_session() as session:
    #         try:
    #             frames = await self._main_db_manager.projects.get_frames_with_markups(
    #                 session, content_id
    #             )
    #             labels = await self._main_db_manager.projects.get_labels_by_project(
    #                 session, frames[0].project_id
    #             )
    #             label_id_to_name = {label.id: label.name for label in labels}
    #             for idx_frame, frame in enumerate(frames):
    #                 for idx_markup, markup in enumerate(frame.markups):
    #                     label_name = label_id_to_name[markup.label_id]
    #                     if label_name not in label_map:
    #                         continue
    #                     if markup.confidence < confidence_thresholds[markup]:
    #                         frames[idx_frame].markups[idx_markup].confidence = 0
    #             resp = [FramesWithMarkupRead.parse_obj(fr) for fr in frames]
    #             return UnifiedResponse(data=resp)
    #         except NoResultFound as e:
    #             return UnifiedResponse(error=exc_to_str(e), status_code=404)

    async def create_project(
        self, project: ProjectCreate, token: Annotated[str, Depends(oauth2_scheme)]
    ) -> UnifiedResponse[ProjectRead]:

        proj = ProjectBase.parse_obj(project)
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
                    session, new_project.id, project.tags_ids
                )

                tags = await self._main_db_manager.projects.get_tags_by_project(
                    session, new_project.id
                )

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
    ) -> UnifiedResponse[BplaProjectStats]:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            content = await self._main_db_manager.projects.get_all_content(session)

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

        projects_with_users: list[ProjectWithUsers] = []
        for project_with_users_ids in projects_with_users_ids:
            author = users_by_ids[project_with_users_ids.author_id]
            content_type = project_id_to_content_type[project_with_users_ids.id]
            project_with_users = ProjectWithUsers(
                author=author,
                content_type=content_type,
                detected_count=project_id_to_detected_count[project_with_users_ids.id],
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
        res = Content.from_video_or_photo(content, detected_count=0)  # TODO: проставлять РЕАЛЬНОЕ ЗНАЧЕНИЕ
        return UnifiedResponse(data=res)

    async def get_content_by_project(
        self,
        project_id: uuid.UUID,
    ) -> UnifiedResponse[list[Content]]:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                items = await self._main_db_manager.projects.get_content_by_project(
                    session, project_id
                )
            except NoResultFound as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=404)

        content_items: list[Content] = [Content.from_video_or_photo(item, detected_count=0) for item in items]  # TODO: проставлять РЕАЛЬНОЕ ЗНАЧЕНИЕ
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

                # frames_with_markups = ContentMarkupCreate(
                #     content_id=video_id,
                #     content_type=FrameContentTypeOption.video,
                #     frames=[FramesWithMarkupCreate(
                #         frame_offset=offset,
                #         markup_list=[MarkupListCreate(
                #             coord_top_left=(
                #                 random.choice(range(1, video_.width // 2)),
                #                 random.choice(range(1, video_.height // 2))
                #             ),
                #             coord_bottom_right=(
                #                 random.choice(range(video_.width // 2, video_.width)),
                #                 random.choice(range(video_.height // 2, video_.height))
                #             ),
                #             label_id=random.choice(labels_ids),
                #             confidence=Decimal(random.random())
                #         ) for _ in range(2)]
                #     ) for offset in range(video_.n_frames)]  # ДЕЛАЕМ ДЛЯ КАЖДОГО КАДРА
                # )
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

                async with self._main_db_manager.projects.make_autobegin_session() as session:
                    session.add_all(frames)

                for filename, frame in list(zip(frames_filenames, frames)):
                    data_to_send = {
                        "image_path": filename,
                        "frame_id": str(frame.id),
                        "project_id": str(project_id),
                        "frames_in_content": str(len(filenames)),
                    }

                    await self._publisher.publish(
                        routing_key="to_yolo_model",
                        exchange_name="ToModels",
                        data={'data': data_to_send},
                        ensure=False,
                    )
                logger.info(f"Message for video {video.id} sent to detector")

                video_.status = VideoStatusOption.created

                # await self._get_clip_predictions(
                #     video_name, video_id, video_, apartment.project_id
                # )

                # content_items.append(Content.from_video(video, detected_count=2))  # TODO: проставлять РЕАЛЬНОЕ ЗНАЧЕНИЕ

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

                # await self._get_clip_predictions(
                #     video_name, video_id, video_, apartment.project_id
                # )

                content_items.append(Content.from_photo(photo, detected_count=3))  # TODO: проставлять РЕАЛЬНОЕ ЗНАЧЕНИЕ

        return UnifiedResponse(data=content_items)

    async def download_detect_result(
        self,
        content_id: uuid.UUID,
    ) -> FileResponse:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            content: Photo | Video = await self._main_db_manager.projects.get_content(
                session, content_id
            )
            frames: list[Frame] = await self._main_db_manager.projects.get_frames_with_markups(
                session, content_id
            )
        resp = [FramesWithMarkupRead.parse_obj(fr) for fr in frames]

        if type(content) == Photo:
            json_data = {
                "photo_id": str(content.id),
                "markups": [
                    {
                        "id": str(markup.id),
                        "label_id": str(markup.label_id),
                        "coord_top_left_x": float(markup.coord_top_left_x),
                        "coord_top_left_y": float(markup.coord_top_left_y),
                        "coord_bottom_right_x": float(markup.coord_bottom_right_x),
                        "coord_bottom_right_y": float(markup.coord_bottom_right_y),
                        "confidence": float(markup.confidence)
                    } for markup in resp[0].markups
                ]
            }
        elif type(content) == Video:
            json_data = {
                "video_id": str(content.id),
                "frames": [
                    {
                        "frame_offset": frame.frame_offset,
                        "markups": [
                            {
                                "id": str(markup.id),
                                "label_id": str(markup.label_id),
                                "coord_top_left_x": float(markup.coord_top_left_x),
                                "coord_top_left_y": float(markup.coord_top_left_y),
                                "coord_bottom_right_x": float(markup.coord_bottom_right_x),
                                "coord_bottom_right_y": float(markup.coord_bottom_right_y),
                                "confidence": float(markup.confidence)
                            } for markup in frame.markups
                        ]
                    } for frame in resp
                ]
            }

        # Конвертируем JSON в строку
        json_data = json.dumps(json_data, indent=4, ensure_ascii=False)

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        async with aiofiles.open(temp_file.name, mode='w', encoding='utf-8') as f:
            await f.write(json_data)

        # Используем FileResponse для отправки файла
        return FileResponse(temp_file.name, media_type='application/json', filename='data.json')
        # return FileResponse(temp_file.)

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
