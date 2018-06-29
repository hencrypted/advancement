import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
			'tango_with_django.settings')
import django
django.setup()

from rango.models import Category, Page

def populate():
	python_pages = [
	{'title': 'hacking secret ciphers with python',
	 'url': 'invypy.com',
	 'views': '18'
	},
	{'title': 'invent your own computer games with python',
	 'url': 'invypy.com', 
	 'views': '45'},
	 {'title': 'Automating tasks using python',
	  'url': 'invypy.com',
	  'views': '23'}]

	django_pages = [
	{'title': 'tango_with_django',
	 'url': 'tango_with_django.com', 
	 'views': '88'},
	 {'title': 'django documentation',
	 'url':'django.org', 
	 'views': '76'},]
	
	cats = {'Python': {'page': python_pages},
			'Django': {'page': django_pages}}

	for cat, cat_data in cats.items():
		c = add_cat(cat)
		for p in cat_data['page']:
			add_page(c, p['title'], p['url'], p['views'])

	for c in Category.objects.all():
		for p in Page.objects.filter(category= c):
			print('%s - %s' % (c,p))

def add_cat(name, views=0, likes=0):
	c = Category.objects.get_or_create(name=name)[0]
	if name == 'Python':
		c.views = 128
		c.likes = 64
	elif name == 'Django':
		c.views = 64
		c.likes= 32
	c.save()
	return c

def add_page(cat, title, url, views=0):
	p = Page.objects.get_or_create(category=cat, title=title)[0]
	p.url = url
	p.views= views
	p.save()
	return p


if __name__ == '__main__':
	populate()