import re
from datetime import date, datetime
from django.conf import settings
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, PasswordResetForm, UserCreationForm
from django.contrib.auth.models import User 
from django.contrib.contenttypes.models import ContentType
from django.core.context_processors import csrf
from django.core.mail import send_mail, EmailMessage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db.models import Count, Max, Q
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.utils import simplejson, timezone
from forms import *
from models import *
from django.core.exceptions import MultipleObjectsReturned

try:
	APPLICANT = ProfileStatus.objects.get(name__icontains='applicant')
except ProfileStatus.DoesNotExist:
	APPLICANT = ProfileStatus.objects.create(name='ApplMultipleObjectsReturnedicant')
except MultipleObjectsReturned:
	APPLICANT = ProfileStatus.objects.all()[0]
	print("ERROR: original developer intended for only one Profile Status to contain the word 'Applicant'")

donotreply = 'This email is from the UCLA Student Media application website. Do not respond directly to this email address.\nSend your reply to:'
subject_prefix = 'Apply: UCLA Student Media - '

status_colors = {
	Entry.INCOMPLETE:'',
	Entry.SUBMITTED:'badge-info',
	Entry.ACCEPTED:'badge-success',
	Entry.REJECTED:'badge-important',
	Entry.WAITLISTED:'badge-warning',
	Entry.DECLINED:'badge-inverse',
}

def get_contains(request,key):
	return request.GET.get(key,'') != ''
cssbase = [
	'css/theme_venera_white.css',
]
jsbase = [
	'js/bootstrap.js',
	'js/jquery-1.10.1.min.js',
	'js/lightbox.js',
	'js/main.js',
	'js/prettify.js',
]	

baselinks = [
	{'name':'home','text':'Home'},
	{'name':'applications','text':'Apply'},
]

endlinks = [
	{'name':'contact','text':'Contact'},
]

loglinks = [
	{'name':'profile','text':'Profile'},
	#{'name':'statement','text':'Personal Statement'},
]
managerlinks = [
	{'name':'managepeople','text':'People'},
]

def activeLink(context,name):
	context['active'] = name

def baseContext(request,name):
	links = []
	if request.user.is_authenticated():
		if request.user.is_staff:
			links+=managerlinks
		links+=loglinks
	links+=endlinks
	context = RequestContext(request,{
		'request':request,
		'csslist':cssbase,
		'jslist':jsbase,
		'navbar':links,
		'publications':Publication.objects.all(),
		'staff':request.user.is_authenticated() and request.user.is_staff,
	})
	activeLink(context,name)
	context.update(csrf(request))
	return context

def context_processor(request):
	return { 'publications' : Publication.objects.all() }

def home(request):
	context = baseContext(request,'home')
	context['title'] = 'Home'
	applications = Application.objects.filter(publish=True)
	open_applications = []
	pending_applications = []
	for app in applications:
		if app.is_open():
			open_applications += [app]
		elif app.is_pending():
			pending_applications += [app]
	p = 1
	pp_string = '5'
	try:
		p = int(request.GET['p'])
	except:
		p = 1
	news = News.objects.order_by('-date','publish')
	if not context['staff']:
		news = news.filter(publish=True,staff=False)
	elif 'staff' in request.GET and request.GET['staff'] == '1':
		news = news.filter(staff=True)
	if 'pp' in request.GET:
		pp_string = request.GET['pp']
	try:
		pp = int(request.GET['pp'])
	except:
		pp = news.count()
	if pp <= 0:
		pp = 1
	pages = Paginator(news,pp)
	context['p'] = p
	context['pp'] = pp_string
	context['pp_op'] = [5,10]
	context['page_count'] = pages.num_pages
	context['page_range'] = range(max(p-3,1),min(p+4,pages.num_pages+1))
	context['news'] = pages.page(p)
	context['open_applications'] = open_applications
	context['pending_applications'] = pending_applications
	return render(request,'home.html',context)

def contact(request):
	context = baseContext(request,'contact')
	context['title'] = 'Contact'
	contacts = Contact.objects.filter(show=True)
	context['contacts'] = contacts
	emails = ContactEmail.objects.all()
	infolist = {}
	for email in emails:
		infolist[str(email.id)] = str(email.description)
	context['infolist'] = infolist
	context['default'] = 'Please select a recipient.'
	if request.method == 'POST':
		try:
			context['selected_email'] = request.POST['recipient']
		except:
			pass
		contact_form = ContactForm(request.POST)
		if contact_form.is_valid():
			sender = contact_form.cleaned_data['sender']
			email = contact_form.cleaned_data['recipient']
			subject = contact_form.cleaned_data['subject']
			message = contact_form.cleaned_data['message']
			try:
				email = EmailMessage(u''.join([subject_prefix,subject.replace('%N',email.name)]),u'\n'.join([donotreply,sender,u'\n',message.replace('%N',email.name)]),sender,[email.email],[],headers={'Reply-To':sender,'From':'UCLA Student Media'})
				email.send()
				context['message'] = {
					'text':'Your email has been sent.',
					'class':'success'
				}
			except:
				context['message'] = {
					'text':'Your email could not be sent.',
					'class':'error'
				}
		else:
			context['message'] = {
				'text':'There were problems with the form.',
				'class':'error'
			}
	else:
		contact_form = ContactForm()
	context['contact_form'] = contact_form
	return render(request,'contact.html',context)

@csrf_protect
@login_required(login_url='login')
def profile(request):
	context = baseContext(request,'profile')
	context['help_texts'] = {}
	for help in ProfileHelpText.objects.all():
		context['help_texts'][help.field] = help.info
	context['title'] = 'Edit Profile'
	try:
		profile = Profile.objects.get(user=request.user)
	except:
		profile = Profile(user=request.user,state=APPLICANT)
		context['message'] = {
			'text':'Please complete your profile before submitting your application.',
			'class':'info'
		}
	try:
		status = Status.objects.filter(profile=profile).order_by('-start')[0]
		new_status = False
	except:
		status = Status(profile=profile,status=APPLICANT)
		new_status = True
	if request.method == 'POST':
		form = ProfileForm(request.POST,request.FILES,instance=profile)
		"""
		attachment = Attachment(user=profile.user)
		attachment_form = AttachmentForm(request.POST,request.FILES,instance=attachment)
		deletions = request.POST.getlist('delete',[])
		for id in deletions:
			try:
				att = Attachment.objects.get(user=profile.user,pk=id)
				if att.deletable():
					att.delete()
			except:
				pass
		if  attachment_form.is_valid():
			attachment_form.save()
		"""
		if form.is_valid():
			profile = form.save()
			if new_status:
				status.profile = profile
				status.save()
			request.user.first_name = profile.first
			request.user.last_name = profile.last
			request.user.email = profile.email
			request.user.save()
			context['message'] = {
				'text':'Your changes have been saved.',
				'class':'success'
			}
			if 'next' in request.GET:
				return HttpResponseRedirect(request.GET['next'])
		else:
			context['message'] = {
				'text':'There were errors with the form.',
				'class':'error'
			}
	else:
		form = ProfileForm(instance=profile)
	attachment_form = AttachmentForm()
	context['form'] = form
	context['attachments'] = Attachment.objects.filter(user=profile.user)
	context['attachment_form'] = attachment_form
	context['profile'] = profile
	return render(request,'profile.html',context)

def settings(request):
	context = baseContext(request,'settings')
	context['title'] = 'Settings'
	if 'next' in request.GET:
		return HttpResponseRedirect(request.GET['next'])
	return render(request,'settings.html',context)

def publications(request):
	context = baseContext(request,'applications')
	if request.method == 'POST' and context['staff']:
		for key in request.POST:
			if re.match('^\d+$',key):
				try:
					pub = Publication.objects.get(pk=key)
					pub.rank = request.POST[key]
					pub.save()
				except:
					pass
		for i,pub in enumerate(Publication.objects.all()):
			pub.rank=i+1
			pub.save()
	publications = Publication.objects.all()
	if not context['staff']:
		publications = publications.filter(active=True)
	pubs = [[],[],[]]
	for i, publication in enumerate(publications):
		pubs[i%3]+=[publication]
	context['exists'] = publications.exists()
	context['pubs'] = pubs
	return render(request,'publications.html',context)

def publication(request,slug):
	context = baseContext(request,'applications')
	publication = get_object_or_404(Publication,slug=slug)
	if request.method == 'POST' and context['staff']:
		for key in request.POST:
			if re.match('^\d+$',key):
				try:
					pos = Position.objects.get(pk=key)
					pos.rank = request.POST[key]
					pos.save()
				except:
					pass
		for i,pos in enumerate(Position.objects.filter(publication=publication)):
			pos.rank=i+1
			pos.save()
	if not context['staff'] and not publication.active:
		return HttpResponseRedirect(reverse('applications'))
	context['publication'] = publication
	context['title'] = str(publication)
	positions = publication.position_set.all()
	if not context['staff']:
		positions = positions.filter(active=True)
	poss = [[],[]]
	for i, position in enumerate(positions):
		poss[i%2]+=[position]
	context['poss'] = poss
	context['applications'] = Application.objects.filter(position__in=positions)
	return render(request,'publication.html',context)

@csrf_protect
def position(request,pub,pos):
	form = NewAppForm(request.GET)
	if form.is_valid():
		return HttpResponseRedirect(reverse('manageapp',kwargs=form.cleaned_data))
	if request.method == 'POST' and 'app' in request.POST:
		return HttpResponseRedirect(reverse('apply',kwargs={'id':request.POST['app']}));
	context = baseContext(request,'applications')
	position = get_object_or_404(Position,slug=pos,publication__slug=pub)
	if not context['staff'] and not (position.active and position.publication.active):
		return HttpResponseRedirect(reverse('publication',kwargs={'slug':pub}))
	applications = position.application_set.all().order_by('-year','-quarter','-close','-open')
	if not context['staff']:
		applications = applications.filter(publish=True)
	context['title'] = str(position)
	context['position'] = position
	context['applications'] = applications
	apps = [[],[]]
	for app in applications:
		if app.is_open() or app.is_pending() or app.is_on_hold():
			apps[0]+=[app]
		else:
			apps[1]+=[app]
	context['apps'] = apps
	context['QUARTERS'] = QUARTERS
	context['newapp'] = form
	return render(request,'position.html',context)

@csrf_protect
def apply(request,pub,pos,app):
	context = baseContext(request,'applications')
	application = get_object_or_404(Application,slug=app,position__slug=pos,position__publication__slug=pub)
	if not context['staff'] and not (application.publish and application.position.active and application.position.publication.active):
		return HttpResponseRedirect(reverse('position',kwargs={'pub':pub,'pos':pos}))
	if application.is_on_hold():
		context['message'] = {
			'text':'This application is a draft; contents are subject to change before it is published.',
			'class':'warning'
		}
	if request.user.is_authenticated():
		context['attachments'] = Attachment.objects.filter(user=request.user)
		try:
			entry = Entry.objects.get(applicant=request.user,application=application)
		except:
			entry = Entry(applicant=request.user,application=application,year=application.year,quarter=application.quarter)
			#if application.is_open():
			#	entry.save()
	else:
		entry = Entry(application=application)
	editable = request.user.is_authenticated() and application.is_open() and (entry.status == Entry.INCOMPLETE)
	if (request.method == 'POST') and editable:
		entry_data = {}
		for key in request.POST:
			if re.match(r'^\d+.\d+$',key):
				entry_data[key] = request.POST.getlist(key,[])
		for key in request.FILES:
			if re.match(r'^\d+.\d+$',key):
				sq = map(int,key.split('.'))
				application_data = application.decode()
				type = AttachmentType.objects.get(pk=int(application_data[sq[0]]['questions'][sq[1]]['type']))
				attachment = Attachment(user=entry.applicant,type=type,file=request.FILES[key])


				#print("\n\n>>>>>   ", request.FILES[key].name)
				# TODO: FIX THIS QUICKFIX
				try:
					attachment.save()
				except Exception, e:
					import logging
                                        logging.exception(e)
					return HttpResponse('Something went wrong with your attachment:<br /><br />%s\n<br /><br />Please push the back button in your web browser and reupload your attachment with a simplified filename by removing special characters and/or shortening it.  If the problem persists please email your application to <a href="mailto:online@media.ucla.edu">online@media.ucla.edu</a> describing this problem.' % request.FILES[key])

				entry_data[key] = [u''.join([u'a',unicode(attachment.id)])]
		entry.encode(entry_data)
		entry.save()
		context['message'] = {
			'text':'Your changes have been saved.',
			'class':'info'
		}
		if 'action' in request.POST and request.POST['action'] == 'sub':
			if entry.is_valid():
				try:
					entry.applicant.profile
					entry.submit = timezone.now()
					entry.status = Entry.SUBMITTED
					entry.save()
					editable = False
				except:
					context['message'] = {
						'text':'You must complete your profile before you submit an application.',
						'class':'warning'
					}
			else:
				context['message'] = {
					'text':'You must complete the entire application before submitting.',
					'class':'error'
				}
				context['indicate_invalid'] = True
	application_data = combine(application,entry)
	context['editable'] = editable
	context['entry'] = entry
	context['application'] = application
	context['app'] = application_data
	context['INCOMPLETE'] = Entry.INCOMPLETE
	context['status'] = entry.status_string() if entry.status == Entry.INCOMPLETE else choice_string(Entry.STATUSES,Entry.SUBMITTED)
	context['color'] = status_colors[entry.status if entry.status == Entry.INCOMPLETE else Entry.SUBMITTED]
	return render(request,'apply.html',context)

@sensitive_post_parameters()
@csrf_protect
@never_cache
def applyLogin(request):
	if request.user.is_authenticated():
		return HttpResponseRedirect(reverse('home'))
	context = baseContext(request,'account')
	context['title'] = 'Log in'
	if request.method == 'POST' and 'username' in request.POST and 'password' in request.POST:
		user = authenticate(username=request.POST['username'],password=request.POST['password'])
		if user is not None:
			if user.is_active:
				login(request,user)
				if 'next' in request.GET:
					return HttpResponseRedirect(request.GET['next'])
				else:
					try:
						request.user.profile
						return HttpResponseRedirect(reverse('home'))
					except:
						return HttpResponseRedirect(reverse('profile'))
			else:
				context['message'] = {
					'text':'Your account has been disabled.',
					'class':'error'
				}
		else:
			context['message'] = {
					'text':'Incorrect credentials.',
					'class':'error'
			}
	context['loginform']=AuthenticationForm()
	return render(request,'login.html',context)

@login_required(login_url='login')
def applyLogout(request):
	logout(request)
	return HttpResponseRedirect(reverse('login'))

@sensitive_post_parameters()
@csrf_protect
def applyRegister(request):
	if request.user.is_authenticated():
		return HttpResponseRedirect(reverse('home'))
	context = baseContext(request,'account')
	context['title'] = 'Register'
	if request.method == 'POST':
		form = UserCreationForm(request.POST)
		if form.is_valid():
			form.save()
			new_user = authenticate(username=request.POST['username'],password=request.POST['password1'])
			login(request,new_user)
			if 'next' in request.GET:
				return HttpResponseRedirect(reverse('profile')+'?next='+request.GET['next'])
			else:
				return HttpResponseRedirect(reverse('profile'))
	else:
		form = UserCreationForm()
	context['form'] = form
	return render(request,'register.html',context)

@staff_member_required
def managePeople(request):
	context = baseContext(request,'managepeople')
	context['title'] = 'People'
	p = 1
	pp_string = '100'
	people = Profile.objects.all()
	search_form = ProfileSearchForm(request.GET)
	statuses = request.GET.getlist('status',[])
	if statuses:
		people = people.filter(state__id__in=statuses)

	genders = request.GET.getlist('gender',[])
	if genders and genders[0] != '':
		for val in request.GET['gender'].split(' '):
			people = people.filter(gender__iexact=val)

	quarters = request.GET.getlist('quarter',[])
	if quarters:
		people = people.filter(quarter__in=quarters)
	if get_contains(request,'position'):
		for val in request.GET['position'].split(' '):
			people = people.filter(title__icontains=val)
	if get_contains(request,'name'):
		for val in request.GET['name'].split(' '):
			people = people.filter(Q(first__icontains=val)|Q(middle__icontains=val)|Q(last__icontains=val))
	if get_contains(request,'email'):
		for val in request.GET['email'].split(' '):
			people = people.filter(email__icontains=val)
	if get_contains(request,'num_mob'):
		people = people.filter(phone_mob__icontains=request.GET['num_mob'])
	if get_contains(request,'num_prm'):
		people = people.filter(phone_perm__icontains=request.GET['num_prm'])
	if get_contains(request,'addr_loc'):
		for val in request.GET['addr_loc'].split(' '):
			people = people.filter(Q(add1_local__icontains=val)|Q(add2_local__icontains=val)|Q(city_local__icontains=val)|Q(state_local__icontains=val)|Q(postal_local__icontains=val))
	if get_contains(request,'addr_prm'):
		for val in request.GET['addr_prm'].split(' '):
			people = people.filter(Q(add1_perm__icontains=val)|Q(add2_perm__icontains=val)|Q(city_perm__icontains=val)|Q(state_perm__icontains=val)|Q(postal_perm__icontains=val))
	if get_contains(request,'major'):
		for val in request.GET['major'].split(' '):
			people = people.filter(major__icontains=val)
	if get_contains(request,'year_low'):
		people = people.filter(year__gte=request.GET['year_low'])
	if get_contains(request,'year_high'):
		people = people.filter(year__lte=request.GET['year_high'])
	if get_contains(request,'high'):
		for val in request.GET['high'].split(' '):
			people = people.filter(Q(high__icontains=val)|Q(city_high__icontains=val))
	if get_contains(request,'p'):
		p = int(request.GET['p'])
	if get_contains(request,'pp'):
		pp_string = request.GET['pp']
	try:
		pp = int(pp_string)
	except:
		pp = people.count()
	if pp <= 0:
		pp = 1
	pages = Paginator(people,pp)
	context['profile_count'] = people.count()
	context['page_count'] = pages.num_pages
	context['page_range'] = range(max(p-3,1),min(p+4,pages.num_pages+1))
	context['people'] = pages.page(min(p,pages.num_pages))
	context['p'] = p
	context['pp'] = pp_string
	context['pp_op'] = [50,100,200]
	context['search_form'] = search_form
	return render(request,'manage/people.html',context)

@csrf_protect
@staff_member_required
def managePerson(request,id):
	context = baseContext(request,'managepeople')
	profile = get_object_or_404(Profile,pk=id)
	context['person'] = profile
	if request.method == 'POST':
		try:
			status = ProfileStatus(pk=int(request.POST['change']))
		except:
			context['message'] = {
				'text':'Something went wrong!',
				'class':'error'
			}
		try:
			new_title = request.POST['title']
		except:
			new_title = ''
		if status == APPLICANT:
			context['message'] = {
				'text':'You cannot turn someone back into an applicant.',
				'class':'error'
			}
		elif status != profile.state or new_title != profile.title:
			old_status = profile.state
			old_title = profile.title
			profile.title = new_title
			profile.state = status
			LogEntry.objects.log_action(
				user_id=request.user.id,
				content_type_id=ContentType.objects.get_for_model(Profile).pk,
				object_id=profile.id,
				object_repr=unicode(profile),
				change_message=' '.join(map(unicode,[old_status,old_title,'to',profile.state,new_title])),
				action_flag=CHANGE
			)
			profile.save()
			new_status = Status(profile=profile,status=status,title=new_title)
			LogEntry.objects.log_action(
				user_id=request.user.id,
				content_type_id=ContentType.objects.get_for_model(Status).pk,
				object_id=new_status.id,
				object_repr=unicode(status),
				action_flag=ADDITION
			)
			new_status.save()
			context['message'] = {
				'text':'Your changes have been saved.',
				'class':'success'
			}
		else:
			context['message'] = {
				'text':'The status is unchanged.',
				'class':'info'
			}
	statuses = Status.objects.filter(profile=profile).order_by('-start')
	context['entries'] = profile.user.entry_set.all()
	context['attachments'] = Attachment.objects.filter(user=profile.user)
	context['statuses'] = statuses
	context['types'] = ProfileStatus.objects.all()
	context['title'] = str(context['person'])
	return render(request,'manage/person.html',context)

@csrf_protect
@staff_member_required
def manageNews(request):
	if request.method == 'POST':
		try:
			id = int(request.POST['id'])
		except:
			id = -1
		try:
			news = News.objects.get(pk=id)
			new = False
		except:
			news = News()
			new = True
		if 'action' in request.POST:
			action = request.POST['action']
			if action == 'delete':
				LogEntry.objects.log_action(
					user_id=request.user.id,
					content_type_id=ContentType.objects.get_for_model(News).pk,
					object_id=news.id,
					object_repr=unicode(news),
					action_flag=DELETION
				)
				news.delete()
			elif action == 'toggle':
				try:
					news.publish = not news.publish
					LogEntry.objects.log_action(
						user_id=request.user.id,
						content_type_id=ContentType.objects.get_for_model(News).pk,
						object_id=news.id,
						object_repr=unicode(news),
						change_message=unicode('Published' if news.publish else 'Hid'),
						action_flag=CHANGE
					)
					news.save()
				except:
					pass
			elif action == 'staff-toggle':
				try:
					news.staff = not news.staff
					news.save()
					LogEntr.objects.log_ation(
						user_id=request.user.id,
						content_type_id=ContentType.objects.get_for_model(News).pk,
						object_id=news.id,
						object_repr=unicode(news),
						change_message=unicode('Turned staff' if news.staff else 'Turned General'),
						action_flag=CHANGE
					)
				except:
					pass
			elif action == 'refresh':
				news.date = timezone.now()
				LogEntry.objects.log_action(
					user_id=request.user.id,
					content_type_id=ContentType.objects.get_for_model(News).pk,
					object_id=news.id,
					object_repr=unicode(news),
					change_message=unicode('Refreshed'),
					action_flag=CHANGE
				)
				news.save()
		else:
			form = NewsForm(request.POST,instance=news)
			if form.is_valid():
				news = form.save()
				LogEntry.objects.log_action(
					user_id=request.user.id,
					content_type_id=ContentType.objects.get_for_model(News).pk,
					object_id=news.id,
					object_repr=unicode(news),
					action_flag=ADDITION if new else CHANGE
				)
	try:
		return HttpResponseRedirect(request.GET['next'])
	except:
		return HttpResponseRedirect(reverse('home'))

@csrf_protect
@staff_member_required
def managePublication(request):
	if request.method == 'POST':
		try:
			id = int(request.POST['id'])
		except:
			id = -1
		try:
			publication = Publication.objects.get(pk=id)
			new = False
		except:
			new_rank = Publication.objects.all().aggregate(Max('rank'))['rank__max']
			if new_rank:
				new_rank+=1
			else:
				new_rank=1
			publication = Publication(rank=new_rank)
			new = True
		if 'action' in request.POST:
			action = request.POST['action']
			if action == 'delete':
				if publication.deletable():
					LogEntry.objects.log_action(
						user_id=request.user.id,
						content_type_id=ContentType.objects.get_for_model(Publication).pk,
						object_id=publication.id,
						object_repr=unicode(publication),
						action_flag=DELETION
					)
					publication.delete()
			elif action == 'toggle':
				try:
					publication.active = not publication.active
					LogEntry.objects.log_action(
						user_id=request.user.id,
						content_type_id=ContentType.objects.get_for_model(Publication).pk,
						object_id=publication.id,
						object_repr=unicode(publication),
						change_message=unicode('Activated' if publication.active else 'Deactivated'),
						action_flag=CHANGE
					)
					publication.save()
				except:
					pass
		else:
			form = PublicationForm(request.POST,instance=publication)
			if form.is_valid():
				if not new:
					old_title = publication.title
				publication = form.save()
				if not new:
					publication.title = old_title
				else:
					publication.slug = slugify(publication.title)
				publication.save()
				LogEntry.objects.log_action(
					user_id=request.user.id,
					content_type_id=ContentType.objects.get_for_model(Publication).pk,
					object_id=publication.id,
					object_repr=unicode(publication),
					action_flag=ADDITION if new else CHANGE
				)
	try:
		return HttpResponseRedirect(request.GET['next'])
	except:
		return HttpResponseRedirect(reverse('publications'))

@csrf_protect
@staff_member_required
def managePosition(request):
	if request.method == 'POST':
		publication = get_object_or_404(Publication,pk=request.POST['publication'])
		try:
			id = int(request.POST['id'])
		except:
			id = -1
		try:
			position = Position.objects.get(pk=id)
			new = False
		except:
			new_rank = Position.objects.filter(publication=publication).aggregate(Max('rank'))['rank__max'];
			if new_rank:
				new_rank+=1
			else:
				new_rank=1
			position = Position(publication=publication,rank=new_rank)
			new = True
		if position.publication != publication:
			raise Http404
		if 'action' in request.POST:
			action = request.POST['action']
			if action == 'delete':
				if position.deletable():
					LogEntry.objects.log_action(
						user_id=request.user.id,
						content_type_id=ContentType.objects.get_for_model(Position).pk,
						object_id=position.id,
						object_repr=unicode(position),
						action_flag=DELETION
					)
					position.delete()
			elif action == 'toggle':
				try:
					position.active = not position.active
					LogEntry.objects.log_action(
						user_id=request.user.id,
						content_type_id=ContentType.objects.get_for_model(Position).pk,
						object_id=position.id,
						object_repr=unicode(position),
						change_message=unicode('Activated' if position.active else 'Deactivated'),
						action_flag=CHANGE
					)
					position.save()
				except:
					pass
		else:
			form = PositionForm(request.POST,instance=position)
			if form.is_valid():
				if not new:
					old_title = position.title
				position = form.save()
				if not new:
					position.title = old_title
				else:
					position.slug = slugify(position.title)
				position.save()
				LogEntry.objects.log_action(
					user_id=request.user.id,
					content_type_id=ContentType.objects.get_for_model(Position).pk,
					object_id=position.id,
					object_repr=unicode(position),
					action_flag=ADDITION if new else CHANGE
				)
	try:
		return HttpResponseRedirect(request.GET['next'])
	except:
		return HttpResponseRedirect(reverse('publications'))

@staff_member_required
def entriesJson(request):
	json = dict(enumerate(Entry.objects.values('id','status','application__quarter','application__year','application__position__title','application__position__publication__title','applicant__profile__first','applicant__profile__middle','applicant__profile__last','applicant__username','applicant__profile__email','submit')))
	return HttpResponse(simplejson.dumps(json,default=lambda obj: obj.strftime('%D, %I:%M:%S %p')),mimetype='application/json')

def get_entries(request):
    """Helper function that filters applicants based on url query string.
       For the manageEntries() view"""
    entries = Entry.objects.all()

    get_pub = request.GET.getlist('pub',[])
    if get_pub:
        entries = entries.filter(application__position__publication__slug__in=get_pub)
    get_pos = request.GET.getlist('pos',[])
    if get_pos:
        entries = entries.filter(application__position__slug__in=get_pos)
    get_e_quarter = request.GET.getlist('e_quarter',[])
    if get_e_quarter:
        entries = entries.filter(quarter__in=get_e_quarter)
    get_e_year = request.GET.getlist('e_year',[])
    if get_e_year:
        entries = entries.filter(year__in=get_e_year)
    entry_statuses = request.GET.getlist('entry_status',[])
    if entry_statuses:
        entries = entries.filter(status__in=entry_statuses)
    statuses = request.GET.getlist('status',[])
    if statuses:
        entries = entries.filter(applicant__profile__state__id__in=statuses)
    genders = request.GET.getlist('gender',[])
    if genders and genders[0] != '':
        for val in request.GET['gender'].split(' '):
            entries = entries.filter(applicant__profile__gender__iexact=val)
    quarters = request.GET.getlist('quarter',[])
    if quarters:
        entries = entries.filter(applicant__profile__quarter__in=quarters)
    if get_contains(request,'name'):
        for val in request.GET['name'].split(' '):
            entries = entries.filter(Q(applicant__profile__first__icontains=val)|Q(applicant__profile__middle__icontains=val)|Q(applicant__profile__last__icontains=val))
    if get_contains(request,'email'):
        for val in request.GET['email'].split(' '):
            entries = entries.filter(applicant__profile__email__icontains=val)
    if get_contains(request,'num_mob'):
        entries = entries.filter(applicant__profile__phone_mob__icontains=request.GET['num_mob'])
    if get_contains(request,'num_prm'):
        entries = entries.filter(applicant__profile__phone_perm__icontains=request.GET['num_prm'])
    if get_contains(request,'addr_loc'):
        for val in request.GET['addr_loc'].split(' '):
            entries = entries.filter(Q(applicant__profile__add1_local__icontains=val)|Q(applicant__profile__add2_local__icontains=val)|Q(applicant__profile__city_local__icontains=val)|Q(applicant__profile__state_local__icontains=val)|Q(applicant__profile__postal_local__icontains=val))
    if get_contains(request,'addr_prm'):
        for val in request.GET['addr_prm'].split(' '):
            entries = entries.filter(Q(applicant__profile__add1_perm__icontains=val)|Q(applicant__profile__add2_perm__icontains=val)|Q(applicant__profile__city_perm__icontains=val)|Q(applicant__profile__state_perm__icontains=val)|Q(applicant__profile__postal_perm__icontains=val))
    if get_contains(request,'major'):
        for val in request.GET['major'].split(' '):
            entries = entries.filter(applicant__profile__major__icontains=val)
    if get_contains(request,'year_low'):
        entries = entries.filter(applicant__profile__year__gte=request.GET['year_low'])
    if get_contains(request,'year_high'):
        entries = entries.filter(applicant__profile__year__lte=request.GET['year_high'])
    if get_contains(request,'high'):
        for val in request.GET['high'].split(' '):
            entries = entries.filter(Q(applicant__profile__high__icontains=val)|Q(applicant__profile__city_high__icontains=val))
    userlist = list(set([e['applicant__id'] for e in entries.values('applicant__id')]))
    users = User.objects.filter(pk__in=userlist)
    ufilter = request.GET.getlist('ufilter',[])
    if ufilter:
        dup_users = users.annotate(Count('entry')).filter(entry__count__gt=1)
        if 'u' in ufilter:
            entries = entries.exclude(applicant__in=dup_users)
        if 'd' in ufilter:
            entries = entries.filter(applicant__in=dup_users)
    return entries

@csrf_protect
@staff_member_required
def manageEntries(request):
    # TODO: at the url /manage/entries the 'Entries' count currently includes applications submitted by
    # applicants without a profile but the list below does not show the applications.
    #  Should note that somewhere or give option to view those applications
    # TODO: does a search query using GET querystring which creates server errors if user hand types
    #  in url.  Should create safety-checking/escaping/exception-catching
	context = baseContext(request,'managepeople')
	search_form = EntrySearchForm(request.GET)
	p = 1
	pp_string = '50'
	poss = {}
	for position in Position.objects.all():
		if position.slug in poss:
			poss[str(position.slug)]['pubs'] += [str(position.publication.slug)]
		else:
			poss[str(position.slug)] = {'text':str(position.title),'pubs':[str(position.publication.slug)]}
	e_quarters = {}
	#for entry in Entry.objects.all():
	#	if entry.quarter in e_quarters:
	#		e_quarters[entry.quarter_string]['poss'] += 
	apps = {}
	for application in Application.objects.all():
		if application.slug in apps:
			apps[str(application.slug)]['poss'] += [str(application.position.slug)]
		else:
			apps[str(application.slug)] = {'text':str(application),'poss':[str(application.position.slug)]}
	pubs = {}

	entries = get_entries(request)

	if get_contains(request,'p'):
		p = int(request.GET['p'])
	if get_contains(request,'pp'):
		pp_string = request.GET['pp']
	try:
		pp = int(pp_string)
	except:
		pp = entries.count()
	if pp <= 0:
		pp = 1
	context['emails'] = ','.join(list(set([entry.applicant.profile.email for entry in entries.filter(applicant__profile__isnull=False)])))
	if request.method == 'POST':
		email_form = EmailForm(request.POST)
		if email_form.is_valid():
			sender = email_form.cleaned_data['sender']
			recipients = email_form.cleaned_data['recipients'].split(',')
			subject = email_form.cleaned_data['subject']
			message = email_form.cleaned_data['message']
			for recipient in recipients:
				try:
					profile = Profile.objects.get(email__exact=recipient)
					first = profile.first
					name = unicode(profile)
				except:
					first = recipient.split('@')[0]
					name = recipient
				try:
					email = EmailMessage(subject.replace('%N',name).replace('%n',first),u'\n'.join([donotreply,sender,u'\n',message.replace('%N',name).replace('%n',first)]),sender,[recipient],[],headers={'Reply-To':sender,'From':'UCLA Student Media'})
					email.send()
					context['message'] = {
						'text':'Your email has been sent.',
						'class':'success'
					}
				except:
					context['message'] = {
						'text':'There was a problem with the email form.',
						'class':'error'
					}
		else:
			context['message'] = {
				'text':'Your email was not sent.',
				'class':'error'
			}
	pages = Paginator(entries,pp)
	context['entry_count'] = entries.count()
	context['unique_count'] = len(set([e['applicant__id'] for e in entries.values('applicant__id')]))
	context['p'] = p
	context['pp'] = pp_string
	context['pp_op'] = [50,100,200]
	context['page_count'] = pages.num_pages
	context['page_range'] = range(max(p-3,1),min(p+4,pages.num_pages+1))
	context['search_form'] = search_form
	try:
		context['entries'] = pages.page(p)
	except PageNotAnInteger:
		context['entries'] = pages.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		context['entries'] = pages.page(pages.num_pages)

	context['search_form'] = search_form
	context['poss'] = poss
	context['apps'] = apps
	context['QUARTERS'] = dict(QUARTERS)
	context['STATUSES'] = dict(Entry.STATUSES)
	return render(request,'manage/entries.html',context)

@csrf_protect
@staff_member_required
def manageEntry(request,id):
	entry = get_object_or_404(Entry,pk=id)
	application = entry.application
	context = baseContext(request,'applications')
	context['ACCEPTED'] = Entry.ACCEPTED
	context['REJECTED'] = Entry.REJECTED
	context['WAITLISTED'] = Entry.WAITLISTED
	context['DECLINED'] = Entry.DECLINED
	context['SUBMITTED'] = Entry.SUBMITTED
	context['INCOMPLETE'] = Entry.INCOMPLETE
	context['STATUSES'] = Entry.STATUSES
	if request.method == 'POST':
		if 'status' in request.POST and request.POST['status'] in all_choices(Entry.STATUSES):
			new_status = request.POST['status']
			if (Entry.ACCEPTED and Entry.REJECTED) != entry.status != new_status != (Entry.SUBMITTED and Entry.INCOMPLETE and Entry.DECLINED):
				LogEntry.objects.log_action(
					user_id=request.user.id,
					content_type_id=ContentType.objects.get_for_model(Entry).pk,
					object_id=entry.id,
					object_repr=unicode(entry),
					change_message=' '.join(map(unicode,['from',entry.status_string(),'to',choice_string(Entry.STATUSES,new_status)])),
					action_flag=CHANGE
				)
				entry.status = new_status
				entry.save()
		elif 'notes' in request.POST:
			entry_form = EntryForm(request.POST,instance=entry)
			if entry_form.is_valid():
				entry_form.save()
				context['message'] = {
					'text':'Your notes have been saved.',
					'class':'success',
				}
			else:
				context['message'] = {
					'text':'These notes could not be saved.',
					'class':'error',
				}
	try:
		profile = entry.applicant.profile
		context['profile'] = profile
	except:
		pass

	application_data = combine(application,entry)
	context['entry'] = entry
	context['application'] = application_data
	context['notice'] = entry.application.notice
	return render(request,'manage/entry.html',context)

@csrf_protect
@staff_member_required
def manageApplication(request,pos,quarter,year):
	position = get_object_or_404(Position,pk=pos)
	context = baseContext(request,'applications')
	context['twelve'] = range(1,13)
	context['years'] = range(date.today().year,date.today().year+5)
	context['sixty'] = range(1,61)
	context['thirtyone'] = range(1,32)
	try:
		application = Application.objects.get(position=position,quarter=quarter,year=year)
	except:
		application = Application(position=position,quarter=quarter,year=year)
		application.slug = slugify(u' '.join([application.quarter_string(),unicode(application.year)]))
	editable = application.deletable()
	if request.method == 'POST':
		form = ApplicationForm(request.POST,instance=application)
		attachment_form = AppAttachmentFormSet(request.POST,request.FILES,instance=application)
		app = []
		for key in request.POST:
			if re.match(r'^\d+(.\d+)*$',key):
				indexes = map(int,key.split('.'))
				length = len(indexes)
				if length > 0:
					if len(app) <= indexes[0]:
						for i in range(indexes[0]+1-len(app)):
							app.extend([{'title':u'','text':u'','questions':[]}])
					section = app[indexes[0]]
					if length == 1:
						section['title'] = request.POST[key]
				if length > 1:
					if len(section['questions']) <= indexes[1]:
						for i in range(indexes[1]+1-len(section['questions'])):
							section['questions'].extend([{'text':u'','help':u'','type':u'','answer':[]}])
					question = section['questions'][indexes[1]]
					if length == 2:
						question['text'] = request.POST[key]
				if length > 2:
					if len(question['answer']) <= indexes[2]:
						for i in range(indexes[2]+1-len(question['answer'])):
							question['answer'].extend([{'text':u''}])
					choice = question['answer'][indexes[2]]
					if length == 3:
						choice['text'] = request.POST[key]
			elif re.match(r'^\d+.text$',key):
				index = map(int,key.split('.')[:1])[0]
				if len(app) <= index:
					for i in range(index+1-len(app)):
						app.extend([{'title':u'','text':u'','questions':[]}])
				section = app[index]
				section['text'] = request.POST[key]
			elif re.match(r'^\d+.\d+.type$',key):
				indexes = map(int,key.split('.')[:2])
				if len(app) <= indexes[0]:
					for i in range(indexes[0]+1-len(app)):
						app.extend([{'title':u'','text':u'','questions':[]}])
				section = app[indexes[0]]
				if len(section['questions']) <= indexes[1]:
					for i in range(indexes[1]+1-len(section['questions'])):
						section['questions'].extend([{'text':u'','help':u'','type':u'','answer':[]}])
				question = section['questions'][indexes[1]]
				question['type'] = request.POST[key]
			elif re.match(r'^\d+.\d+.help$',key):
				indexes = map(int,key.split('.')[:2])
				if len(app) <= indexes[0]:
					for i in range(indexes[0]+1-len(app)):
						app.extend([{'title':u'','text':u'','questions':[]}])
				section = app[indexes[0]]
				if len(section['questions']) <= indexes[1]:
					for i in range(indexes[1]+1-len(section['questions'])):
						section['questions'].extend([{'text':u'','help':u'','type':u'','answer':[]}])
				question = section['questions'][indexes[1]]
				question['help'] = request.POST[key]
		if editable:
			application_data = app
		else:
			application_data = application.decode()
		if form.is_valid() and attachment_form.is_valid():
			application = form.save()
			application.slug = slugify(u' '.join([application.quarter_string(),unicode(application.year)]))
			application.save()
			attachment_form.save()
			attachment_form = AppAttachmentFormSet(instance=application)
			application.encode(application_data)
			application.save()
			LogEntry.objects.log_action(
				user_id=request.user.id,
				content_type_id=ContentType.objects.get_for_model(Application).pk,
				object_id=application.id,
				object_repr=unicode(application),
				change_message=application.data,
				action_flag=CHANGE
			)
			context['message'] = {
				'text':'The application has been saved.',
				'class':'success'
			}
		else:
			context['message'] = {
				'text':'The application could not be saved.',
				'class':'error'
			}
	else:
		form = ApplicationForm(instance=application)
		attachment_form = AppAttachmentFormSet(instance=application)
		application_data = application.decode()
	counts = []
	for section in application_data:
		s = []
		for question in section['questions']:
			q = 0
			for choice in question['answer']:
				q+=1
			s.extend([q])
		counts.extend([s])
	editable = application.deletable()
	context['counts'] = counts
	context['quarter_string'] = application.quarter_string
	context['year'] = application.year
	context['position'] = position
	context['application'] = application
	context['app'] = application_data
	context['editable'] = editable
	context['form'] = form
	context['attachment_form'] = attachment_form
	context['attachmenttypes'] = AttachmentType.objects.all()
	return render(request, 'manage/application.html',context)

@csrf_protect
@staff_member_required
def manageDeleteApp(request):
	if request.method == 'POST':
		try:
			application = Application.objects.get(pk=request.POST['id'])
			if application.deletable():
				application.delete()
				LogEntry.objects.log_action(
					user_id=request.user.id,
					content_type_id=ContentType.objects.get_for_model(Application).pk,
					object_id=application.id,
					object_repr=unicode(application),
					change_message=application.data,
					action_flag=DELETION
				)
		except:
			pass
	if 'next' in request.GET:
		return HttpResponseRedirect(request.GET['next'])
	else:
		return HttpResponseRedirect(reverse('home'))
