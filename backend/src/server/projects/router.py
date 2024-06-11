from typing import Optional

import settings
from fastapi import APIRouter, Depends

from common.rabbitmq.publisher import Publisher
from src.db.main_db_manager import MainDbManager
from src.db.projects.models.frame import Frame
from src.db.projects.models.frame_markup import FrameMarkup
from src.db.projects.models.label import Label
from src.db.projects.models.project import Project
from src.db.projects.models.project_document import ProjectDocument
from src.db.projects.models.user_role import UserRole
from src.db.projects.models.verification_tag import VerificationTag
from src.db.projects.models.video import Video
from src.server.auth import Auth
from src.server.common import METHOD, UnifiedResponse
from src.server.projects.endpoints import ProjectsEndpoints
from src.server.projects.models import (
    FramesWithMarkupRead,
    UserRoleWithProjectRead,
    ProjectRead,
    ProjectsStats,
    ProjectWithUsers,
    ApartmentWithVideo,
    ProjectStats,
    ProjectScores,
    ApartmentWithPlans,
    ScoreMapItemWithLabels,
)


class ProjectsRouter:
    def __init__(self, main_db_manager: MainDbManager, publisher: Publisher):
        self._projects_endpoints = ProjectsEndpoints(main_db_manager, publisher)

        self.router = APIRouter(
            prefix=f"{settings.API_PREFIX}/projects",
            tags=["projects"],
        )

        self.router.add_api_route(
            path="/create-upload-video",
            endpoint=self._projects_endpoints.create_and_upload_video,
            response_model=UnifiedResponse[Video],
            methods=[METHOD.POST],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/frames-with-markups",
            endpoint=self._projects_endpoints.create_frames_with_markups,
            response_model=UnifiedResponse[list[FrameMarkup]],
            methods=[METHOD.POST],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/frames-with-markups",
            endpoint=self._projects_endpoints.get_frames_with_markups,
            response_model=UnifiedResponse[list[FramesWithMarkupRead]],
            methods=[METHOD.GET],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/labels",
            endpoint=self._projects_endpoints.create_labels,
            response_model=UnifiedResponse[list[Label]],
            methods=[METHOD.POST],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/labels",
            endpoint=self._projects_endpoints.get_labels_by_project,
            response_model=UnifiedResponse[list[Label]],
            methods=[METHOD.GET],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/video",
            endpoint=self._projects_endpoints.get_video,
            response_model=UnifiedResponse[Video],
            methods=[METHOD.GET],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/videos-by-apartment",
            endpoint=self._projects_endpoints.get_videos_by_apartment,
            response_model=UnifiedResponse[list[Video]],
            methods=[METHOD.GET],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/frame",
            endpoint=self._projects_endpoints.get_frame,
            response_model=UnifiedResponse[Frame],
            methods=[METHOD.GET],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/frames-by-video",
            endpoint=self._projects_endpoints.get_frames_by_video,
            response_model=UnifiedResponse[list[Frame]],
            methods=[METHOD.GET],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/frame-markups",
            endpoint=self._projects_endpoints.get_frame_markups,
            response_model=UnifiedResponse[list[FrameMarkup]],
            methods=[METHOD.GET],
            description="Get markups for given frame. "
            "Frame can be given with frame_id or with pair (video_id, time_point)",
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/stream-video",
            endpoint=self._projects_endpoints.stream_video,
            methods=[METHOD.GET],
            # dependencies=[Depends(Auth(main_db_manager))],
        )
        #
        self.router.add_api_route(
            path="/streaming-example",
            endpoint=self._projects_endpoints.streaming_example,
        )

        self.router.add_api_route(
            path="/video-file",
            endpoint=self._projects_endpoints.get_video_file,
            methods=[METHOD.GET],
        )

        self.router.add_api_route(
            path="/user-role",
            endpoint=self._projects_endpoints.create_user_role,
            response_model=UnifiedResponse[UserRole],
            methods=[METHOD.POST],
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
#----------
        self.router.add_api_route(
            path="/user-role",
            endpoint=self._projects_endpoints.get_user_roles,
            response_model=UnifiedResponse[list[UserRoleWithProjectRead]],
            methods=[METHOD.GET],
            description="Get roles user_id or/and by project_id."
            "Optionally results can be filtered by role_type "
            "(E.g. getting all verificators for the particular project)",
            responses={
                404: {
                    "description": "user_id/project_id is not specified or "
                    "user/project by requested parameters was not found"
                }
            },
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/project-document",
            endpoint=self._projects_endpoints.create_and_upload_project_document,
            response_model=UnifiedResponse[ProjectDocument],
            methods=[METHOD.POST],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/apartments-by-project",
            endpoint=self._projects_endpoints.get_apartments_by_project,
            response_model=UnifiedResponse[list[ApartmentWithVideo]],
            methods=[METHOD.GET],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/apartment",
            endpoint=self._projects_endpoints.get_apartment,
            response_model=UnifiedResponse[ApartmentWithPlans],
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
            path="/video-status",
            endpoint=self._projects_endpoints.change_video_status,
            response_model=UnifiedResponse[Video],
            methods=[METHOD.POST],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/gps",
            endpoint=self._projects_endpoints.write_gps,
            response_model=UnifiedResponse[Video],
            methods=[METHOD.POST],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/download-score-map",
            endpoint=self._projects_endpoints.get_score_map,
            methods=[METHOD.GET],
            # dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/finish-apartment-check",
            endpoint=self._projects_endpoints.finish_apartment_check,
            methods=[METHOD.GET],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/stats",
            endpoint=self._projects_endpoints.get_projects_stats,
            response_model=UnifiedResponse[ProjectsStats],
            methods=[METHOD.GET],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/projects-with-users",
            endpoint=self._projects_endpoints.get_user_projects,
            response_model=UnifiedResponse[list[ProjectWithUsers]],
            methods=[METHOD.GET],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/stats-micro",
            endpoint=self._projects_endpoints.get_project_stats,
            response_model=UnifiedResponse[ProjectStats],
            methods=[METHOD.GET],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/scores",
            endpoint=self._projects_endpoints.get_scores,
            response_model=UnifiedResponse[ProjectScores],
            methods=[METHOD.GET],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/scores-apartment",
            endpoint=self._projects_endpoints.get_score_map_for_apartment,
            response_model=UnifiedResponse[Optional[ScoreMapItemWithLabels]],
            methods=[METHOD.GET],
            dependencies=[Depends(Auth(main_db_manager))],
        )

        self.router.add_api_route(
            path="/scores-apartment",
            endpoint=self._projects_endpoints.update_score_map_for_apartment_mock,
            response_model=UnifiedResponse[ScoreMapItemWithLabels],
            methods=[METHOD.POST],
            dependencies=[Depends(Auth(main_db_manager))],
        )
