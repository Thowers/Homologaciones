from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Materia
from apps.descripcion.utils import generar_descripcion

@receiver(post_save, sender=Materia)
def generar_descripcion_automatica(sender, instance, created, **kwargs):
    if created and not instance.descripcion:
        try:
            descripcion = generar_descripcion(instance.nombre)
            instance.descripcion = descripcion
            instance.save()
        except Exception as e:
            print(f"Error generando descripción: {e}")