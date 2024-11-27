"""  This module is used to import all the views from the views package. """

from .project_views import ProjectList, ProjectDetail
from .survey_views import SurveyList, SurveyDetail, FilledSurveys
from .risknote_views import RiskNoteCreate, RiskNoteDetail
from .user_views import UserList, UserDetail
from .auth_views import SignIn
from .azure_views import (
    RetrieveImage,
    RetrieveParams,
    TranscribeAudio,
    TranslateText,
    UploadImages,
)
from .utils_views import api_root

__all__ = [
    "ProjectList",
    "ProjectDetail",
    "SurveyList",
    "SurveyDetail",
    "RiskNoteCreate",
    "RiskNoteDetail",
    "UserList",
    "UserDetail",
    "SignIn",
    "TranscribeAudio",
    "TranslateText",
    "UploadImages",
    "RetrieveImage",
    "RetrieveParams",
    "FilledSurveys",
    "api_root",
]
