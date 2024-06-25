import uuid
from collections import defaultdict
from decimal import Decimal
from typing import Optional

from sqlalchemy import update, case
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlmodel import col
from src.db.base_manager import BaseDbManager
from src.db.exceptions import ResourceAlreadyExists
from src.db.projects.models import (
    Frame,
    FrameMarkup,
    Label,
    LabelBase,
    Video,
    Project,
    RoleTypeOption,
    UserRole,
    ProjectBase,
    VerificationTag,
    VerificationTagBase,
    ProjectTag,
    VideoStatusOption,
    Photo
)
from src.server.projects.models import ProjectWithUsersIds


# TODO: add pagination to videos e.g.


class ProjectsDbManager(BaseDbManager):

    async def create_video(self, session: AsyncSession, video: Video) -> Video:
        return await Video.create(session, video)

    async def create_photo(self, session: AsyncSession, photo: Photo) -> Photo:
        return await Photo.create(session, photo)

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

    async def get_content_by_project(
        self,
        session: AsyncSession,
        project_id: uuid.UUID
    ) -> list[Video | Photo]:
        stmt = select(Photo).where(Photo.project_id == project_id).order_by(Photo.name)
        photos = (await session.execute(stmt)).scalars().all()
        stmt = select(Video).where(Video.project_id == project_id).order_by(Video.name)
        videos = (await session.execute(stmt)).scalars().all()
        return photos + videos

    # async def get_content_with_markups_count_by_project(
    #     self,
    #     session: AsyncSession,
    #     project_id: uuid.UUID
    # ) -> list[tuple[Video | Photo, int]]:
    #
    #     tags = await self.get_tags_by_project(
    #         session, project_id
    #     )
    #     label_to_verification_tag_mapping: dict[
    #         uuid.UUID, uuid.UUID] = await self.get_label_to_verification_tag_mapping(
    #         session, [t[0].id for t in tags]
    #     )
    #
    #     stmt = select(Photo).where(Photo.project_id == project_id).order_by(Photo.name)
    #     photos: list[Photo] = (await session.execute(stmt)).scalars().all()
    #     stmt = select(Video).where(Video.project_id == project_id).order_by(Video.name)
    #     videos: list[Video] = (await session.execute(stmt)).scalars().all()
    #     frames = await self.get_frames_with_markups_by_content_ids(
    #         session,
    #         [photo.id for photo in photos] + [video.id for video in videos]
    #     )
    #     frame_id_to_content_id = {frame.id: frame.content_id for frame in frames}
    #
    #     # frames = await self._main_db_manager.projects.get_frames_with_markups(
    #     #     session, content_id
    #     # )
    #
    #     tag_id_to_confidence = {t[0].id: t[1] for t in tags}
    #     # frame_id_cnt_markups: defaultdict[uuid.UUID, int] = defaultdict(int)
    #     content_id_cnt_markups: defaultdict[uuid.UUID, int] = defaultdict(int)
    #     # TODO: ненужная логика. надо пересмотреть подход с verification_tag и лейблами
    #     for idx, frame in enumerate(frames):
    #         for idx_markup, markup in enumerate(frame.markups):
    #             if markup.label_id in label_to_verification_tag_mapping:
    #                 verification_tag_id = label_to_verification_tag_mapping[markup.label_id]
    #                 if verification_tag_id in tag_id_to_confidence and markup.confidence >= tag_id_to_confidence[
    #                     verification_tag_id]:
    #                     # frame_id_cnt_markups[frame.id] += 1
    #                     content_id_cnt_markups[frame_id_to_content_id[frame.id]] += 1
    #     res = [(content, content_id_cnt_markups[content.id]) for content in photos + videos]
    #     return res

    async def get_content_by_projects(
        self,
        session: AsyncSession,
        project_ids: list[uuid.UUID]
    ) -> list[Video | Photo]:
        stmt = select(Video).where(col(Video.project_id).in_(project_ids))
        videos = (await session.execute(stmt)).scalars().all()
        stmt = select(Photo).where(col(Photo.project_id).in_(project_ids))
        photos = (await session.execute(stmt)).scalars().all()
        return videos + photos

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

    async def get_frames_with_markups_by_content_ids(
        self, session: AsyncSession, content_ids: list[uuid.UUID]
    ) -> list[Frame]:
        stmt = (
            select(Frame)
            .where(col(Frame.content_id).in_(content_ids))
            .options(selectinload(Frame.markups))
        )
        frames = (await session.execute(stmt)).scalars().all()
        return frames

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
        current_project_tags_ids: set[uuid.UUID] = set(
            (await session.execute(stmt)).scalars().all()
        )
        new_tags_ids = set(tags_ids) - current_project_tags_ids

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
        stmt = select(FrameMarkup).where(col(FrameMarkup.id).in_(markups_to_delete))
        frame_markups = (await session.execute(stmt)).scalars().all()
        for frame_markup in frame_markups:
            await session.delete(frame_markup)
        await session.flush()
        session.add_all(new_markups)
        await session.flush()
        return new_markups

    async def increase_content_detected_cnt(
        self,
        session: AsyncSession,
        content_id: uuid.UUID,
        increase_by_number: int
    ) -> None:
        # content: Photo | Video = await self.get_content(session, content_id)
        # if content.detected_cnt is None:
        #     content.detected_cnt = increase_by_number
        # else:
        #     content.detected_cnt += increase_by_number
        # session.add(content)
        # await session.flush()

        stmt = (
            update(Photo)
            .where(Photo.id == content_id)
            .values(detected_cnt=case(
                [(Photo.detected_cnt == None, increase_by_number)],
                else_=Photo.detected_cnt + increase_by_number
            ))
        )
        await session.execute(stmt)

        stmt = (
            update(Video)
            .where(Video.id == content_id)
            .values(detected_cnt=case(
                [(Video.detected_cnt == None, increase_by_number)],
                else_=Video.detected_cnt + increase_by_number
            ))
        )
        await session.execute(stmt)
