from typing import List
from zope.interface import implements

# Importaciones desde el paquete hexagonal-polls
from hexagonal_polls.dtos import QuestionDTO 
from hexagonal_polls.interfaces import IQuestionRepository, IGetRecentQuestionsExecutor

@implements(IGetRecentQuestionsExecutor)
class GetRecentQuestionsService:
    def __init__(self):
        """
        Recibe el Adaptador de Infraestructura (DynamoDBQuestionReader) 
        a través de su interfaz (IQuestionRepository).
        """
        self.repository = IQuestionRepository(self)

    # 3. La Lógica (Orquestación Pura)
    def execute(self) -> List[QuestionDTO]:
        """
        Ejecuta la lógica del caso de uso (pedir datos y devolverlos).
        No hay lógica de negocio compleja, es un simple fetch.
        """
        # Llama al método del Repositorio inyectado.
        questions = self.repository.get_recent(limit=5)
        
        # Opcional: Podríamos filtrar o transformar aquí, pero para este CU es directo.
        return questions