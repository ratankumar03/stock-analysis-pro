from django.contrib import admin

# Register your models here.
# Since we're using MongoDB, we don't have Django models to register
# But we can create custom admin views if needed

admin.site.site_header = "Stock Analysis Admin"
admin.site.site_title = "Stock Analysis Admin Portal"
admin.site.index_title = "Welcome to Stock Analysis Administration"