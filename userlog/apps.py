from django.apps import AppConfig


class UserlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'userlog'
    
    def ready(self):
        import userlog.signals
