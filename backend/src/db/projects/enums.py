import enum


class VideoStatusOption(str, enum.Enum):
    created = "created"  # Video is created
    extracted = "extracted"  # Video has gone through extraction
    approved = "approved"  # Video is approved by admin
    declined = "declined"  # Video is declined by admin


class ApartmentDecorationTypeOption(str, enum.Enum):
    rough = "rough"
    finishing = "finishing"


class RoleTypeOption(str, enum.Enum):
    author = "author"
    view_only = "view_only"
    verificator = "verificator"


class ProjectStatusOption(str, enum.Enum):
    created = "created"  # When project is created by admin
    # in_extraction = "in_extraction"
    # extracted = "extracted"
    # approved = "approved"
    in_progress = "in_progress"  # When verificator started to work at the project
    finished = "finished"  # When the project is totally finished


class ApartmentStatusOption(str, enum.Enum):
    created = "created"  # When apartment doesn't have video yet
    in_progress = (
        "in_progress"  # When apartment has a video, but it's extraction is not approved
    )
    # finished = "finished"  # When apartment's video is approved
    approved = "approved"
    declined = "declined"