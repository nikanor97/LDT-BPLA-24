from typing import Optional, Annotated
from uuid import UUID

from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy.exc import NoResultFound

from src.db.main_db_manager import MainDbManager
from src.db.projects.models import ProjectStatusOption, ProjectBase, VerificationTag
from src.server.auth_utils import oauth2_scheme, get_user_id_from_token
from src.server.common import UnifiedResponse, exc_to_str
from src.server.projects.endpoints import ProjectsEndpoints


class ProjectCreate(BaseModel):
    name: str
    # description: Optional[str] = Field(nullable=True, default=None)
    status: Optional[ProjectStatusOption]
    # document_id: Optional[UUID]
    is_deleted: Optional[bool]
    # deadline_at: Optional[date] = Field(nullable=True)
    tags_ids: list[UUID]  # ids of VerificationTags
    # verificators_ids: list[uuid.UUID]  # ids of verificator users that will be attached to the project
    message_receiver: str  # TODO: это кто?


class ProjectRead(BaseModel):
    id: UUID
    name: str
    # description: Optional[str] = Field(nullable=True, default=None)
    status: Optional[ProjectStatusOption]
    # document_id: Optional[UUID]
    is_deleted: Optional[bool]
    # deadline_at: Optional[date] = Field(nullable=True)
    tags: list[VerificationTag]
    # verificators: Optional[list[User]]


class CreateProject(ProjectsEndpoints):
    def __init__(self, main_db_manager: MainDbManager):
        super().__init__(main_db_manager)

    async def __call__(self, project: ProjectCreate, token: Annotated[str, Depends(oauth2_scheme)]
        ) -> UnifiedResponse[ProjectRead]:

        proj = ProjectBase.parse_obj(project)
        user_id = get_user_id_from_token(token)

        # Checking whether user with user_id exists
        async with self._main_db_manager.users.make_autobegin_session() as session:
            try:
                user = await self._main_db_manager.users.get_user_or_error(session, user_id)
            except NoResultFound as e:
                return UnifiedResponse(error=exc_to_str(user), status_code=404)

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