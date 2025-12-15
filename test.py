from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import re

MODEL_NAME = "mrm8488/mt5-small-finetuned-spanish-summarization"

print("🔹 Cargando modelo, esto puede tardar unos segundos...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

# Forzar CPU
device = torch.device("cpu")
model.to(device)
print(f"🚀 Dispositivo activo: {device}")

def limpiar_texto(texto: str) -> str:
    # Limpieza básica del texto
    texto = re.sub(r"\s+", " ", texto)
    texto = texto.strip().capitalize()
    return texto

def generar_descripcion(nombre_materia: str) -> str:
    prompt = (
        f"Redacta una descripción académica formal y clara en español sobre la asignatura universitaria '{nombre_materia}'. "
        "Incluye los temas principales de estudio y los objetivos de aprendizaje."
    )

    # Tokenizar entrada
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=128).to(device)

    # Generar descripción
    outputs = model.generate(
        **inputs,
        max_length=150,
        num_beams=5,
        do_sample=True,
        top_p=0.95,
        top_k=50,
        early_stopping=True
    )

    descripcion = tokenizer.decode(outputs[0], skip_special_tokens=True)
    descripcion = limpiar_texto(descripcion)

    # En caso de texto muy corto, usar fallback
    if len(descripcion.split()) < 10:
        descripcion = (
            f"La asignatura {nombre_materia} estudia los fundamentos teóricos y prácticos del área, "
            "abarcando conceptos esenciales y aplicaciones formales."
        )

    return descripcion

if __name__ == "__main__":
    materia = input("📘 Ingresa el nombre de la materia: ")
    descripcion = generar_descripcion(materia)
    print("\n🧠 Descripción generada:\n")
    print(descripcion)
