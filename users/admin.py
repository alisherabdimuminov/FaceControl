from django.contrib import admin


from .models import History


@admin.register(History)
class HistoryModelAdmin(admin.ModelAdmin):
    list_display = ["user", "model", "comment", "created"]
