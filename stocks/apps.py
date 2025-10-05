from django.apps import AppConfig

class StocksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stocks'
    
    def ready(self):
        # Import signals or perform startup tasks
        pass