import uuid
from collections import defaultdict
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
    Apartment,
    Project,
    RoleTypeOption,
    UserRole,
    ProjectBase,
    UserRoleBase,
    ProjectDocument,
    VerificationTag,
    VerificationTagBase,
    ProjectTag,
    VideoStatusOption,
    ApartmentStatusOption,
    ProjectStatusOption,
)
from src.server.projects.models import (
    VideoMarkupCreate,
    GpsCoords,
    ProjectWithUsersIds,
    ApartmentWithVideo,
    ProjectsStats,
)


# TODO: add pagination to videos e.g.


class ProjectsDbManager(BaseDbManager):
    async def get_apartment(
        self, session: AsyncSession, apartment_id: uuid.UUID
    ) -> Apartment:
        return await Apartment.by_id(session, apartment_id)

    async def create_video(self, session: AsyncSession, video: Video) -> Video:
        await Apartment.by_id(session, video.apartment_id)
        return await Video.create(session, video)

    # async def create_frame(
    #     self,
    #     session: AsyncSession,
    #     frame: FrameBase,
    # ) -> Frame:
    #     # Checking if project with this id exists
    #     await Video.by_id(session, frame.video_id)
    #
    #     stmt = select(Frame).where(Frame.video_id == frame.video_id).where(Frame.frame_offset == frame.frame_offset)
    #     existing_frame = (await session.execute(stmt)).scalar_one_or_none()
    #     if existing_frame is None:
    #         return await Frame.create(session, frame)
    #     else:
    #         raise ResourceAlreadyExists(f"Frame with video_id {frame.video_id} "
    #                                     f"and frame_offset {frame.frame_offset} already exists")
    #
    # async def create_markup(self, session: AsyncSession, frame_markup: FrameMarkupBase) -> FrameMarkup:
    #     # Checking if frame with this id exists
    #     await Frame.by_id(session, frame_markup.frame_id)
    #
    #     label = (await session.execute(select(Label).where(Label.id == frame_markup.label_id))).scalar_one_or_none()
    #     if label is None:
    #         raise NoResultFound(f"Label with id {frame_markup.label_id} was not found")
    #
    #     return await FrameMarkup.create(session, frame_markup)

    async def create_frames_with_markups(
        self, session: AsyncSession, video_markup: VideoMarkupCreate
    ) -> list[FrameMarkup]:
        # Checking if video with this id exists
        stmt = (
            select(Video)
            .where(Video.id == video_markup.video_id)
            .options(selectinload(Video.apartment))
        )
        video: Optional[Video] = (await session.execute(stmt)).scalar_one_or_none()
        if video is None:
            raise NoResultFound(f"Video with id {video_markup.video_id} not found")

        # Checking if all provided labels exist
        label_ids = set()
        for frame in video_markup.frames:
            for markup in frame.markup_list:
                label_ids.add(markup.label_id)
        stmt = select(Label.id).where(Label.project_id == video.apartment.project_id)
        available_label_ids = (await session.execute(stmt)).scalars().all()
        not_existing_labels = label_ids - set(available_label_ids)
        if len(not_existing_labels) > 0:
            raise NoResultFound(
                f"Labels with ids {', '.join([str(i) for i in not_existing_labels])} "
                f"do not exist in this project"
            )

        # Creating frames
        desired_frame_offsets = {fr.frame_offset for fr in video_markup.frames}
        stmt = (
            select(Frame.frame_offset)
            .where(Frame.video_id == video_markup.video_id)
            .where(col(Frame.frame_offset).in_(desired_frame_offsets))
        )
        existing_frame_offsets = (await session.execute(stmt)).scalars().all()
        new_frame_offsets = desired_frame_offsets - set(existing_frame_offsets)
        new_frames = []
        for tp in new_frame_offsets:
            new_frame = Frame(video_id=video_markup.video_id, frame_offset=tp)
            new_frames.append(new_frame)
            session.add(new_frame)
        # await session.commit()

        stmt = select(Frame).where(col(Frame.frame_offset).in_(desired_frame_offsets))
        frames: list[Frame] = (await session.execute(stmt)).scalars().all()
        frame_offset_to_frame_id = {fr.frame_offset: fr.id for fr in frames}

        new_markups = []
        for frame in video_markup.frames:
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

    # async def get_apartments_by_project(
    #     self, session: AsyncSession, project_id: uuid.UUID
    # ) -> list[Video]:
    #     # Checking of the project existence should be done explicitly
    #     stmt = select(Video).where(Video.project_id == project_id)
    #
    #     return (await session.execute(stmt)).scalars().all()

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
        self, session: AsyncSession, video_id: uuid.UUID
    ) -> list[Frame]:
        await Video.by_id(session, video_id)

        stmt = (
            select(Frame)
            .where(Frame.video_id == video_id)
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

    # async def get_videos_by_owner(
    #     self, session: AsyncSession, owner_id: uuid.UUID
    # ) -> list[Video]:
    #     # Checking that user with owner_id exists should be done explicitly
    #
    #     stmt = select(Video).where(Video.owner_id == owner_id)
    #     videos = (await session.execute(stmt)).scalars().all()
    #     return videos

    # async def assign_videos_to_project(
    #     self, session: AsyncSession, video_ids: list[uuid.UUID], project_id: uuid.UUID
    # ) -> list[Video]:
    #     for video_id in video_ids:
    #         await Video.by_id(session, video_id)
    #
    #     stmt = select(Video).where(col(Video.id).in_(set(video_ids)))
    #     videos: list[Video] = (await session.execute(stmt)).scalars().all()
    #
    #     for idx, _ in enumerate(videos):
    #         videos[idx].project_id = project_id
    #         session.add(videos[idx])
    #
    #     await session.commit()
    #     return videos

    async def get_project(
        self, session: AsyncSession, project_id: uuid.UUID
    ) -> Project:
        return await Project.by_id(session, project_id)

    async def get_apartments_with_video_by_project(
        self, session: AsyncSession, project_id: uuid.UUID
    ) -> list[ApartmentWithVideo]:
        stmt = (
            select(Apartment)
            .where(Apartment.project_id == project_id)
            .options(selectinload(Apartment.videos))
        )
        apartments: list[Apartment] = (await session.execute(stmt)).scalars().all()

        apartments_with_video: list[ApartmentWithVideo] = []
        for idx, apartment in enumerate(apartments):
            video = None
            if len(apartment.videos) > 0:
                video = sorted(apartment.videos, key=lambda x: x.created_at)[-1]
            apartment_with_video = ApartmentWithVideo(video=video, **apartment.dict())
            apartments_with_video.append(apartment_with_video)
        apartments_with_video = sorted(
            apartments_with_video, key=lambda x: x.created_at
        )
        return apartments_with_video

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

    async def create_project_document(
        self, session: AsyncSession, project_doc: ProjectDocument
    ) -> ProjectDocument:
        if project_doc.project_id is not None:
            await Project.by_id(session, project_doc.project_id)
        project_document = await ProjectDocument.create(session, project_doc)
        return project_document

    async def get_project_document(
        self, session: AsyncSession, document_id: uuid.UUID
    ) -> ProjectDocument:
        return await ProjectDocument.by_id(session, document_id)

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
        self, session: AsyncSession, project_id: uuid.UUID, tags_ids: set[uuid.UUID]
    ) -> list[ProjectTag]:
        """
        Will add new project tags. If some already exist it'll be OK
        :returns newly created project tags
        """
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
        new_project_tags = [
            ProjectTag(project_id=project_id, tag_id=tag_id) for tag_id in new_tags_ids
        ]
        session.add_all(new_project_tags)
        return new_project_tags

    async def get_tags_by_project(
        self,
        session: AsyncSession,
        project_id: uuid.UUID,
    ) -> list[VerificationTag]:
        await Project.by_id(session, project_id)
        stmt = (
            select(ProjectTag)
            .where(ProjectTag.project_id == project_id)
            .options(selectinload(ProjectTag.tag))
        )
        project_tags: list[ProjectTag] = (await session.execute(stmt)).scalars().all()
        tags = [pt.tag for pt in project_tags]

        return tags

    async def get_videos_by_apartment(
        self, session: AsyncSession, apartment_id: uuid.UUID
    ) -> list[Video]:
        await Apartment.by_id(session, apartment_id)
        stmt = (
            select(Apartment)
            .where(Apartment.id == apartment_id)
            .options(selectinload(Apartment.videos))
        )
        apartment: Apartment = (await session.execute(stmt)).scalar()
        return apartment.videos

    async def change_video_status(
        self, session: AsyncSession, video_id: uuid.UUID, new_status: VideoStatusOption
    ) -> Video:
        video = await Video.by_id(session, video_id)
        video.status = new_status
        session.add(video)

        apartment = await Apartment.by_id(session, video.apartment_id)
        project = await Project.by_id(session, apartment.project_id)

        if new_status == VideoStatusOption.declined:
            apartment.status = ApartmentStatusOption.declined

        if new_status in {VideoStatusOption.approved, VideoStatusOption.extracted}:
            if project.status == ProjectStatusOption.created:
                project.status = ProjectStatusOption.in_progress
            if apartment.status == ApartmentStatusOption.created:
                apartment.status = ApartmentStatusOption.in_progress

        if new_status == VideoStatusOption.approved:
            apartment.status = ApartmentStatusOption.approved

            apartments_by_project = await self.get_apartments_with_video_by_project(
                session, apartment.project_id
            )
            if all(
                [
                    a.status == ApartmentStatusOption.approved
                    for a in apartments_by_project
                ]
            ):
                project.status = ProjectStatusOption.finished

        session.add(apartment)
        session.add(project)

        return video

    async def change_apartment_status(
        self,
        session: AsyncSession,
        apartment_id: uuid.UUID,
        new_status: ApartmentStatusOption,
    ) -> Apartment:
        apartment = await Apartment.by_id(session, apartment_id)
        apartment.status = new_status
        session.add(apartment)
        return apartment

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
            verificators_ids = []
            for ur in usr_rls:
                if ur.role_type == RoleTypeOption.author:
                    author_id = ur.user_id
                elif ur.role_type == RoleTypeOption.verificator:
                    verificators_ids.append(ur.user_id)
            project_with_users_ids = ProjectWithUsersIds(
                author_id=author_id,
                verificators_ids=verificators_ids,
                **project_by_id[project_id].dict(),
            )
            projects_with_users_ids.append(project_with_users_ids)

        return projects_with_users_ids

    async def get_all_projects_stats(
        self, session: AsyncSession, user_id: uuid.UUID
    ) -> ProjectsStats:
        projects = await self.get_projects_with_users_ids(session, user_id)
        projects_ids = {p.id for p in projects}

        stmt = select(Apartment).where(col(Apartment.project_id).in_(projects_ids))
        related_apartments = (await session.execute(stmt)).scalars().all()
        related_apartments_ids = {ra.id for ra in related_apartments}

        stmt = select(Video.apartment_id)
        apartments_ids = (await session.execute(stmt)).scalars().all()

        apartments_ids = set(apartments_ids).intersection(related_apartments_ids)

        n_appartments_approved = sum(
            [
                1
                for a in related_apartments
                if a.status == ApartmentStatusOption.approved
            ]
        )

        stats = ProjectsStats(
            total_apartments=len(related_apartments),
            total_videos=len(apartments_ids),
            apartments_approved=n_appartments_approved,
        )
        return stats
