import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from materias.models import Materia
from .models import Homologacion

def comparar_materia(materia):
    todas = Materia.objects.exclude(id=materia.id).filter(procesada=True)

    if not todas.exists():
        return

    base_embeddings = np.array([m.embedding for m in todas])
    vector = np.array([materia.embedding])
    similitudes = cosine_similarity(vector, base_embeddings)[0]

    for idx, valor in enumerate(similitudes):
        if valor > 0.80:  # umbral de similitud
            Homologacion.objects.create(
                materia_origen=materia,
                materia_destino=todas[idx],
                similitud=round(float(valor), 4)
            )