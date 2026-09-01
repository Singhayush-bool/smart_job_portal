from django.apps import AppConfig
from django.contrib import admin


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        # Admin branding customization
        admin.site.site_header = "Smartjob Administration"
        admin.site.site_title = "Smartjob Admin Portal"
        admin.site.index_title = "Welcome to Smartjob Site Administration"

        # Signals import (Ye aapkaignal load karega)
        import accounts.signals
