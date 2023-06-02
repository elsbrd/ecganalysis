from celery import shared_task
from celery.utils.log import get_task_logger

from modelling.models import TrainingSession
from modelling.training.manager import TrainingManager


logger = get_task_logger(__name__)

@shared_task
def q_train_model(training_session_id, general_params, algorithm_params):
    session = TrainingSession.objects.filter(id=training_session_id).first()
    if not session:
        logger.warning(f'Training session with id {training_session_id} does not exist. Existing task...')
        return

    manager = TrainingManager(session, general_params, algorithm_params)
    manager.run()
