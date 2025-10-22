# microservices/questions-ms/adapters/dynamo_question_repository.py

import boto3
from typing import List, Union, Optional
from zope.interface import implementer
from datetime import datetime
import uuid

# --- IMPORTACIONES DEL CORE DOMAIN ---
# (Asume que QuestionDTO, IQuestionRepository y EntityNotFound están en 'hexagonal_polls')
from hexagonal_polls.dtos import QuestionDTO 
from hexagonal_polls.interfaces import IQuestionRepository

from global_config.config import (
    DYNAMODB_ENDPOINT_URL, 
    QUESTION_TABLE_NAME, 
    AWS_REGION
)


@implementer(IQuestionRepository)
class DynamoDBQuestionRepository:
    """
    Adaptador de salida que implementa el Puerto IQuestionRepository 
    para manejar operaciones de Preguntas con DynamoDB.
    """
    def __init__(self):
        """
        Inicializa la conexión, requiriendo los parámetros de infraestructura.
        """
        endpoint_url = DYNAMODB_ENDPOINT_URL
        table_name = QUESTION_TABLE_NAME
        region_name = AWS_REGION


        self.table_name = table_name
        self.dynamo_client = boto3.resource(
            'dynamodb',
            endpoint_url=endpoint_url if endpoint_url else None,
            region_name=region_name 
        )
        self.table = self.dynamo_client.Table(self.table_name)
    
    # --- 1. COMANDO: CREAR UNA PREGUNTA ---
    
    def create(self, question_text: str) -> QuestionDTO:
        """
        Crea una nueva pregunta, generando un ID y la fecha de publicación.
        """
        question_id = str(uuid.uuid4())
        pub_date = datetime.utcnow().isoformat()
        
        item = {
            # Usamos un PK genérico y un SK para el diseño de tabla única
            'pk': f"QUESTION#{question_id}",
            'sk': f"INFO#{question_id}", 
            'question_id': question_id, # ID limpio para consultas internas
            'question_text': question_text,
            'pub_date': pub_date,
            'entity_type': 'QUESTION',
        }
        
        self.table.put_item(Item=item)
        
        # Mapeo: Convertir de DynamoDB a nuestro DTO
        return QuestionDTO(
            id=question_id, 
            question_text=item.get('question_text', 'N/A'),
            pub_date=datetime.fromisoformat(pub_date)
        )

    # --- 2. CONSULTA: OBTENER DETALLE POR ID ---

    def get_by_id(self, question_id: str) -> Optional[QuestionDTO]:
        """
        Obtiene el detalle de una pregunta por su ID.
        """
        key = {
            'pk': f"QUESTION#{question_id}",
            'sk': f"INFO#{question_id}"
        }
        
        response = self.table.get_item(Key=key)
        item = response.get('Item')
        
        if not item:
            # Puedes levantar EntityNotFound aquí si el contrato del puerto lo permite
            return None
        
        # Mapeo a DTO
        return QuestionDTO(
            id=item.get('question_id'),
            question_text=item.get('question_text', 'N/A'),
            pub_date=datetime.fromisoformat(item.get('pub_date'))
        )

    # --- 3. CONSULTA: LISTAR RECIENTES ---

    def get_recent(self, limit: int = 5) -> List[QuestionDTO]:
        """
        Lista las 5 preguntas más recientes en orden descendente.
        
        ⚠️ Nota: Implementación funcional pero ineficiente (Scan). La versión óptima
        requiere un GSI para evitar el SCAN completo. Dejamos el SCAN por simplicidad
        mientras configuramos el GSI en la infraestructura.
        """

        # Versión Ineficiente (SCAN):
        response = self.table.scan()
        items = response.get('Items', [])
        
        # Ordenar en memoria (costoso para tablas grandes)
        items.sort(key=lambda x: x.get('pub_date', ''), reverse=True)
        recent_items = items[:limit]
        
        # Mapeo a DTOs
        questions_dto: List[QuestionDTO] = [
            QuestionDTO(
                id=item.get('question_id'), 
                question_text=item.get('question_text', 'N/A'),
                pub_date=datetime.fromisoformat(item.get('pub_date')) if item.get('pub_date') else None
            )
            for item in recent_items
        ]
        
        return questions_dto

    # ----------------------------------------------------
    # MÉTODOS NO UTILIZADOS (Demostración de la Violación de ISP)
    # ----------------------------------------------------

    # Dejamos estos métodos levantando el error, como querías, para demostrar el costo
    # de tener una interfaz (IQuestionRepository) que es demasiado grande (violando ISP).

    def get_all(self) -> List[QuestionDTO]:
        """No usamos scan sin límite. Levantamos error para forzar el uso de get_recent."""
        raise NotImplementedError("Operación get_all no implementada: No se permiten scans sin límite.")

    def update(self, entity: QuestionDTO) -> Union[QuestionDTO, None]:
        """Operación de escritura (update) no implementada."""
        raise NotImplementedError("Operación de escritura (update) no permitida.")

    def delete(self, entity_id: str) -> None:
        """Operación de eliminación (delete) no implementada."""
        raise NotImplementedError("Operación de eliminación (delete) no permitida.")
