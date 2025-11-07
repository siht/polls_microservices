# Configuraciones de Infraestructura para LocalStack (Entorno de Desarrollo)
# Usaremos variables de entorno simples que serán leídas por el orquestador (Docker Compose / Ensamble)

# Variable que apunta a LocalStack
DYNAMODB_ENDPOINT_URL = "http://localhost.localstack.cloud:4566" 
# Nombre de la tabla (puede ser igual en LocalStack y Prod)
QUESTION_TABLE_NAME = "PollsQuestionsTable"
# Región estándar
AWS_REGION = "us-east-1"