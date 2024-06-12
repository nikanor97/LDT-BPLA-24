import os
import uuid
from collections import Counter, defaultdict
from decimal import Decimal
from io import BytesIO
from os.path import isfile, join
from typing import Optional, Annotated

import aiofiles
import ffmpeg  # type: ignore
import pandas as pd
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
    Apartment,
    ProjectDocument,
    ApartmentDecorationTypeOption,
    VerificationTag,
    VerificationTagBase,
    VideoStatusOption,
    ApartmentStatusOption, Photo,
)
from src.db.users.models import User
from src.server.auth_utils import oauth2_scheme, get_user_id_from_token
from src.server.common import UnifiedResponse, exc_to_str
from src.server.constants import tag_translation, colors
from src.server.projects.models import (
    FramesWithMarkupRead,
    VideoMarkupCreate,
    UserRoleWithProjectRead,
    ProjectCreate,
    ProjectRead,
    GpsCoords,
    ProjectsStats,
    ProjectWithUsers,
    ApartmentWithVideo,
    ProjectStats,
    ScoreMapItem,
    ScoreMapDecorationTypes,
    ProjectScoredOneFloorStat,
    ProjectScoresForFloor,
    ProjectScores,
    ApartmentWithPlans,
    ScoreMapItemWithLabels, BplaProjectStats, Content,
)
from starlette.requests import Request
from starlette.responses import Response, FileResponse
from starlette.templating import Jinja2Templates


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

    # async def create_frame(self, frame: FrameBase) -> UnifiedResponse[Frame]:
    #     async with self._main_db_manager.markup.make_autobegin_session() as session:
    #         try:
    #             new_frame = await self._main_db_manager.markup.create_frame(session, frame)
    #             return UnifiedResponse(data=new_frame)
    #         except NoResultFound as e:
    #             # raise HTTPException(status_code=404, detail=e.args)
    #             return UnifiedResponse(error=exc_to_str(e), status_code=404)
    #         except ResourceAlreadyExists as e:
    #             # raise HTTPException(status_code=409, detail=e.args)
    #             return UnifiedResponse(error=exc_to_str(e), status_code=409)
    #
    # async def create_markup(self, markup: FrameMarkupBase) -> UnifiedResponse[FrameMarkup]:
    #     async with self._main_db_manager.markup.make_autobegin_session() as session:
    #         try:
    #             new_markup = await self._main_db_manager.markup.create_markup(session, markup)
    #             return UnifiedResponse(data=new_markup)
    #         except NoResultFound as e:
    #             # raise HTTPException(status_code=404, detail=e.args)
    #             return UnifiedResponse(error=exc_to_str(e), status_code=404)

    async def create_frames_with_markups(
        self, video_markup: VideoMarkupCreate
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

    async def get_video(self, video_id: uuid.UUID) -> UnifiedResponse[Video]:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                video = await self._main_db_manager.projects.get_video(
                    session, video_id
                )
                return UnifiedResponse(data=video)
            except NoResultFound as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=404)

    # async def get_project(self, project_id: uuid.UUID) -> UnifiedResponse[ProjectRead]:
    #     async with self._main_db_manager.projects.make_autobegin_session() as session:
    #         try:
    #             project = await self._main_db_manager.projects.get_project(
    #                 session, project_id
    #             )
    #             tags = await self._main_db_manager.projects.get_tags_by_project(
    #                 session, project_id
    #             )
    #             user_roles_verificators = (
    #                 await self._main_db_manager.projects.get_user_roles(
    #                     session,
    #                     project_id=project_id,
    #                     role_type=RoleTypeOption.verificator,
    #                 )
    #             )
    #
    #         except NoResultFound as e:
    #             return UnifiedResponse(error=exc_to_str(e), status_code=404)
    #
    #     users_ids = {urv.user_id for urv in user_roles_verificators}
    #
    #     async with self._main_db_manager.users.make_autobegin_session() as session:
    #         verificators = await self._main_db_manager.users.get_users(
    #             session, users_ids
    #         )
    #
    #     project = ProjectRead(tags=tags, verificators=verificators, **project.dict())
    #     return UnifiedResponse(data=project)

    async def delete_project(self, project_id: uuid.UUID) -> UnifiedResponse[Project]:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                project = await self._main_db_manager.projects.delete_project(
                    session, project_id
                )
                return UnifiedResponse(data=project)
            except NoResultFound as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=404)

    async def get_apartments_by_project(
        self, project_id: uuid.UUID
    ) -> UnifiedResponse[list[ApartmentWithVideo]]:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                apartments = await self._main_db_manager.projects.get_apartments_with_video_by_project(
                    session, project_id
                )
                return UnifiedResponse(data=apartments)
            except NoResultFound as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=404)

    # NO NEED CAUSE WE HAVE GETPROJECT THAT RETURNS APARTMENTS ALSO
    # async def get_videos_by_project(
    #     self, project_id: uuid.UUID
    # ) -> UnifiedResponse[list[Video]]:
    #     # async with self._main_db_manager.projects.make_autobegin_session() as session:
    #     #     try:
    #     #         await self._main_db_manager.projects.get_project(session, project_id)
    #     #     except NoResultFound as e:
    #     #         return UnifiedResponse(error=exc_to_str(e), status_code=404)
    #
    #     async with self._main_db_manager.projects.make_autobegin_session() as session:
    #         videos = await self._main_db_manager.projects.get_videos_by_project(
    #             session, project_id
    #         )
    #         return UnifiedResponse(data=videos)

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

    async def get_frames_with_markups(
        self, video_id: uuid.UUID
    ) -> UnifiedResponse[list[FramesWithMarkupRead]]:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                frames = await self._main_db_manager.projects.get_frames_with_markups(
                    session, video_id
                )
                # resp = []
                # for fr in frames:
                #     markups = []
                #     for markup in fr.markups:
                #         markups.append(FrameMarkupReadMassive(
                #             id=markup.id,
                #             label_id=markup.label_id,
                #             coords=(
                #                 markup.coord_top_left_x,
                #                 markup.coord_top_left_y,
                #                 markup.coord_bottom_right_x,
                #                 markup.coord_bottom_right_y
                #             ),
                #             confidence=markup.confidence
                #         ))
                #     resp.append(FramesWithMarkupRead(
                #         id=fr.id, video_id=fr.video_id, frame_offset=fr.frame_offset, markups=markups
                #     ))
                resp = [FramesWithMarkupRead.parse_obj(fr) for fr in frames]
                return UnifiedResponse(data=resp)
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

    # async def get_videos_from_galery(
    #     self, token: Annotated[str, Depends(oauth2_scheme)]
    # ) -> UnifiedResponse[list[Video]]:
    #     # Checking if user with this id exists
    #     async with self._main_db_manager.users.make_autobegin_session() as session:
    #         try:
    #             user_id = get_user_id_from_token(token)
    #             await self._main_db_manager.users.get_user(session, user_id=user_id)
    #         except NoResultFound as e:
    #             return UnifiedResponse(error=exc_to_str(e), status_code=404)
    #
    #     async with self._main_db_manager.markup.make_autobegin_session() as session:
    #         videos = await self._main_db_manager.markup.get_videos_by_owner(
    #             session, user_id
    #         )
    #     return UnifiedResponse(data=videos)

    # async def assign_videos_to_project(
    #     self, videos_project: VideosWithProjectAssign
    # ) -> UnifiedResponse[list[Video]]:
    #     async with self._main_db_manager.users.make_autobegin_session() as session:
    #         try:
    #             await self._main_db_manager.users.get_project(
    #                 session, videos_project.project_id
    #             )
    #         except NoResultFound as e:
    #             return UnifiedResponse(error=exc_to_str(e), status_code=404)
    #
    #     async with self._main_db_manager.markup.make_autobegin_session() as session:
    #         try:
    #             videos = await self._main_db_manager.markup.assign_videos_to_project(
    #                 session, videos_project.video_ids, videos_project.project_id
    #             )
    #         except NoResultFound as e:
    #             return UnifiedResponse(error=exc_to_str(e), status_code=404)
    #     return UnifiedResponse(data=videos)

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

    async def create_project(
        self, project: ProjectCreate, token: Annotated[str, Depends(oauth2_scheme)]
    ) -> UnifiedResponse[ProjectRead]:
        def get_decoration_type(word) -> ApartmentDecorationTypeOption:
            if word == "Чистовая":
                return ApartmentDecorationTypeOption.finishing
            elif word == "Черновая":
                return ApartmentDecorationTypeOption.rough

        proj = ProjectBase.parse_obj(project)
        user_id = get_user_id_from_token(token)

        # Checking whether user with user_id exists
        user = await self._get_user_or_error(user_id)
        if isinstance(user, NoResultFound):
            return UnifiedResponse(error=exc_to_str(user), status_code=404)

        # Checking whether users with verificators_ids exist in the DB
        async with self._main_db_manager.users.make_autobegin_session() as session:
            try:
                await self._main_db_manager.users.get_users(
                    session, project.verificators_ids
                )
            except NoResultFound as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=404)

        async with self._main_db_manager.projects.make_autobegin_session() as session:
            # async with AsyncTransaction(session.connection) as trans:
            try:
                # TODO: implement transactional behaviour here !!!
                # Checking whether verification tags provided actually exist
                await self._main_db_manager.projects.get_verification_tags(
                    session, project.tags_ids
                )

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
                        )
                    )

                await self._main_db_manager.projects.create_labels(
                    session, new_project.id, labels
                )

                new_project_read = ProjectRead(tags=tags, **new_project.dict())
                new_project_read.tags = tags

                # Checking if any verificators with verificators_ids are already assigned to the project
                existing_user_roles = (
                    await self._main_db_manager.projects.get_user_roles(
                        session,
                        project_id=new_project.id,
                        role_type=RoleTypeOption.verificator,
                    )
                )
                not_assigned_users_ids = set(project.verificators_ids) - set(
                    [eur.user_id for eur in existing_user_roles]
                )
                for u_id in not_assigned_users_ids:
                    ur = UserRoleBase(
                        project_id=new_project.id,
                        user_id=u_id,
                        role_type=RoleTypeOption.verificator,
                    )
                    await self._main_db_manager.projects.create_user_role(session, ur)

                if proj.document_id is not None:
                    project_document = (
                        await self._main_db_manager.projects.get_project_document(
                            session, proj.document_id
                        )
                    )

                    df = pd.read_csv(
                        settings.MEDIA_DIR / "documents" / project_document.source_url,
                        header=None,
                    )

                    apartments = []
                    for i in range(4, len(df[0])):
                        apartments.append(
                            Apartment(
                                number=df[0][i],
                                decoration_type=get_decoration_type(df[1][i].strip()),
                                building=df[2][i],
                                section=df[3][i],
                                floor=df[4][i],
                                rooms_total=df[5][i],
                                square=df[6][i],
                                project_id=new_project.id,
                            )
                        )
                    session.add_all(apartments)

            except NoResultFound as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=404)
            except Exception as e:
                # print(session.pen)
                # # session.expunge_all()
                # await session.rollback()
                raise e

        return UnifiedResponse(data=new_project_read)

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

    async def create_and_upload_project_document(
        self, document: UploadFile
    ) -> UnifiedResponse[ProjectDocument]:
        contents = document.file.read()
        buffer = BytesIO(contents)
        df = pd.read_csv(buffer, header=None)
        buffer.close()
        document.file.close()

        project_name = df[1][0]
        address = df[1][1]

        decoration_types = [df[1][i] for i in range(4, len(df[0]))]
        decor_types_agg = Counter(decoration_types)
        decor_types_agg = {k.strip(): v for k, v in decor_types_agg.items()}

        document_id = uuid.uuid4()
        if document.filename is not None:
            document_name = (
                f'{".".join(document.filename.split(".")[:-1])}_{document_id}.csv'
            )
        else:
            document_name = f"{document_id}.csv"
        document_path = settings.MEDIA_DIR / "documents" / document_name
        os.makedirs(settings.MEDIA_DIR / "documents", exist_ok=True)

        # async with aiofiles.open(document_path, "wb", ) as f:
        #     await f.write(buffer.read())
        df.to_csv(document_path, header=False, index=False)

        project_doc = ProjectDocument(
            id=document_id,
            source_url=document_name,
            project_id=None,
            apt_count=len(decoration_types),
            n_finishing=decor_types_agg["Чистовая"],
            n_rough=decor_types_agg["Черновая"],
            project_name=project_name,
            address=address,
        )

        try:
            async with self._main_db_manager.projects.make_autobegin_session() as session:
                project_document = (
                    await self._main_db_manager.projects.create_project_document(
                        session, project_doc
                    )
                )
        except NoResultFound as e:
            return UnifiedResponse(error=exc_to_str(e), status_code=404)

        return UnifiedResponse(data=project_document)

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

    async def get_apartment(
        self, apartment_id: uuid.UUID
    ) -> UnifiedResponse[ApartmentWithPlans]:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                apartment = await self._main_db_manager.projects.get_apartment(
                    session, apartment_id
                )
                # apartment_plan_url = "https://i.postimg.cc/bw5WSmD0/samolet-apt-1-room-apt-plan.png",
                # floor_plan_url = "https://i.postimg.cc/HstDP0JX/samolet-apt-1-room-floor-plan.png",
                if apartment.rooms_total == 1:
                    apartment_plan_url = "https://i.postimg.cc/YCSHCNyc/1.png"
                    floor_plan_url = "https://i.postimg.cc/hvFDJJQL/1.png"
                elif apartment.rooms_total == 2:
                    apartment_plan_url = "https://i.postimg.cc/7Yf9PfMs/2.png"
                    floor_plan_url = "https://i.postimg.cc/kGjT1SN8/2.png"
                elif apartment.rooms_total == 3:
                    apartment_plan_url = "https://i.postimg.cc/Qx8tcTnm/3.png"
                    floor_plan_url = "https://i.postimg.cc/RVdWYRn2/3.png"
                else:
                    apartment_plan_url = None
                    floor_plan_url = None

                # print(apartment_plan_url, floor_plan_url)

                apt_with_plans = ApartmentWithPlans(
                    apartment_plan_url=apartment_plan_url,
                    floor_plan_url=floor_plan_url,
                    **apartment.dict(),
                )
            except NoResultFound as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=404)
        return UnifiedResponse(data=apt_with_plans)

    async def change_video_status(
        self, video_id: uuid.UUID, new_status: VideoStatusOption
    ) -> UnifiedResponse[Video]:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                video = await self._main_db_manager.projects.change_video_status(
                    session, video_id, new_status
                )
            except NoResultFound as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=404)
        return UnifiedResponse(data=video)

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

    async def get_score_map(self, video_id: uuid.UUID):
        files_dir = settings.MEDIA_DIR / "score_maps"
        filenames_all = [f for f in os.listdir(files_dir) if isfile(join(files_dir, f))]
        needed_file = [f for f in filenames_all if f.endswith(f"{video_id}.csv")]
        if len(needed_file) == 0:
            return UnifiedResponse(
                error=f"No score map found for video with id {video_id}",
                status_code=404,
            )
        else:
            return FileResponse(files_dir / needed_file[0], media_type="text/csv")

    @logger.catch
    async def get_scores(
        self,
        project_id: uuid.UUID,
    ) -> UnifiedResponse[ProjectScores]:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                apartments = await self._main_db_manager.projects.get_apartments_with_video_by_project(
                    session, project_id
                )
            except NoResultFound as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=404)

        files_dir = settings.MEDIA_DIR / "score_maps"
        filenames_all = {f for f in os.listdir(files_dir) if isfile(join(files_dir, f))}
        # print(f"{filenames_all=}")

        # score_maps_by_floor: defaultdict[int, list[pandas.DataFrame]] = defaultdict(list)
        # for apt in apartments:
        #     score_maps_by_floor[apt.floor].append()

        videos_ids: set[uuid.UUID] = set()
        videos_ids_by_floor: defaultdict[int, list] = defaultdict(list)
        for apt in apartments:
            if apt.video is not None:
                videos_ids_by_floor[apt.floor].append(apt.video.id)
                videos_ids.add(apt.video.id)

        # print(f"{videos_ids=}")

        needed_filenames = {
            f
            for f in filenames_all
            if uuid.UUID(f.split("_")[-1].split(".")[0]) in videos_ids
        }
        # print(f"{needed_filenames=}")
        filename_by_video_id: dict[uuid.UUID, str] = dict()
        for filename in needed_filenames:
            try:
                video_id = uuid.UUID(filename.split("_")[-1].split(".")[0])
                # print(f"{video_id}")
                filename_by_video_id[video_id] = filename
            except KeyError:
                print(
                    f"Scoremap for video {filename} was not found. Most probable video is in extraction stage"
                )

        scoremaps_by_floor: defaultdict[int, list[pd.DataFrame]] = defaultdict(list)
        for floor, vid_ids in videos_ids_by_floor.items():
            for vid_id in vid_ids:
                # print(floor, vid_id)
                try:
                    scoremap_df = pd.read_csv(files_dir / filename_by_video_id[vid_id])
                    scoremaps_by_floor[floor].append(scoremap_df)
                except KeyError:
                    print(
                        f"Scoremap for video with id {vid_id} was not found. "
                        f"Most probable video is in extraction stage"
                    )

        floor_readiness: dict[int, tuple[Decimal, Decimal]] = dict()

        data_avg = [0] * 27
        for floor, scoremaps_df in scoremaps_by_floor.items():
            floor_data_avg = [0] * 27
            for scoremap_df in scoremaps_df:
                # scoremap = self.scores_df_to_model(scoremap_df)
                data = list(scoremap_df["Готовность Модель"])
                # print(data)
                for idx, da in enumerate(data):
                    if da == "True":
                        data[idx] = 1
                    elif da == "False":
                        data[idx] = 0
                    else:
                        data[idx] = float(da)
                floor_data_avg = [i + j for i, j in zip(data, floor_data_avg)]
            # print(f"{floor_data_avg=}")
            if len(scoremaps_df) > 0:
                floor_data_avg = [
                    float(da) / len(scoremaps_df) if idx not in [11, 14] else da
                    for idx, da in enumerate(
                        floor_data_avg
                    )  # kitchen_total, switch_total
                ]
            print(f"{floor_data_avg=}")
            # floor_data_avg = [float(da) / len(scoremaps_df) for da in floor_data_avg if da not in ('True', 'False') else bool()]
            data_avg = [i + j for i, j in zip(data_avg, floor_data_avg)]

            finishing = (
                floor_data_avg[2]
                + floor_data_avg[5]
                + floor_data_avg[8]
                + floor_data_avg[20]
                + floor_data_avg[23]
                + floor_data_avg[26]
            )
            no_decor = (
                floor_data_avg[0]
                + floor_data_avg[3]
                + floor_data_avg[6]
                + floor_data_avg[18]
                + floor_data_avg[21]
                + floor_data_avg[24]
            )
            floor_readiness[floor] = (Decimal(finishing / 6), Decimal(no_decor / 6))

        if len(scoremaps_by_floor) > 0:
            data_avg = [
                da / len(scoremaps_by_floor) if idx not in [11, 14] else da
                for idx, da in enumerate(data_avg)
            ]

        print(f"{data_avg=}")

        psbf = ScoreMapItem(
            floor=ScoreMapDecorationTypes(
                no_decor=data_avg[0] / sum(data_avg[0:3])
                if sum(data_avg[0:3]) > 0
                else 0,
                rough_decor=data_avg[1] / sum(data_avg[0:3])
                if sum(data_avg[0:3]) > 0
                else 0,
                finishing_decor=data_avg[2] / sum(data_avg[0:3])
                if sum(data_avg[0:3]) > 0
                else 0,
            ),
            wall=ScoreMapDecorationTypes(
                no_decor=data_avg[3] / sum(data_avg[3:6])
                if sum(data_avg[3:6]) > 0
                else 0,
                rough_decor=data_avg[4] / sum(data_avg[3:6])
                if sum(data_avg[3:6]) > 0
                else 0,
                finishing_decor=data_avg[5] / sum(data_avg[3:6])
                if sum(data_avg[3:6]) > 0
                else 0,
            ),
            ceiling=ScoreMapDecorationTypes(
                no_decor=data_avg[6] / sum(data_avg[6:9])
                if sum(data_avg[6:9]) > 0
                else 0,
                rough_decor=data_avg[7] / sum(data_avg[6:9])
                if sum(data_avg[6:9]) > 0
                else 0,
                finishing_decor=data_avg[8] / sum(data_avg[6:9])
                if sum(data_avg[6:9]) > 0
                else 0,
            ),
            doors_pct=0.68,  # TODO: CHANGE ME!!! data_avg[9],
            trash_bool=True if data_avg[10] > 0.1 else False,
            switch_total=data_avg[11],
            window_decor_pct=data_avg[12],
            radiator_pct=data_avg[13],
            kitchen_total=data_avg[14],
            toilet_pct=data_avg[15],
            bathtub_pct=data_avg[16],
            sink_pct=data_avg[17],
            mop_floor=ScoreMapDecorationTypes(
                no_decor=data_avg[18] / sum(data_avg[18:21])
                if sum(data_avg[18:21]) > 0
                else 0,
                rough_decor=data_avg[19] / sum(data_avg[18:21])
                if sum(data_avg[18:21]) > 0
                else 0,
                finishing_decor=data_avg[20] / sum(data_avg[18:21])
                if sum(data_avg[18:21]) > 0
                else 0,
            ),
            mop_wall=ScoreMapDecorationTypes(
                no_decor=data_avg[21] / sum(data_avg[21:24])
                if sum(data_avg[21:24]) > 0
                else 0,
                rough_decor=data_avg[22] / sum(data_avg[21:24])
                if sum(data_avg[21:24]) > 0
                else 0,
                finishing_decor=data_avg[23] / sum(data_avg[21:24])
                if sum(data_avg[21:24]) > 0
                else 0,
            ),
            mop_ceiling=ScoreMapDecorationTypes(
                no_decor=data_avg[24] / sum(data_avg[24:27])
                if sum(data_avg[24:27]) > 0
                else 0,
                rough_decor=data_avg[25] / sum(data_avg[24:27])
                if sum(data_avg[24:27]) > 0
                else 0,
                finishing_decor=data_avg[26] / sum(data_avg[24:27])
                if sum(data_avg[24:27]) > 0
                else 0,
            ),
        )

        psff = ProjectScoresForFloor(
            finishing=[
                ProjectScoredOneFloorStat(floor=floor, value=finishing)
                for floor, (finishing, no_decor) in floor_readiness.items()
            ],
            no_decoration=[
                ProjectScoredOneFloorStat(floor=floor, value=no_decor)
                for floor, (finishing, no_decor) in floor_readiness.items()
            ],
        )

        ps = ProjectScores(avg_floor=psbf, for_floor=psff)

        return UnifiedResponse(data=ps)

    async def get_scores_mock(
        self,
        project_id: uuid.UUID,
    ) -> UnifiedResponse[ProjectScores]:
        psdt = ScoreMapDecorationTypes(
            no_decor=0.1, rough_decor=0.7, finishing_decor=0.2
        )
        psdt_mop = ScoreMapDecorationTypes(
            no_decor=0.2, rough_decor=0.3, finishing_decor=0.5
        )
        ps_by_floor = ScoreMapItem(
            doors_pct=0.2,
            trash_bool=True,
            switch_total=10,
            window_decor_pct=0.3,
            radiator_pct=0.5,
            kitchen_total=4,
            toilet_pct=0.45,
            bathtub_pct=0.37,
            sink_pct=0.64,
            floor=psdt,
            wall=psdt,
            ceiling=psdt,
            mop_floor=psdt_mop,
            mop_wall=psdt_mop,
            mop_ceiling=psdt_mop,
        )

        floors_finishing = [
            ProjectScoredOneFloorStat(floor=i, value=(i * 15) % 100) for i in range(15)
        ]

        floors_no_decoration = [
            ProjectScoredOneFloorStat(floor=i, value=(i * 15) % 100)
            for i in range(4, 19)
        ]

        scores_for_floor = ProjectScoresForFloor(
            finishing=floors_finishing, no_decoration=floors_no_decoration
        )

        ps = ProjectScores(avg_floor=ps_by_floor, for_floor=scores_for_floor)

        return UnifiedResponse(data=ps)

    async def get_score_map_for_apartment(
        self, apartment_id: uuid.UUID
    ) -> UnifiedResponse[Optional[ScoreMapItemWithLabels]]:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            videos = await self._main_db_manager.projects.get_videos_by_apartment(
                session, apartment_id
            )
        if len(videos) == 0:
            return UnifiedResponse(data=None)
        video = list(sorted(videos, key=lambda x: x.created_at))[-1]

        files_dir = settings.MEDIA_DIR / "score_maps"
        filenames_all = {f for f in os.listdir(files_dir) if isfile(join(files_dir, f))}

        needed_filename = [f for f in filenames_all if f.endswith(f"{video.id}.csv")]
        if len(needed_filename) == 0:
            return UnifiedResponse(data=None)

        df = pd.read_csv(files_dir / needed_filename[0])
        data = df["Готовность Модель"]
        psdt_not_mop = dict(
            label="Все помещения кроме МОП",
            value=dict(
                floor=dict(
                    label="Пол",
                    value=dict(
                        no_decor=dict(label="Нет отделки", value=data[0]),
                        rough_decor=dict(label="Черновая", value=data[1]),
                        finishing_decor=dict(label="Чистовая", value=data[2]),
                    ),
                ),
                wall=dict(
                    label="Стена",
                    value=dict(
                        no_decor=dict(label="Нет отделки", value=data[3]),
                        rough_decor=dict(label="Черновая", value=data[4]),
                        finishing_decor=dict(label="Чистовая", value=data[5]),
                    ),
                ),
                ceiling=dict(
                    label="Потолок",
                    value=dict(
                        no_decor=dict(label="Нет отделки", value=data[6]),
                        rough_decor=dict(label="Черновая", value=data[7]),
                        finishing_decor=dict(label="Чистовая", value=data[8]),
                    ),
                ),
            ),
        )
        psdt_mop = dict(
            label="МОП",
            value=dict(
                mop_floor=dict(
                    label="Пол",
                    value=dict(
                        no_decor=dict(label="Нет отделки", value=data[18]),
                        rough_decor=dict(label="Черновая", value=data[19]),
                        finishing_decor=dict(label="Чистовая", value=data[20]),
                    ),
                ),
                mop_wall=dict(
                    label="Стена",
                    value=dict(
                        no_decor=dict(label="Нет отделки", value=data[21]),
                        rough_decor=dict(label="Черновая", value=data[22]),
                        finishing_decor=dict(label="Чистовая", value=data[23]),
                    ),
                ),
                mop_ceiling=dict(
                    label="Потолок",
                    value=dict(
                        no_decor=dict(label="Нет отделки", value=data[24]),
                        rough_decor=dict(label="Черновая", value=data[25]),
                        finishing_decor=dict(label="Чистовая", value=data[26]),
                    ),
                ),
            ),
        )
        score_map_raw = dict(
            not_mop=psdt_not_mop,
            all_places=dict(
                label="Все помещения",
                value=dict(
                    doors_pct=dict(label="Двери", value=data[9]),
                    trash_bool=dict(label="Мусор", value=bool(data[10])),
                    switch_total=dict(label="Розетки и выключатели", value=data[11]),
                ),
            ),
            life_zones=dict(
                label="Жилая/Кухня",
                value=dict(
                    window_decor_pct=dict(label="Отделка окна", value=data[12]),
                    radiator_pct=dict(label="Установленная батарея", value=data[13]),
                    kitchen_total=dict(label="Кухня", value=data[14]),
                ),
            ),
            bathroom=dict(
                label="Ванная",
                value=dict(
                    toilet_pct=dict(label="Унитаз", value=data[15]),
                    bathtub_pct=dict(label="Ванна", value=data[16]),
                    sink_pct=dict(label="Раковина", value=data[17]),
                ),
            ),
            mop=psdt_mop,
        )
        score_map = ScoreMapItemWithLabels.parse_obj(score_map_raw)
        return UnifiedResponse(data=score_map)

    async def get_score_map_for_apartment_mock(
        self, apartment_id: uuid.UUID
    ) -> UnifiedResponse[ScoreMapItemWithLabels]:
        psdt_not_mop = dict(
            label="Все помещения кроме МОП",
            value=dict(
                floor=dict(
                    label="Пол",
                    value=dict(
                        no_decor=dict(label="Нет отделки", value=0.1),
                        rough_decor=dict(label="Черновая", value=0.7),
                        finishing_decor=dict(label="Чистовая", value=0.2),
                    ),
                ),
                wall=dict(
                    label="Стена",
                    value=dict(
                        no_decor=dict(label="Нет отделки", value=0.1),
                        rough_decor=dict(label="Черновая", value=0.7),
                        finishing_decor=dict(label="Чистовая", value=0.2),
                    ),
                ),
                ceiling=dict(
                    label="Потолок",
                    value=dict(
                        no_decor=dict(label="Нет отделки", value=0.1),
                        rough_decor=dict(label="Черновая", value=0.7),
                        finishing_decor=dict(label="Чистовая", value=0.2),
                    ),
                ),
            ),
        )
        psdt_mop = dict(
            label="МОП",
            value=dict(
                mop_floor=dict(
                    label="Пол",
                    value=dict(
                        no_decor=dict(label="Нет отделки", value=0.1),
                        rough_decor=dict(label="Черновая", value=0.7),
                        finishing_decor=dict(label="Чистовая", value=0.2),
                    ),
                ),
                mop_wall=dict(
                    label="Стена",
                    value=dict(
                        no_decor=dict(label="Нет отделки", value=0.1),
                        rough_decor=dict(label="Черновая", value=0.7),
                        finishing_decor=dict(label="Чистовая", value=0.2),
                    ),
                ),
                mop_ceiling=dict(
                    label="Потолок",
                    value=dict(
                        no_decor=dict(label="Нет отделки", value=0.1),
                        rough_decor=dict(label="Черновая", value=0.7),
                        finishing_decor=dict(label="Чистовая", value=0.2),
                    ),
                ),
            ),
        )
        score_map_raw = dict(
            not_mop=psdt_not_mop,
            all_places=dict(
                label="Все помещения",
                value=dict(
                    doors_pct=dict(label="Двери", value=0.2),
                    trash_bool=dict(label="Мусор", value=True),
                    switch_total=dict(label="Розетки и выключатели", value=10),
                ),
            ),
            life_zones=dict(
                label="Жилая/Кухня",
                value=dict(
                    window_decor_pct=dict(label="Отделка окна", value=0.3),
                    radiator_pct=dict(label="Установленная батарея", value=0.5),
                    kitchen_total=dict(label="Кухня", value=5),
                ),
            ),
            bathroom=dict(
                label="Ванная",
                value=dict(
                    toilet_pct=dict(label="Унитаз", value=0.45),
                    bathtub_pct=dict(label="Ванна", value=0.37),
                    sink_pct=dict(label="Раковина", value=0.64),
                ),
            ),
            mop=psdt_mop,
        )
        score_map = ScoreMapItemWithLabels.parse_obj(score_map_raw)
        return UnifiedResponse(data=score_map)

    async def update_score_map_for_apartment_mock(
        self, apartment_id: uuid.UUID, score_map: ScoreMapItemWithLabels
    ) -> UnifiedResponse[ScoreMapItemWithLabels]:
        return UnifiedResponse(data=score_map)

    async def finish_apartment_check(self, apartment_id: uuid.UUID):
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                await self._main_db_manager.projects.change_apartment_status(
                    session, apartment_id, ApartmentStatusOption.in_progress
                )
            except NoResultFound as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=404)

    async def get_projects_stats(
        self, token: Annotated[str, Depends(oauth2_scheme)]
    ) -> UnifiedResponse[ProjectsStats]:
        user_id = get_user_id_from_token(token)
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            projects_stats = (
                await self._main_db_manager.projects.get_all_projects_stats(
                    session, user_id
                )
            )

        # projects_stats = ProjectsStats(
        #     total_apartments=100,
        #     total_videos=24,
        #     apartments_approved=15
        # )
        return UnifiedResponse(data=projects_stats)

    async def get_user_projects(
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
            for verificator_id in pwu.verificators_ids:
                users_ids.add(verificator_id)

        async with self._main_db_manager.users.make_autobegin_session() as session:
            users = await self._main_db_manager.users.get_users(session, users_ids)

        users_by_ids: dict[uuid.UUID, User] = dict()
        for user in users:
            users_by_ids[user.id] = user

        projects_with_users: list[ProjectWithUsers] = []
        for project_with_users_ids in projects_with_users_ids:
            author = users_by_ids[project_with_users_ids.author_id]
            verificators = [
                users_by_ids[v] for v in project_with_users_ids.verificators_ids
            ]
            project_with_users = ProjectWithUsers(
                author=author,
                verificators=verificators,
                **project_with_users_ids.dict(),
            )
            projects_with_users.append(project_with_users)

        return UnifiedResponse(data=projects_with_users)

    # async def get_project_stats(
    #     self, project_id: uuid.UUID
    # ) -> UnifiedResponse[ProjectStats]:
    #     apartments_with_video = await self.get_apartments_by_project(project_id)
    #
    #     project_stats = ProjectStats(
    #         total_apartments=len(apartments_with_video.data),
    #         total_video_length_minutes=int(
    #             sum(
    #                 [
    #                     a.video.length_sec
    #                     for a in apartments_with_video.data
    #                     if a.video is not None
    #                 ]
    #             )
    #             / 60
    #         ),
    #         apartments_approved=sum(
    #             [
    #                 1
    #                 for a in apartments_with_video.data
    #                 if a.status == ApartmentStatusOption.approved
    #             ]
    #         ),
    #     )
    #     return UnifiedResponse(data=project_stats)

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

    async def get_project_stats(
        self,
        project_id: uuid.UUID,
    ) -> BplaProjectStats:
        pass

    async def get_projects_with_users(
        self,
    ) -> list[ProjectWithUsers]:
        pass

    async def get_project(self, project_id: uuid.UUID) -> UnifiedResponse[ProjectRead]:
        async with self._main_db_manager.projects.make_autobegin_session() as session:
            try:
                project = await self._main_db_manager.projects.get_project(
                    session, project_id
                )
                tags = await self._main_db_manager.projects.get_tags_by_project(
                    session, project_id
                )
                # user_roles_verificators = (
                #     await self._main_db_manager.projects.get_user_roles(
                #         session,
                #         project_id=project_id,
                #         role_type=RoleTypeOption.verificator,
                #     )
                # )

            except NoResultFound as e:
                return UnifiedResponse(error=exc_to_str(e), status_code=404)

        # users_ids = {urv.user_id for urv in user_roles_verificators}

        # async with self._main_db_manager.users.make_autobegin_session() as session:
        #     verificators = await self._main_db_manager.users.get_users(
        #         session, users_ids
        #     )

        project = ProjectRead(tags=tags, **project.dict())
        return UnifiedResponse(data=project)

    async def get_video_info(self, video_id: uuid.UUID) -> UnifiedResponse[Video]:
        pass

    async def get_photo_info(self, photo_id: uuid.UUID) -> UnifiedResponse[Photo]:
        pass

    async def get_content_info(
        self,
        content_id: uuid.UUID
    ) -> UnifiedResponse[Content]:
        pass

    async def get_content(
        self,
        project_id: uuid.UUID,
    ) -> UnifiedResponse[list[Content]]:
        pass

    async def upload_content(
        self,
        project_id: uuid.UUID,
        content: list[UploadFile],
    ) -> UnifiedResponse[list[Content]]:
        pass

    async def download_detect_result(
        self,
        content_id: uuid.UUID,
    ) -> FileResponse:
        pass
