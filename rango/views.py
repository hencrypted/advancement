from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime

def new(request):
	context_dict = {}
	return render(request, 'rango/base_bootstrap.html', context=context_dict)

def index(request):
	#request.session.set_test_cookie()
	category_list = Category.objects.order_by('-likes')[:5]
	page_list = Page.objects.order_by('-views')[:5]
	context_dict = {'categories':category_list, 'pages': page_list }
	# Get the type of request , GET or POST
	#print(request.method)
	# Print out the name of the User logged in,if None, it'll return Anonymous User
	#print(request.user)

	# Obtain our Response object early so we can add cookie information	

	# Call function to handle the cookies
	return render(request, 'rango/index.html', context = context_dict)

def about(request):
	#if request.session.test_cookie_worked():
		#print("TEST COOKIE WORKED")
		#request.session.delete_test_cookie()
	context_dict = {'text1': 'Moses Benjamin', 
					'text2': 'I uploaded this image: '
				}
	visitor_cookie_handler(request) 
	context_dict['visits'] = request.session['visits']
	context_dict['last_visit'] = request.session['last_visit']
	response = render(request, 'rango/about.html', context = context_dict)
	return response


def show_category(request, category_name_slug):
	context_dict = {}

	try:
		# Can we find a category name slug with the given name?
		#If we can't, the .get() method raises a DoesNotExist exception
		# So the .get() method returns one model instance or raises an exception
		category = Category.objects.get(slug = category_name_slug)

		# Retrieve all of the associated pages
		# Note that filter() returns a list of page objects or an empty list
		pages = Page.objects.filter(category = category)

		# Adds our results list to the template context under name pages
		context_dict['pages'] = pages
		# We also add the category object from the 
		#database to the context dictionary
		# We'll use this in the template to verify that the category exist
		context_dict['category'] = category
	except Category.DoesNotExist:
		# We get here iF we didnt find the specified category
		# Don't do anything
		# the template eill display the "no category" message for us.
		context_dict['pages'] = None
		context_dict['category'] = None

	# Go render the response and return it to the client
	return render(request, 'rango/category.html', context_dict)

@login_required
def add_category(request):
	form = CategoryForm()

	# A HTTP POST?
	if request.method == 'POST':
		form = CategoryForm(request.POST)

		# Have we been provided with a valid form?
		if form.is_valid():
		# Save the new category to the database
			form.save(commit=True)
			# Now that the category is saved
			# We could give a confirmatory message
			# But since the most recent category added is on the index page_list
			# Then we can direct the user back to the index page
			return index(request)
			# The sipplied form contained errors
			# just print them to the terminal
		print(form.errors)

	# Will handle the bad form, new form, or no form supplied cases
	# Render the form with error messages(if any).
	return render(request, 'rango/add_category.html', {'form': form}) 

@login_required
def add_page(request, category_name_slug):
	try:
		category = Category.objects.get(slug=category_name_slug)
	except Category.DoesNotExist:
		category = None

	form = PageForm()
	if request.method == 'POST':
		form = PageForm(request.POST)
		if form.is_valid():
			if category:
				page = form.save(commit=False)
				page.category = category
				page.views = 0
				page.save()
			return show_category(request, category_name_slug)
		else:
			print(form.errors)

	return render(request, 'rango/add_page.html', {'form': form, 'category': category})


def likeCategory(request, category_name_slug):
	category = get_object_or_404(Category, slug=category_name_slug)
	try:
		selected_category = Category.objects.get(slug=request.POST['category'])
	except (KeyError, Category.DoesNotExist):
		return render(request, 'rango/category.html', 
			{'category': category, 'error_message': 'Check the checkbox !'})

	else:
		selected_category.likes += 1
		selected_category.save()
	#return HttpResponseRedirect(reverse('rango:index', args=('')))
	return show_category(request, category_name_slug)

def register(request):
	# A boolean value for telling the template
	# whether the registration was successful.
	# Set to False initially. Code changes value to
	# True when the registration succeeds.	
	registered = False

	# If it's a HTTP POST, we're interested in processing form data
	if request.method == 'POST':
		# Attempt to grab informaton from the raw form information
		# Note that we make use of both UserForm And UserProfileForm.
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)

		# If the two fields are valid...
		if user_form.is_valid() and profile_form.is_valid():
			# Save the User's form data to the database
			user = user_form.save()

			# Now we hash the password with the set_password method
			# Once hashed, we can update the user object
			user.set_password(user.password)
			user.save()

			# Now sort out the UserProfile instance
			#Since we need to set the user attribute ourselves,
			# set commit=False. This delays saving the model
			# until we're ready to avoid integrity problems.
			profile = profile_form.save(commit=False)
			profile.user = user

			# Did the user provide a profile picture ?
			# If so, we need to get it from the input form and
			# put it in the UserProfile model
			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']

			# Now save the UserProfile model instance.
			profile.save()

			# Update our variable to indicate that thet the template
			# registration was successful.
			registered = True

		else:
				# Invalid form or forms - mistakes or something else?
				# Print problems to the terminal
				 print(user_form.errors, profile_form.errors)
	else:
		# Not a HTTP POST, so we render our form using two modelForm instances.
		# These forms will be blank, ready for user input.
		user_form = UserForm()
		profile_form = UserProfileForm()

	# Render the template depending on the context.
	return render(request,
		'rango/register.html',
		{'user_form': user_form,
		'profile_form': profile_form,
		'registered': registered,})
			 	
def user_login(request):
	if request.method == "POST":
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(username=username, password=password)

		if user:
			if user.is_active:
				login(request, user)
				return HttpResponseRedirect(reverse('rango:index'))
			else:
				return render(request, 'rango/login.html',{'error_message':
					'Your account has been disabled.'})
		else:

			return render(request, 'rango/login.html',
				{'error_message': 'Username and Password Mismatch !'})
	else:
		return render(request, 'rango/login.html',{})

@login_required
def restricted(request):
	return render(request,'rango/restricted.html',
		{'text': "Since you're logged in, you can see this text!"})

def user_logout(request):
	logout(request)
	return HttpResponseRedirect(reverse('rango:index'))

def get_server_side_cookie(request, cookie, default_value=None):
	val = request.session.get(cookie)
	if not val:
		val = default_value
	return val

def visitor_cookie_handler(request):
	# Get the number of visits to the site
	# We use the COOKIES.get() function to obtain the visits cookie.
	# If the cookie exists, the value returned is casted to an integer.
	# If the cookie doesn't exist, then the default value of 1 is used.
	visits = int(get_server_side_cookie(request,'visits', '1'))
	last_visit_cookie = get_server_side_cookie(request,
		'last_visit', str(datetime.now())) 
	last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

	# If it's been more than a day since the last visit...
	if (datetime.now() - last_visit_time).seconds > 0:
		visits  =visits + 1
		#update the last visit cookie now that we have updated the count
		request.session['last_visit'] = str(datetime.now())

	else:
		visits =1
		# set the last visit cookie
		request.session['last_visit'] = last_visit_cookie

	# Update/set the visits cookie
	request.session['visits'] = visits	