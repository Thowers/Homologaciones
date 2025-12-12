from django.apps import AppConfig

class HomologadorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    
    # Esto define la ruta de Python a la aplicación:
    name = 'apps.homologador' 
    
    # 🚨 CORRECCIÓN CLAVE: El label de la aplicación en minúsculas.
    # Debe coincidir con la URL que Django usa para el admin: admin/homologador/...
    label = 'homologador' 
    
    verbose_name = 'Sistema de Homologación'