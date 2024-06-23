import uuid
from collections import defaultdict
from decimal import Decimal
from typing import Optional

from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlmodel import col
from src.db.base_manager import BaseDbManager
from src.db.exceptions import ResourceAlreadyExists
from src.db.projects.models import (
    Frame,
    FrameBase,
    FrameMarkup,
    Label,
    LabelBase,
    Video,
    Project,
    RoleTypeOption,
    UserRole,
    ProjectBase,
    UserRoleBase,
    VerificationTag,
    VerificationTagBase,
    ProjectTag,
    VideoStatusOption,
    ProjectStatusOption, Photo, FrameContentTypeOption,
)
from src.server.projects.models import (
    ContentMarkupCreate,
    GpsCoords,
    ProjectWithUsersIds,
    ProjectsStats,
)


# TODO: add pagination to videos e.g.


class ProjectsDbManager(BaseDbManager):

    async def create_video(self, session: AsyncSession, video: Video) -> Video:
        return await Video.create(session, video)

    async def create_photo(self, session: AsyncSession, photo: Photo) -> Photo:
        return await Photo.create(session, photo)

    async def create_frames_with_markups(
        self, session: AsyncSession, content_markup: ContentMarkupCreate
    ) -> list[FrameMarkup]:
        # Checking if video with this id exists
        ContentType = Video if content_markup.content_type == FrameContentTypeOption.video else Photo
        stmt = (
            select(ContentType)
            .where(ContentType.id == content_markup.content_id)
        )
        content: Optional[ContentType] = (await session.execute(stmt)).scalar_one_or_none()
        if content is None:
            raise NoResultFound(f"{ContentType} with id {content_markup.content_id} not found")

        # Checking if all provided labels exist
        label_ids = set()
        for frame in content_markup.frames:
            for markup in frame.markup_list:
                label_ids.add(markup.label_id)
        stmt = select(Label.id).where(Label.project_id == content.project_id)
        available_label_ids = (await session.execute(stmt)).scalars().all()
        not_existing_labels = label_ids - set(available_label_ids)
        if len(not_existing_labels) > 0:
            raise NoResultFound(
                f"Labels with ids {', '.join([str(i) for i in not_existing_labels])} "
                f"do not exist in this project"
            )

        # Creating frames
        desired_frame_offsets = {fr.frame_offset for fr in content_markup.frames}
        stmt = (
            select(Frame.frame_offset)
            .where(Frame.content_id == content_markup.content_id)
            .where(col(Frame.frame_offset).in_(desired_frame_offsets))
        )
        existing_frame_offsets = (await session.execute(stmt)).scalars().all()
        new_frame_offsets = desired_frame_offsets - set(existing_frame_offsets)
        new_frames = []
        for tp in new_frame_offsets:
            new_frame = Frame(
                content_id=content_markup.content_id,
                frame_offset=tp,
                content_type=content_markup.content_type
            )
            new_frames.append(new_frame)
            session.add(new_frame)
        # await session.commit()

        stmt = select(Frame).where(col(Frame.frame_offset).in_(desired_frame_offsets))
        frames: list[Frame] = (await session.execute(stmt)).scalars().all()
        frame_offset_to_frame_id = {fr.frame_offset: fr.id for fr in frames}

        new_markups = []
        for frame in content_markup.frames:
            for markup in frame.markup_list:
                new_markup = FrameMarkup(
                    frame_id=frame_offset_to_frame_id[frame.frame_offset],
                    label_id=markup.label_id,
                    coord_top_left_x=markup.coord_top_left[0],
                    coord_top_left_y=markup.coord_top_left[1],
                    coord_bottom_right_x=markup.coord_bottom_right[0],
                    coord_bottom_right_y=markup.coord_bottom_right[1],
                    confidence=markup.confidence,
                )
                new_markups.append(new_markup)
                session.add(new_markup)

        # await session.commit()
        return new_markups

    async def create_labels(
        self, session: AsyncSession, project_id: uuid.UUID, labels: list[LabelBase]
    ) -> list[Label]:
        await Project.by_id(session, project_id)

        label_names = [lab.name for lab in labels]
        stmt = (
            select(Label)
            .where(Label.project_id == project_id)
            .where(col(Label.name).in_(set(label_names)))
        )
        existing_labels = (await session.execute(stmt)).scalars().all()
        if len(existing_labels) == 0:
            labels_ = []
            for label in labels:
                label_ = Label(
                    name=label.name,
                    description=label.description,
                    color=label.color,
                    project_id=project_id,
                )
                labels_.append(label_)
                session.add(label_)
            # await session.commit()
            return labels_
        else:
            existing_labels_names = [lab.name for lab in existing_labels]
            raise ResourceAlreadyExists(
                f"Labels with names {', '.join(existing_labels_names)} "
                f"already exist in this project. No new labels were created"
            )

    async def get_labels_by_project(
        self, session: AsyncSession, project_id: uuid.UUID
    ) -> list[Label]:
        await Project.by_id(session, project_id)
        stmt = select(Label).where(Label.project_id == project_id)
        labels = (await session.execute(stmt)).scalars().all()
        return labels

    async def get_video(self, session: AsyncSession, video_id: uuid.UUID) -> Video:
        return await Video.by_id(session, video_id)

    async def get_photo(self, session: AsyncSession, photo_id: uuid.UUID) -> Photo:
        return await Photo.by_id(session, photo_id)

    async def get_content(self, session: AsyncSession, content_id: uuid.UUID) -> Video | Photo:
        try:
            return await Video.by_id(session, content_id)
        except NoResultFound:
            return await Photo.by_id(session, content_id)

    async def get_content_by_frame_id(self, session: AsyncSession, frame_id: uuid.UUID) -> Video | Photo:
        stmt = select(Frame).where(Frame.id == frame_id)
        frame = (await session.execute(stmt)).scalar_one()
        try:
            return await Video.by_id(session, frame.content_id)
        except NoResultFound:
            return await Photo.by_id(session, frame.content_id)

    async def get_all_content(self, session: AsyncSession) -> list[Video | Photo]:
        stmt = select(Video)
        videos = (await session.execute(stmt)).scalars().all()
        stmt = select(Photo)
        photos = (await session.execute(stmt)).scalars().all()

        # Отсеиваем контент, принадлежащий удаленным проектам
        projects_ids: set[uuid.UUID] = set()
        for video in videos:
            projects_ids.add(video.project_id)
        for photo in photos:
            projects_ids.add(photo.project_id)

        stmt = select(Project).where(col(Project.id).in_(projects_ids))
        projects = (await session.execute(stmt)).scalars().all()
        deleted_projects_ids = {project.id for project in projects if project.is_deleted}

        videos = [video for video in videos if video.project_id not in deleted_projects_ids]
        photos = [photo for photo in photos if photo.project_id not in deleted_projects_ids]

        return videos + photos

    async def get_content_by_project(
        self,
        session: AsyncSession,
        project_id: uuid.UUID
    ) -> list[Video | Photo]:
        stmt = select(Video).where(Video.project_id == project_id)
        videos = (await session.execute(stmt)).scalars().all()
        stmt = select(Photo).where(Photo.project_id == project_id)
        photos = (await session.execute(stmt)).scalars().all()
        return videos + photos

    async def get_frame(self, session: AsyncSession, frame_id: uuid.UUID) -> Frame:
        return await Frame.by_id(session, frame_id)

    async def get_frames_by_video(
        self, session: AsyncSession, video_id: uuid.UUID
    ) -> list[Frame]:
        await Video.by_id(session, video_id)

        stmt = select(Frame).where(Frame.video_id == video_id)
        frames = (await session.execute(stmt)).scalars().all()
        return frames

    async def get_frames_with_markups(
        self, session: AsyncSession, content_id: uuid.UUID
    ) -> list[Frame]:
        try:
            await Video.by_id(session, content_id)
        except NoResultFound:
            await Photo.by_id(session, content_id)

        stmt = (
            select(Frame)
            .where(Frame.content_id == content_id)
            .options(selectinload(Frame.markups))
        )
        frames = (await session.execute(stmt)).scalars().all()
        return frames

    async def get_frame_markups(
        self,
        session: AsyncSession,
        *,
        frame_: Optional[FrameBase] = None,
        frame_id: Optional[uuid.UUID] = None,
    ) -> list[FrameMarkup]:
        assert (
            frame_ is not None or frame_id is not None
        ), "Either frame_id or (video_id, frame_offset) should not be None"

        stmt = select(Frame)

        if frame_ is not None:
            # Checking if video with this id exists
            await Video.by_id(session, frame_.video_id)
            stmt = stmt.where(Frame.video_id == frame_.video_id).where(
                Frame.frame_offset == frame_.frame_offset
            )

        if frame_id is not None:
            # Checking if frame with this id exists
            await Frame.by_id(session, frame_id)
            stmt = stmt.where(Frame.id == frame_id)

        stmt = stmt.options(selectinload(Frame.markups))

        frame = (await session.execute(stmt)).scalar_one_or_none()
        if frame is None:
            raise NoResultFound("No frame markups found")
        return frame.markups

    async def get_project(
        self, session: AsyncSession, project_id: uuid.UUID
    ) -> Project:
        return await Project.by_id(session, project_id)

    async def get_project_id_by_content_id(
        self, session: AsyncSession, content_id: uuid.UUID
    ) -> uuid.UUID:
        try:
            return (await Video.by_id(session, content_id)).project_id
        except NoResultFound:
            return (await Photo.by_id(session, content_id)).project_id

    async def get_user_roles(
        self,
        session: AsyncSession,
        *,
        user_id: Optional[uuid.UUID] = None,
        project_id: Optional[uuid.UUID] = None,
        role_type: Optional[RoleTypeOption] = None,
    ) -> list[UserRole]:
        assert (
            user_id is not None or project_id is not None
        ), "Either user_id or project_id should not be None"

        stmt = select(UserRole)

        if user_id is not None:
            # Checking if user with this id exists should be done explicitly
            # await User.by_id(session, user_id)
            stmt = stmt.where(UserRole.user_id == user_id)
        if project_id is not None:
            # Checking if project with this id exists
            await Project.by_id(session, project_id)
            stmt = stmt.where(UserRole.project_id == project_id)
        if role_type is not None:
            stmt = stmt.where(UserRole.role_type == role_type)

        stmt = stmt.options(selectinload(UserRole.project))
        # stmt = stmt.options(selectinload(UserRole.user), selectinload(UserRole.project))

        return (await session.execute(stmt)).scalars().all()

    async def create_project(
        self, session: AsyncSession, project: ProjectBase, user_id: uuid.UUID
    ) -> Project:
        # Checking if user with this id exists should be done explicitly

        new_project = Project.parse_obj(project)
        session.add(new_project)

        new_user_role = UserRole(
            user_id=user_id, project_id=new_project.id, role_type=RoleTypeOption.author
        )
        session.add(new_user_role)

        return new_project

    async def create_user_role(
        self, session: AsyncSession, user_role: UserRoleBase
    ) -> UserRole:
        # Checking if user with this id exists should be done explicitly

        # Checking if project with this id exists
        await Project.by_id(session, user_role.project_id)

        existing_user_role = (
            await session.execute(
                select(UserRole)
                .where(UserRole.role_type == user_role.role_type)
                .where(UserRole.user_id == user_role.user_id)
                .where(UserRole.project_id == user_role.project_id)
            )
        ).scalar_one_or_none()
        if existing_user_role is None:
            created_user_role = await UserRole.create(session, user_role)
            return created_user_role
        else:
            raise ResourceAlreadyExists(
                f"User role with role_type {user_role.role_type}, "
                f"user_id {user_role.user_id} and "
                f"project_id {user_role.project_id} already exists"
            )

    async def delete_project(
        self, session: AsyncSession, project_id: uuid.UUID
    ) -> Project:
        project = await Project.by_id(session, project_id)
        project.is_deleted = True
        session.add(project)
        return project

    async def create_verification_tags(
        self, session: AsyncSession, tags: set[VerificationTagBase]
    ) -> list[VerificationTag]:
        # TODO: do it gently with sqlalchemy insert and on_conflict_do_nothing()
        # tags_to_insert = [VerificationTag.parse_obj(tag) for tag in tags]
        # stmt = insert(VerificationTag).values(tags_to_insert).on_conflict_do_nothing()
        # await session.execute(stmt)
        # return tags_to_insert
        existing_tags = await self.get_all_verification_tags(session)
        existing = {(t.tagname, t.groupname) for t in existing_tags}
        tags_to_create: list[VerificationTag] = list()
        for tag in tags:
            if (tag.tagname, tag.groupname) not in existing:
                tags_to_create.append(VerificationTag.parse_obj(tag))
        session.add_all(tags_to_create)
        return tags_to_create

    async def get_all_verification_tags(
        self, session: AsyncSession
    ) -> list[VerificationTag]:
        stmt = select(VerificationTag)
        return (await session.execute(stmt)).scalars().all()

    async def get_verification_tags(
        self, session: AsyncSession, tags_ids: set[uuid.UUID]
    ) -> list[VerificationTag]:
        stmt = select(VerificationTag).where(col(VerificationTag.id).in_(tags_ids))
        tags = (await session.execute(stmt)).scalars().all()
        not_existing_tags_ids = set(tags_ids) - set([t.id for t in tags])
        if len(not_existing_tags_ids) != 0:
            raise NoResultFound(
                f"Tags with ids {not_existing_tags_ids} were not found in the DB"
            )
        return tags

    async def create_project_tags(
        self, session: AsyncSession, project_id: uuid.UUID, tags: list[tuple[uuid.UUID, Optional[float]]]
    ) -> list[ProjectTag]:
        """
        Will add new project tags. If some already exist it'll be OK
        :returns newly created project tags
        """
        tags_ids = set([tag_id for tag_id, _ in tags])
        tag_id_to_confidence = {tag_id: conf for tag_id, conf in tags}
        await Project.by_id(session, project_id)
        await self.get_verification_tags(session, tags_ids)

        # TODO: implement it with upsert with on conflict update updated_at field only
        stmt = select(ProjectTag.tag_id).where(ProjectTag.project_id == project_id)
        # .options(selectinload(ProjectTag.tag), selectinload(ProjectTag.project))
        current_project_tags_ids: set[uuid.UUID] = set(
            (await session.execute(stmt)).scalars().all()
        )
        new_tags_ids = set(tags_ids) - current_project_tags_ids

        # stmt = select(VerificationTag).where(col(VerificationTag.id).in_(new_tags_ids))
        # new_tags = (await session.execute(stmt)).scalars().all()

        # new_project_tags = [ProjectTag(project_id=project_id, tag_id=tag.id, tag=tag) for tag in new_tags]
        new_project_tags = [ProjectTag(
            project_id=project_id,
            tag_id=tag_id,
            confidence_threshold=tag_id_to_confidence[tag_id]
        ) for tag_id in new_tags_ids]
        session.add_all(new_project_tags)
        return new_project_tags

    async def get_tags_by_project(
        self,
        session: AsyncSession,
        project_id: uuid.UUID,
    ) -> list[tuple[VerificationTag, Decimal]]:
        await Project.by_id(session, project_id)
        stmt = (
            select(ProjectTag)
            .where(ProjectTag.project_id == project_id)
            .options(selectinload(ProjectTag.tag))
        )
        project_tags: list[ProjectTag] = (await session.execute(stmt)).scalars().all()
        tags = [(pt.tag, pt.confidence_threshold) for pt in project_tags]

        return tags

    async def get_label_to_verification_tag_mapping(
        self,
        session: AsyncSession,
        verification_tag_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, uuid.UUID]:
        # TODO: метод надо переделывать. Не обязательно tagname должен быть в description у лейбла
        stmt = select(VerificationTag).where(col(VerificationTag.id).in_(verification_tag_ids))
        tags = (await session.execute(stmt)).scalars().all()
        tagnames = [tag.tagname for tag in tags]
        tag_id_by_tagname = {tag.tagname: tag.id for tag in tags}

        stmt = (
            select(Label)
            .where(col(Label.description).in_(tagnames))
        )
        labels = (await session.execute(stmt)).scalars().all()
        verification_tag_id_by_label_id: dict[uuid.UUID, uuid.UUID] = dict()
        for label in labels:
            verification_tag_id_by_label_id[label.id] = tag_id_by_tagname[label.description]
        return verification_tag_id_by_label_id

    async def write_gps_coords(
        self, session: AsyncSession, video_id: uuid.UUID, gps_coords: GpsCoords
    ) -> Video:
        video = await Video.by_id(session, video_id)
        video.description = gps_coords.json()
        session.add(video)
        return video

    async def get_projects_with_users_ids(
        self, session: AsyncSession, user_id: uuid
    ) -> list[ProjectWithUsersIds]:
        stmt = select(UserRole).where(UserRole.user_id == user_id)
        user_roles_by_user: list[UserRole] = (
            (await session.execute(stmt)).scalars().all()
        )

        projects_ids = {ur.project_id for ur in user_roles_by_user}

        stmt = select(UserRole).where(col(UserRole.project_id).in_(projects_ids))
        user_roles: list[UserRole] = (await session.execute(stmt)).scalars().all()

        user_roles_by_project_id: defaultdict[uuid.UUID, list[UserRole]] = defaultdict(
            list
        )
        for user_role in user_roles:
            user_roles_by_project_id[user_role.project_id].append(user_role)

        stmt = select(Project).where(col(Project.id).in_(projects_ids))
        projects: list[Project] = (await session.execute(stmt)).scalars().all()

        project_by_id: dict[uuid.UUID, Project] = dict()
        for project in projects:
            project_by_id[project.id] = project

        projects_with_users_ids: list[ProjectWithUsersIds] = []
        for project_id, usr_rls in user_roles_by_project_id.items():
            # Skipping deleted projects
            if project_by_id[project_id].is_deleted:
                continue
            author_id = None
            for ur in usr_rls:
                if ur.role_type == RoleTypeOption.author:
                    author_id = ur.user_id
            project_with_users_ids = ProjectWithUsersIds(
                author_id=author_id,
                **project_by_id[project_id].dict(),
            )
            projects_with_users_ids.append(project_with_users_ids)

        return projects_with_users_ids

    async def change_content_status(
        self,
        session: AsyncSession,
        content_id: uuid.UUID,
        status: VideoStatusOption,
    ) -> Photo | Video:
        try:
            content = await Video.by_id(session, content_id)
        except NoResultFound:
            content = await Photo.by_id(session, content_id)
        content.status = status
        session.add(content)
        return content

    async def set_notification_sent_status(
        self,
        session: AsyncSession,
        content_id: uuid.UUID,
        status: bool,
    ) -> Photo | Video:
        try:
            content = await Video.by_id(session, content_id)
        except NoResultFound:
            content = await Photo.by_id(session, content_id)
        content.notification_sent = status
        session.add(content)
        return content

    async def update_markups_for_frame(
        self,
        session: AsyncSession,
        frame_id: uuid.UUID,
        markups_to_delete: list[uuid.UUID],
        new_markups: list[FrameMarkup],
    ) -> list[FrameMarkup]:
        # stmt = select(Frame).where(Frame.id == frame_id)
        # frame = (await session.execute(stmt)).scalar_one()
        stmt = select(FrameMarkup).where(col(FrameMarkup.id).in_(markups_to_delete))
        frame_markups = (await session.execute(stmt)).scalars().all()
        for frame_markup in frame_markups:
            await session.delete(frame_markup)
        await session.flush()
        # frame.markups = [markup for markup in frame.markups if markup.id not in markups_to_delete]
        # session.add(frame)
        session.add_all(new_markups)
        await session.flush()
        return new_markups
