from services.training_service import TrainingService
from services.inference_service import InferenceService
from services.task_service import TaskService
from services.preprocessing_service import PreprocessingService

_training_service = None
_inference_service = None
_task_service = None
_preprocessing_service = None


def get_training_service() -> TrainingService:
    global _training_service
    if _training_service is None:
        _training_service = TrainingService()
    return _training_service


def get_inference_service() -> InferenceService:
    global _inference_service
    if _inference_service is None:
        _inference_service = InferenceService()
    return _inference_service


def get_task_service() -> TaskService:
    global _task_service
    if _task_service is None:
        _task_service = TaskService(
            training_service=get_training_service(),
            inference_service=get_inference_service()
        )
    return _task_service


def get_preprocessing_service() -> PreprocessingService:
    global _preprocessing_service
    if _preprocessing_service is None:
        _preprocessing_service = PreprocessingService()
    return _preprocessing_service
