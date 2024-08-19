from django.apps import AppConfig
import sys


class DocumentBusinessServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'documentBusinessService'

    def ready(self):
        """
        This method is used to perform startup tasks when the Django application
        is ready. For example, it can be used to initialize components that are
        necessary for the application's operation.
        """

        """
        This check prevents certain startup tasks from being executed,
        if the management command executed is any other than 'runserver'
        command.
        """

        if not ("runserver" in sys.argv or "core.wsgi:application" in sys.argv):
            return
