from typing import Optional
from uuid import UUID

from starlette.responses import FileResponse

import settings
from fastapi import APIRouter, Depends

from common.rabbitmq.publisher import Publisher
from src.db.main_db_manager import MainDbManager
from src.db.projects.models import (
    Frame,
    FrameMarkup,
    Label,
    Video,
    UserRole,
    Project,
    VerificationTag, Photo,
)
from src.server.auth import Auth
from src.server.common import METHOD, UnifiedResponse
from src.server.projects.endpoints import ProjectsEndpoints
from src.server.projects.models import (
    FramesWithMarkupRead,
    UserRoleWithProjectRead,
    ProjectRead,
    ProjectsStats,
    ProjectWithUsers,
    BplaProjectStats,
    Content,
)


class ProjectsRouter:
    def __init__(self, main_db_manager: MainDbManager, publisher: Publisher):
        self._projects_endpoints = ProjectsEndpoints(main_db_manager, publisher)

        self.router = APIRouter(
            prefix=f"{settings.API_PREFIX}/projects",
            tags=["projects"],
        )

        self.router.add_api_route(
            path="/frames-with-markups",
            endpoint=self._projects_endpoints.get_frames_with_markups,
            response_model=UnifiedResponse[list[FramesWithMarkupRead]],
            methods=[METHOD.GET],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/content-status",
            endpoint=self._projects_endpoints.change_content_status,
            response_model=UnifiedResponse[Video],
            methods=[METHOD.POST],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/video-file",
            endpoint=self._projects_endpoints.get_video_file,
            methods=[METHOD.GET],
        )

        self.router.add_api_route(
            path="/labels",
            endpoint=self._projects_endpoints.get_labels_by_project,
            response_model=UnifiedResponse[list[Label]],
            methods=[METHOD.GET],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/project-stats",
            endpoint=self._projects_endpoints.get_project_stats,
            response_model=UnifiedResponse[BplaProjectStats],
            methods=[METHOD.GET],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/projects-all-stats",
            endpoint=self._projects_endpoints.get_projects_all_stats,
            response_model=UnifiedResponse[BplaProjectStats],
            methods=[METHOD.GET],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/content-ids-by-project",
            endpoint=self._projects_endpoints.get_content_ids_by_project,
            response_model=UnifiedResponse[list[UUID]],
            methods=[METHOD.GET],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/verification-tags",
            endpoint=self._projects_endpoints.get_all_verification_tags,
            response_model=UnifiedResponse[list[VerificationTag]],
            methods=[METHOD.GET],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/projects-with-users",
            endpoint=self._projects_endpoints.get_projects_with_users,
            response_model=UnifiedResponse[list[ProjectWithUsers]],
            methods=[METHOD.GET],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/project",
            endpoint=self._projects_endpoints.create_project,
            response_model=UnifiedResponse[ProjectRead],
            methods=[METHOD.POST],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/project",
            endpoint=self._projects_endpoints.get_project,
            response_model=UnifiedResponse[ProjectRead],
            methods=[METHOD.GET],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/project",
            endpoint=self._projects_endpoints.delete_project,
            response_model=UnifiedResponse[Project],
            methods=[METHOD.DELETE],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/video-info",
            endpoint=self._projects_endpoints.get_video_info,
            response_model=UnifiedResponse[Video],
            methods=[METHOD.GET],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/photo-info",
            endpoint=self._projects_endpoints.get_photo_info,
            response_model=UnifiedResponse[Photo],
            methods=[METHOD.GET],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/content-info",
            endpoint=self._projects_endpoints.get_content_info,
            response_model=UnifiedResponse[Content],
            methods=[METHOD.GET],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/content-by-project",
            endpoint=self._projects_endpoints.get_content_by_project,
            response_model=UnifiedResponse[list[Content]],
            methods=[METHOD.GET],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/create-upload-content",
            endpoint=self._projects_endpoints.upload_content,
            response_model=UnifiedResponse[list[Content]],
            methods=[METHOD.POST],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/download_detect_result",
            endpoint=self._projects_endpoints.download_detect_result,
            response_class=FileResponse,
            methods=[METHOD.GET],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/send-image-to-model",
            endpoint=self._projects_endpoints.send_image_to_model_service,
            methods=[METHOD.GET],
            dependencies=[Depends(Auth(main_db_manager))],
        )




