# microservices/questions-ms/handler.py
import json
from http import HTTPStatus

from .adapters.lambda_question_creator_adapter import LambdaQuestionCreatorAdapter


def setup_component_architecture(): # "dependency injector" setup
    """Realiza todos los registros de adaptadores y utilidades necesarios."""
    from twisted.python import components
    from hexagonal_polls.interfaces import (
        IQuestionRepository,
        ICreateChoiceExecutor,
        ICreateQuestionExecutor,
    )
    from hexagonal_polls.misc.helper_interfaces import IQuestionCreatorIOFrameworkAdapter
    from hexagonal_polls.use_cases import CreateQuestion

    from .adapters.dynamo_question_repository import DynamoDBQuestionRepository

    components.registerAdapter(DynamoDBQuestionRepository, ICreateChoiceExecutor, IQuestionRepository)
    components.registerAdapter(CreateQuestion, IQuestionCreatorIOFrameworkAdapter, ICreateQuestionExecutor)

setup_component_architecture()


def create_question_handler(event: dict, context: dict):
    """
    Función de entrada de AWS Lambda (API Gateway).
    Delega toda la orquestación y el manejo de errores al Adaptador de I/O.
    """
    try:
        lambda_adapter = LambdaQuestionCreatorAdapter()
    except:
        return {
            'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR.value,
            'body': json.dumps({'error': 'Servicio no inicializado.'})
        }
    try:
        return lambda_adapter.execute(event)
    except Exception as e:
        return lambda_adapter.map_error_to_framework_response(e)
