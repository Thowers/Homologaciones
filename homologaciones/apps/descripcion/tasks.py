from transformers import pipeline, AutoModel, AutoTokenizer
import numpy as np
from materias.models import Materia
from comparacion.utils import comparar_materia

def generar_descripcion_y_embedding(materia_id):
    materia = Materia.objects.get(id=materia_id)

    # 1️⃣ Generar descripción con FLAN-T5
    generator = pipeline("text2text-generation", model="google/flan-t5-base")
    prompt = f"Describe brevemente la materia universitaria '{materia.nombre}' en español."
    descripcion = generator(prompt, max_length=100)[0]['generated_text']

    # 2️⃣ Generar embedding con MiniLM
    model_name = "sentence-transformers/all-MiniLM-L12-v2"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)

    inputs = tokenizer(descripcion, return_tensors='pt', truncation=True)
    outputs = model(**inputs)
    embedding = outputs.last_hidden_state.mean(dim=1).detach().numpy().tolist()[0]

    # 3️⃣ Guardar resultados
    materia.descripcion = descripcion
    materia.embedding = embedding
    materia.procesada = True
    materia.save()

    # 4️⃣ Comparar con otras materias existentes
    comparar_materia(materia)