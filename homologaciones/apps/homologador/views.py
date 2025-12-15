import re
import json
import traceback # Importado para manejo robusto de errores
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.conf import settings
from .forms import NotasUploadForm
from .models import AsignaturaDestino, Carrera, HistoricoHomologacion
from .utils import extraer_texto_de_archivo, generar_docx_homologacion

from google import genai
from google.genai.errors import APIError

# --- ESQUEMA DE SALIDA DE EXTRACCIÓN (FASE 1) ---
SCHEMA_MATERIAS_ORIGEN = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "nombre_origen": {"type": "string", "description": "Nombre completo de la materia de origen."},
            "nota_final": {"type": "string", "description": "Calificación numérica o equivalente de la materia."},
            "creditos_origen": {"type": "integer", "description": "Número de créditos de la materia de origen."},
            "codigo_origen": {"type": "string", "description": "Código de la materia de origen, si está disponible, sino N/A."}
        },
        "required": ["nombre_origen", "nota_final", "creditos_origen"]
    }
}

# --- FUNCIONES AUXILIARES ---

def extraer_materias_origen(texto_notas: str):
    """
    FASE 1: Usa Gemini para convertir el texto plano de las notas del estudiante
    en un objeto JSON estructurado y limpio.
    """
    
    prompt_extraccion = f"""
    Eres un experto en el procesamiento de documentos académicos. Tu tarea es la extracción EXTREMADAMENTE agresiva de datos. Tu única tarea es identificar y extraer TODAS las materias cursadas del siguiente texto bruto, convirtiéndolas estrictamente al formato JSON proporcionado.
    
    Instrucciones Clave para la Extracción:
    1. **IGNORA EL RUIDO:** Ignora líneas de cabecera, pie de página, totales, información personal o textos que no sean una materia.
    2. **BUSCA PATRONES:** Las materias válidas suelen ir seguidas por una nota y un número de créditos.
    3. **TOLERANCIA AL ERROR:** Si la nota o los créditos no son claros, usa "N/A" para el campo y luego continúa. NO debes devolver una lista vacía si hay datos de materias presentes.
    
    --- TEXTO A PROCESAR (Historial Académico) ---
    {texto_notas}
    --- FIN DEL TEXTO ---
    """
    
    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt_extraccion,
            config={
                "response_mime_type": "application/json",
                "response_schema": SCHEMA_MATERIAS_ORIGEN 
            }
        )
        
        # Devuelve la lista JSON de materias de origen
        return json.loads(response.text)
        
    except APIError as e:
        # Devuelve el error como un diccionario serializable
        return {"error": f"Error de la API de Gemini (Fase 1 - Extracción): {str(e)}"} 
    except (json.JSONDecodeError, ValueError) as e:
        # Error si la IA no devuelve JSON limpio
        return {"error": f"La IA devolvió un JSON inválido en Fase 1: {str(e)}"}
    except Exception as e:
        # Captura cualquier otro error
        return {"error": f"Error inesperado en Fase 1: {str(e)}"}


def generar_prompt_homologacion(materias_origen_json: str, plan_estudios_json: str):
    """
    FASE 2: Construye el prompt estructurado para la homologación, 
    utilizando la lista JSON limpia de materias de origen.
    """
    
    # 1. Reglas de Homologación Detalladas (CRÉDITOS MODIFICADOS)
    reglas = """
    REGLAS DE HOMOLOGACIÓN A APLICAR ESTRICTAMENTE:
    1. **ITERACIÓN TOTAL:** Por cada materia en el 'PLAN DE ESTUDIOS DE DESTINO', se debe buscar la materia de origen más adecuada. El JSON de salida DEBE incluir una entrada para CADA materia de destino.
    2. **CRITERIO SEMÁNTICO (PRIORIDAD):** Ignora mayúsculas, minúsculas, tildes y caracteres especiales. La coincidencia temática se ASUME suficiente si los nombres de origen y destino cubren la misma ÁREA FUNDAMENTAL (ej. Cálculo, Programación, Bases de Datos, Inglés).
    3. **CRÉDITOS (Condición Modificada):** Para que la homologación proceda, los 'creditos_origen' de la materia extraída del PDF deben ser **MAYORES O IGUALES** a los 'creditos' de la materia de destino. Si esta condición no se cumple, el estado es 'NO APLICA'. Al homologar, el valor de 'creditos_otorgados' DEBE ser el mismo que los 'creditos' de la materia de destino.
    4. **NOTA MÍNIMA:** Se requiere una calificación de 70/100 o su equivalente. Si la nota de origen no está en escala de 100, la IA debe hacer la CONVERSIÓN (ej. 3.5/5.0 -> 70/100) para verificar si supera el 70%. Si la nota es insuficiente, el estado es 'NO APLICA'.
    5. **ESTADO FINAL:** El estado debe ser 'HOMOLOGADA' solo si se cumplen las reglas 2, 3 y 4. En cualquier otro caso, el estado es 'NO APLICA'.
    """
    
    instruccion = (
        "Eres un analista experto en homologación de créditos. Tu única tarea es la comparación lógica. "
        "Utiliza la lista 'MATERIAS DE ORIGEN (JSON LIMPIO)' y coteja CADA elemento del 'PLAN DE ESTUDIOS DE DESTINO' aplicando las 'REGLAS DE HOMOLOGACIÓN'. "
        "Tu respuesta DEBE ser ÚNICAMENTE un arreglo JSON que contenga los objetos de homologación y siga el esquema de salida. "
    )

    esquema_ejemplo_json = [
        {
            "materia_destino": "Nombre de la materia de destino",
            "codigo_destino": "Código de la materia de destino",
            "materia_origen_homologada": "Nombre de la materia de origen que aplica, o 'N/A' si no aplica.",
            "creditos_otorgados": 0,
            "razon_homologacion": "Justificación concisa (ej. 'Homologada: Cumple nota, coincide área de Cálculo, y créditos de origen (5) son mayores a destino (4)', o 'No aplica: Nota insuficiente').",
            "estado": "HOMOLOGADA" 
        }
    ]
    
    prompt_final = f"""
    {instruccion}

    ### PLAN DE ESTUDIOS DE DESTINO (CARRERA A INGRESAR) ###
    {plan_estudios_json}

    ### MATERIAS DE ORIGEN (JSON LIMPIO) ###
    {materias_origen_json}
    
    ### REGLAS DE HOMOLOGACIÓN ###
    {reglas}
    
    ### ESQUEMA DE SALIDA JSON ###
    {json.dumps(esquema_ejemplo_json, indent=2)}
    """
    
    return prompt_final


# --- VISTA DE DJANGO (PROCESAMIENTO DE DOS FASES) ---

def procesar_homologacion_view(request):
    if request.method == 'POST':
        form = NotasUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # 1. Preparación de datos y extracción de texto
                archivo_notas = request.FILES['notas_file']
                carrera_destino_id = form.cleaned_data['carrera_destino'].id
                texto_de_notas_estudiante = extraer_texto_de_archivo(archivo_notas)
                
                print("-" * 50)
                print("TEXTO BRUTO DEL PDF RECIBIDO POR GEMINI:")
                print(texto_de_notas_estudiante)
                print("-" * 50)
                
                if "Error" in texto_de_notas_estudiante:
                     return JsonResponse({'status': 'error', 'message': texto_de_notas_estudiante}, status=400)
                
                # 🚨 FASE 1: EXTRACCIÓN DE DATOS DE ORIGEN 🚨
                materias_origen_result = extraer_materias_origen(texto_de_notas_estudiante)
                
                # Chequeo si la Fase 1 devolvió un error (diccionario con clave "error")
                if isinstance(materias_origen_result, dict) and "error" in materias_origen_result:
                    error_message = materias_origen_result["error"]
                    print("-" * 50)
                    print("🚨 ERROR EN FASE 1 (EXTRACCIÓN) 🚨")
                    print(error_message)
                    print(traceback.format_exc())
                    print("-" * 50)
                    
                    return JsonResponse({
                        'status': 'error', 
                        'message': f"Error en la extracción de notas (Fase 1). Detalle: {error_message}"
                    }, status=500)

                # Continuamos si la lista es válida y no es un diccionario de error
                materias_origen_list = materias_origen_result
                materias_origen_json = json.dumps(materias_origen_list)
                
                # 2. Preparar el Plan de Estudios (Destino)
                asignaturas = AsignaturaDestino.objects.filter(carrera_id=carrera_destino_id)
                plan_estudios_list = list(asignaturas.values('nombre', 'codigo', 'creditos', 'contenido_tematico'))
                plan_estudios_json = json.dumps(plan_estudios_list)

                # 🚨 FASE 2: HOMOLOGACIÓN 🚨
                prompt = generar_prompt_homologacion(materias_origen_json, plan_estudios_json) 
                client = genai.Client(api_key=settings.GEMINI_API_KEY)

                # Definición del esquema de salida para la Homologación (DEBE COINCIDIR CON EL PROMPT)
                schema_homologacion = {
                    # ... (Esquema de salida) ...
                }

                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config={"response_mime_type": "application/json", "response_schema": schema_homologacion}
                )
                
                # 4. Parsear la respuesta
                homologaciones_json = json.loads(response.text)
                
                # ------------------------------------------------------------------
                # 🚨 INSERCIÓN: GUARDAR EN HISTÓRICO Y OBTENER ID 🚨
                # ------------------------------------------------------------------
                
                # Serializar el JSON de resultado
                resultado_str = json.dumps(homologaciones_json) 
                
                # Crear la entrada en el histórico
                historico_guardado = HistoricoHomologacion.objects.create(
                    carrera_destino_id=carrera_destino_id,
                    # Nota: Si el nombre del estudiante se extrae en Fase 1, se debe usar aquí.
                    nombre_estudiante=None, 
                    documento_identidad=None, 
                    resultado_json=resultado_str,
                    archivo_pdf_nombre=archivo_notas.name
                )
                
                # ------------------------------------------------------------------
                
                # 5. Retorno Exitoso (Incluyendo el ID del histórico)
                return JsonResponse({
                    'status': 'success', 
                    'message': 'Homologación procesada con éxito y guardada en el histórico.',
                    'resultado': homologaciones_json,
                    'historico_id': historico_guardado.id  # <-- DEVOLVEMOS EL ID
                })

            except Exception as e:
                # 🚨 CAPTURA FINAL DE ERRORES INESPERADOS 🚨
                print("-" * 50)
                print("🚨 ERROR FATAL INESPERADO 🚨")
                print(traceback.format_exc())
                print("-" * 50)
                
                return JsonResponse({
                    'status': 'error', 
                    'message': f"Un error inesperado ocurrió en la fase final de homologación. Detalle: {str(e)}"
                }, status=500)
        else:
            return JsonResponse({'status': 'error', 'message': dict(form.errors.items())}, status=400)
    
    # Si es una solicitud GET, renderiza el formulario
    form = NotasUploadForm()
    carreras = Carrera.objects.all()
    return render(request, 'homologador/upload.html', {'form': form, 'carreras': carreras})
        
        
    
    # Si es una solicitud GET, renderiza el formulario
    form = NotasUploadForm()
    carreras = Carrera.objects.all()
    return render(request, 'homologador/upload.html', {'form': form, 'carreras': carreras})

def descargar_docx_homologacion(request, historico_id):
    """
    Busca un histórico por ID y devuelve el resultado como un archivo DOCX.
    """
    historico_obj = get_object_or_404(HistoricoHomologacion, pk=historico_id)
    
    try:
        # Llama a la función utilitaria para generar el archivo en memoria
        docx_file = generar_docx_homologacion(historico_obj)
        
        # Construye el nombre del archivo
        filename = f"Homologacion_{historico_obj.carrera_destino.nombre.replace(' ', '_')}_{historico_obj.fecha_procesamiento.strftime('%Y%m%d')}.docx"
        
        # Configura la respuesta HTTP para la descarga
        response = HttpResponse(
            docx_file, 
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error al generar el DOCX: {str(e)}'}, status=500)