from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

MODEL_NAME = "MBZUAI/LaMini-T5-738M"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

def generar_descripcion(nombre_materia: str) -> str:
    prompt = (
        f"Genera una descripción académica breve, clara y formal en español sobre la asignatura universitaria "
        f"'{nombre_materia}'. Explica los temas principales y los objetivos de aprendizaje."
    )

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=256)
    outputs = model.generate(
        **inputs,
        max_length=128,
        num_beams=5,
        early_stopping=True
    )

    descripcion = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return descripcion.strip().capitalize()