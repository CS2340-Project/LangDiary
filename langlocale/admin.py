from django.contrib import admin

# Register your models here.
from .models import Favorite

class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'place', 'get_place_id', 'get_place_mapsUrl')
    list_filter = ('user', 'place')
    search_fields = ('user__username', 'place__placeName', 'place__placeId')

    fieldsets = (
        (None, {
            'fields': ('user', 'place')
        }),
    )


    def get_place_id(self, obj):
        return obj.place.id
    def get_place_mapsUrl(self, obj):
        return obj.place.placeId
    get_place_id.short_description = 'Place ID'
    get_place_mapsUrl.short_description = 'Place PlaceId field (URL technically)'
admin.site.register(Favorite, FavoriteAdmin)
