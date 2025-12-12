import PyPDF2
import io
from django.core.files.uploadedfile import InMemoryUploadedFile

def extraer_texto_de_archivo(archivo: InMemoryUploadedFile) -> str:
    """Extrae texto de un archivo PDF subido en Django."""
    
    # Es crucial que el archivo se lea solo una vez y en modo binario
    try:
        archivo_bytes = archivo.read()
    except Exception as e:
        return f"Error al leer archivo binario: {e}"
    
    
    if archivo.content_type == 'application/pdf':
        try:
            lector = PyPDF2.PdfReader(io.BytesIO(archivo_bytes))
            texto_completo = ""
            
            for pagina in lector.pages:
                # 🚨 CORRECCIÓN CLAVE: 🚨
                # 1. Extraer el texto de la página.
                # 2. Concatenarlo a texto_completo, añadiendo un salto de línea (espacio) para separar páginas.
                texto_completo += pagina.extract_text() + "\n"
                
            # Opcional: limpiar la cadena final de espacios extra
            return texto_completo.strip()
            
        except Exception as e:
            # Capturar errores específicos de PyPDF2 (ej. PDF encriptado)
            return f"Error al procesar PDF (PyPDF2): {e}"
    
    else:
        return "Tipo de archivo no soportado (solo PDF por ahora)."