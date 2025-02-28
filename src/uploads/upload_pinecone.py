from pinecone import Pinecone
import os

# Configurar a API do Pinecone
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENV = "us-east-1"  # Exemplo: "us-west1-gcp-free"

# Inicializar o Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)

# Nome do índice
index_name = "notion-docs"

def get_embeddings(text):
  result = pc.inference.embed(
    "multilingual-e5-large",
    inputs=text,
    parameters={
      "input_type": "passage"
    }
  )

  return result.data[0]['values']

def upload_pinecone(texts):
  # Conectar ao índice
  index = pc.Index(index_name)

  # Inserindo dados sem precisar gerar embeddings manualmente
  vectors = []
  for i, text in enumerate(texts):
    embedding = get_embeddings(text);
    vector = (str(i), embedding, {"text": text})
    vectors.append(vector)

  # Inserir no Pinecone
  index.upsert(vectors)

  print("Dados enviados com sucesso!")
