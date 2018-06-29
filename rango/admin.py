from django.contrib import admin

from rango.models import Category, Page
from rango.models import UserProfile

class PageInline(admin.TabularInline): #admin.StackedInline
	model = Page
	#extra =10

class CategoryAdmin(admin.ModelAdmin):
	fieldsets = [ ('Name of Category', {'fields': ['name']}),
			('Number of views', {'fields': ['views']}), 
			('Number of likes' , {'fields': ['likes']}), 
			('Slug' , {'fields': ['slug']}), 
			]
	inlines = [PageInline]
	list_display = ('name', 'likes', 'views', 'slug')
	prepopulated_fields = {'slug': ('name',)}
class PageAdmin(admin.ModelAdmin):
	fields = ['category','views','url', 'title']
	list_display = ('title', 'category', 'url', 'views')
	list_filter = ['title']
	search_fields = ['title']
admin.site.register(Category, CategoryAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(UserProfile)