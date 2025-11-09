# microservices/questions-ms/adapters/lambda_question_creator_adapter.py
import json
from typing import (
    Any,
    Dict,
)
from http import HTTPStatus
from datetime import datetime
from hexagonal_polls.misc.adapters import AbstractQuestionCreatorIOFrameworkAdapter
from hexagonal_polls.dtos import QuestionDTO


class LambdaQuestionCreatorAdapter(AbstractQuestionCreatorIOFrameworkAdapter):
    """
    Adaptador de Entrada/Salida concreto para el Framework AWS Lambda/API Gateway.

    Hereda de AbstractQuestionCreatorIOFrameworkAdapter e implementa los métodos 
    abstractos 'input' y 'output' para mapear datos crudos a DTOs y viceversa.
    """
    def input(self, input_data: Dict[str, Any]) -> QuestionDTO:
        """
        Método de Entrada (Input): Mapea la petición cruda de Lambda/HTTP (el 'event') 
        a un DTO de Dominio (QuestionDTO) para el Core.
        """
        try:
            # Lambda/API Gateway coloca el payload JSON como string en 'body'
            body = json.loads(input_data.get('body', '{}'))
        except json.JSONDecodeError:
            body = {} 

        question_text = body.get('question_text')
        # Creamos un QuestionDTO, aunque solo se usen algunos campos
        return QuestionDTO(
            id=None, # ID nulo en la creación
            question_text=question_text,
            pub_date=datetime.utcnow() # Simulación de la fecha para pasar la validación simple
        )

    def output(self, question: QuestionDTO) -> Dict[str, Any]:
        """
        Método de Salida (Output): Mapea el DTO de salida del Core a un objeto de respuesta HTTP.
        """
        # Mapeo a un diccionario de respuesta estándar (Adapter de Salida del Framework)
        response_data = {
            'id': question.id,
            'question_text': question.question_text,
            # Aseguramos la serialización correcta de datetime
            'pub_date': question.pub_date.isoformat() if question.pub_date else None
        }
        # Estructura de respuesta de AWS Lambda/API Gateway
        return {
            'statusCode': HTTPStatus.CREATED.value,
            'body': json.dumps(response_data),
            'headers': {'Content-Type': 'application/json'}
        }
        
    def map_error_to_framework_response(self, error: Exception) -> Dict[str, Any]:
        """
        Método auxiliar para mapear errores, complementando el flujo de 'execute'.
        """
        status = HTTPStatus.INTERNAL_SERVER_ERROR.value
        error_message = "Ocurrió un error inesperado en el servicio."

        # Mapeo de errores conocidos (incluyendo ValueError y el error de tu Core)
        if isinstance(error, (ValueError, Exception)):
            status = HTTPStatus.BAD_REQUEST.value
            error_message = str(error)

        return {
            'statusCode': status,
            'body': json.dumps({'error': error_message}),
            'headers': {'Content-Type': 'application/json'}
        }
