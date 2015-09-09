import ast
import datetime
import os.path
import re
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from django.utils import timezone

FALL = '0'
WINTER = '1'
SPRING = '2'
SUMMER = '3'
QUARTERS = (
	(FALL, 'Fall'),
	(WINTER, 'Winter'),
	(SPRING, 'Spring'),
	(SUMMER, 'Summer')
)

def choice_string(choices, choice):
	for pair in choices:
		if pair[0] == choice:
			return pair[1]

def all_choices(choices):
	return [c[0] for c in choices]

class Contact(models.Model):
	class Meta:
		verbose_name='Contact Info Piece'
		verbose_name_plural='Contact Info Pieces'
		ordering = ['number','title']
	icon = models.CharField(max_length=32)
	title = models.CharField(max_length=32,unique=True)
	info = models.TextField()
	number = models.PositiveSmallIntegerField()
	show = models.BooleanField()
	def __unicode__(self):
		return u':'.join([self.title,self.info])

class ContactEmail(models.Model):
	class Meta:
		ordering = ['department']
	name = models.CharField(max_length=128)
	department = models.CharField(max_length=128)
	description = models.TextField(blank=True)
	email = models.EmailField()
	def __unicode__(self):
		return u': '.join([self.department,self.email])

class News(models.Model):
	class Meta:
		verbose_name_plural='News'
		ordering = ['date']
	title = models.CharField(max_length=128)
	content = models.TextField()
	date = models.DateTimeField(auto_now_add=True,editable=False,blank=True)
	publish = models.BooleanField(default=False)
	staff = models.BooleanField(default=False)
	def __unicode__(self):
		return self.title

class ProfileStatus(models.Model):
	class Meta:
		verbose_name_plural='Profile Statuses'
		ordering = ['name']
	name = models.CharField(max_length=50,verbose_name='Title',unique=True)
	def __unicode__(self):
		return self.name

class ProfileHelpText(models.Model):
	field = models.CharField(max_length=64)
	info = models.TextField()
	def __unicode__(self):
		return u': '.join([self.field,self.info])

def set_picture_filename(instance,filename):
	path='user_pictures/'
	name = u'-'.join([unicode(instance.user.id),filename])
	return os.path.join(path,name)

class Profile(models.Model):
	class Meta:
		ordering = ['last','first','middle']
	user = models.OneToOneField(User)
	state = models.ForeignKey(ProfileStatus)
	title = models.CharField(max_length=128,verbose_name='Position',blank=True,null=True)
	first = models.CharField(max_length=16,verbose_name='First Name')
	middle = models.CharField(max_length=16,verbose_name='Middle Name',blank=True,null=True)
	last = models.CharField(max_length=16,verbose_name='Last Name')
	email = models.EmailField(unique=True,verbose_name='Email Address')
	gender = models.CharField(max_length=30, verbose_name='Gender')
	sid = models.CharField(unique=True,max_length=9,verbose_name='Student ID')
	birth = models.DateField(verbose_name='Date of Birth')
	race = models.CharField(max_length=32,blank=True,null=True)
	phone_perm = models.CharField(max_length=16,verbose_name='Permanent Phone Number',blank=True,null=True)
	phone_mob = models.CharField(max_length=16,verbose_name='Mobile Phone Number')
	website = models.CharField(max_length=64,verbose_name='Website/Blog',blank=True,null=True)
	add1_local = models.CharField(max_length=128,verbose_name='Local Address Line 1')
	add2_local = models.CharField(max_length=128,verbose_name='Local Address Line 2',blank=True,null=True)
	city_local = models.CharField(max_length=16,verbose_name='Local City')
	state_local = models.CharField(max_length=16,verbose_name='Local State or Province')
	postal_local = models.CharField(max_length=8,verbose_name='Local Postal Code')
	add1_perm = models.CharField(max_length=128,verbose_name='Permanent Address Line 1')
	add2_perm = models.CharField(max_length=128,verbose_name='Permanent Address Line 2',blank=True,null=True)
	city_perm = models.CharField(max_length=16,verbose_name='Permanent City')
	state_perm = models.CharField(max_length=16,verbose_name='Permanent State or Province')
	postal_perm = models.CharField(max_length=8,verbose_name='Permanent Postal Code')
	major = models.CharField(max_length=32)
	quarter = models.CharField(max_length=1,choices=QUARTERS,default=SPRING,verbose_name='Expected Grad Quarter')
	year = models.PositiveSmallIntegerField(verbose_name='Expected Grad Year')
	high = models.CharField(max_length=128,verbose_name='High School')
	city_high = models.CharField(max_length=128,verbose_name='High School City')
	picture = models.ImageField(upload_to=set_picture_filename,blank=True,null=True)
	def __unicode__(self):
		if self.middle:
			return ' '.join([self.first,self.middle,self.last])
		else:
			return ' '.join([self.first,self.last])
	def quarter_string(self):
		return choice_string(QUARTERS,self.quarter)
	def filename(self):
		if self.picture:
			try:
				name = os.path.basename(self.picture.name).split('-',1)[1]
			except:
				name = 'photo'
			if len(name) > 16:
				name = u''.join([name[:16],u'...'])
			return name
		return u''
	def website_url(self):
		if re.match('^https?://.*$',self.website):
			return self.website
		else:
			return u''.join(['http://',self.website])
	def save(self, *args, **kwargs):
		try:
			this = Profile.objects.get(id=self.id)
			if this.picture != self.picture:
				this.picture.delete(save=False)
		except:
			pass
		super(Profile,self).save(*args,**kwargs)

@receiver(pre_delete, sender=Profile)
def picture_delete(sender,instance,**kwargs):
	instance.picture.delete(False)

class Status(models.Model):
	class Meta:
		verbose_name_plural='Statuses'
		ordering = ['profile__last','profile__first','profile__middle','-start']
	profile = models.ForeignKey(Profile)
	start = models.DateTimeField(auto_now_add=True)
	status = models.ForeignKey(ProfileStatus)
	title = models.CharField(max_length=128,verbose_name='Position',blank=True,null=True)
	def __unicode__(self):
		return ' '.join([unicode(self.status),unicode(self.profile)])

class AttachmentType(models.Model):
	class Meta:
		ordering = ['name']
	name = models.CharField(max_length=32,verbose_name="Attachment Type")
	def __unicode__(self):
		return self.name

def set_attachment_filename(instance,filename):
	path='user_attachments'
	name=u'-'.join([unicode(instance.user.id),filename])
	return os.path.join(path,name)

class Attachment(models.Model):
	class Meta:
		ordering = ['type','file']
	user = models.ForeignKey(User)
	type = models.ForeignKey(AttachmentType)
	file = models.FileField(upload_to=set_attachment_filename)
	date = models.DateTimeField(auto_now_add=True)
	def filename(self):
		if self.file:
			try:
				name = os.path.basename(self.file.name).split('-',1)[1]
			except:
				name = 'attachment'
			return name
		return u''
	def deletable(self):
		for entry in Entry.objects.filter(applicant=self.user):
			entry_data = entry.decode()
			for answer in entry_data:
				if u''.join([u'a',unicode(self.id)]) in answer:
					return False
		return True

@receiver(pre_delete, sender=Attachment)
def attachment_delete(sender,instance,**kwargs):
	instance.file.delete(False)

class Publication(models.Model):
	class Meta:
		ordering = ['rank','-active']
	title = models.CharField(max_length=64,verbose_name='Publication',unique=True)
	description = models.TextField(blank=True,null=True)
	active = models.BooleanField(default=False)
	slug = models.SlugField(max_length=64,unique=True)
	rank = models.PositiveSmallIntegerField()
	def __unicode__(self):
		return self.title
	def deletable(self):
		return not self.position_set.exists()
	def no_app(self):
		return not self.position_set.filter(active=True).exists()
	def short_description(self):
		return self.description.split(u'\n\n')[0].split(u'\r\n\r\n')[0]

class Position(models.Model):
	class Meta:
		unique_together = (('publication','title'),('slug','publication'),)
		ordering = ['publication','rank','-active']
	publication = models.ForeignKey(Publication)
	title = models.CharField(max_length=64,verbose_name='Position')
	description = models.TextField(blank=True,null=True)
	active = models.BooleanField(default=False)
	slug = models.SlugField(max_length=64)
	rank = models.PositiveSmallIntegerField()
	def __unicode__(self):
		return ': '.join([self.publication.__unicode__(),self.title])
	def open(self):
		for app in self.application_set.all():
			if app.is_open():
				return True
	def deletable(self):
		return not self.application_set.exists()
	def short_description(self):
		return self.description.split(u'\n\n')[0].split(u'\r\n\r\n')[0]

class Application(models.Model):
	class Meta:
		unique_together = (('position','quarter','year'),('slug','position'),)
		ordering = ['-quarter','-year','position','-open','-close']
	position = models.ForeignKey(Position)
	notice = models.TextField(blank=True)
	staff_notes = models.TextField(blank=True)
	open = models.DateTimeField()
	close = models.DateTimeField()
	quarter = models.CharField(max_length=1,choices=QUARTERS)
	year = models.PositiveSmallIntegerField()
	data = models.TextField()
	slug = models.SlugField(max_length=64)
	publish = models.BooleanField(default=False)
	def __unicode__(self):
		return ' '.join(map(unicode,[self.quarter_string(),self.year]))
	def full_name(self):
		return ' '.join(map(unicode,[self.position,'-',choice_string(QUARTERS,self.quarter),self.year]))
	def decode(self):
		if self.data:
			return ast.literal_eval(self.data)
		else:
			return []
	def encode(self,data):
		self.data = unicode(data)
	def quarter_string(self):
		return choice_string(QUARTERS,self.quarter)
	def is_active(self):
		return self.publish and self.position.active and self.position.publication.active 
	def is_open(self):
		return self.open <= timezone.now() <= self.close and self.is_active()
	def is_pending(self):
		return self.is_active() and timezone.now() < self.open
	def is_closing_soon(self):
		return self.is_open() and self.close - timezone.now() <= datetime.timedelta(weeks=1)
	def is_on_hold(self):
		return not self.is_active() and timezone.now() <= self.close
	def deletable(self):
		return not self.publish and not self.entry_set.exclude(status=Entry.INCOMPLETE).exists()

def set_app_filename(instance,filename):
	path='application_attachments'
	name=u'-'.join([unicode(instance.application.id),filename])
	return os.path.join(path,name)

class AppAttachment(models.Model):
	application = models.ForeignKey(Application)
	name = models.CharField(max_length=128)
	file = models.FileField(upload_to=set_app_filename)

@receiver(pre_delete, sender=AppAttachment)
def appattachment_delete(sender,instance,**kwargs):
	instance.file.delete(False)

class Entry(models.Model):
	class Meta:
		verbose_name_plural = 'Entries'
		unique_together=(('applicant','application'),)
		ordering = ['status','submit','start','application',]
	ACCEPTED = '1'#'A'
	REJECTED = '2'#'R'
	WAITLISTED = '3'#'W'
	DECLINED = '4'#'D'
	SUBMITTED = '5'#'S'
	INCOMPLETE = '6'#'I'
	STATUSES = (
		(ACCEPTED, 'Accepted'),
		(REJECTED, 'Rejected'),
		(WAITLISTED, 'Waitlisted'),
		(DECLINED, 'Declined'),
		(SUBMITTED, 'Submitted'),
		(INCOMPLETE, 'Incomplete'),
	)
	quarter = models.CharField(max_length=1,choices=QUARTERS)
	year = models.PositiveSmallIntegerField()
	applicant = models.ForeignKey(User)
	application = models.ForeignKey(Application)
	status = models.CharField(max_length=1,choices=STATUSES,default=INCOMPLETE)
	start = models.DateTimeField(auto_now_add=True)
	submit = models.DateTimeField(blank=True,null=True)
	data = models.TextField(default='{}')
	notes = models.TextField(blank=True)
	def __unicode__(self):
		return ' '.join(map(unicode,[self.application.position,'-',choice_string(QUARTERS,self.quarter),self.year]))
		#return ' at '.join([unicode(self.applicant),unicode(self.application)])
	def decode(self):
		if self.data:
			return ast.literal_eval(self.data)
		else:
			return []
	def encode(self,data):
		self.data = unicode(data)
	def quarter_string(self):
		return choice_string(QUARTERS,self.quarter)
	def status_string(self):
		return choice_string(Entry.STATUSES,self.status)
	def is_valid(self):
		entry = self.decode()
		application = self.application.decode()
		for i,section in enumerate(application):
			for j,question in enumerate(section['questions']):
				key = '.'.join(map(str,[i,j]))
				if key not in entry or not entry[key]:
					return False
		return True

def combine(application,entry):
	application_data = application.decode()
	entry_data = entry.decode()
	for i,section in enumerate(application_data):
		for j,question in enumerate(section['questions']):
			key = '.'.join(map(str,[i,j]))
			if question['type'] in ['checkbox','radio']:
				for k,answer in enumerate(question['answer']):
					answer['chosen'] = key in entry_data and unicode(k) in entry_data[key]
			elif question['type'] == 'text':
				if key in entry_data and entry_data[key]:
					question['answer'] = entry_data[key][0]
				else:
					question['answer'] = ''
			else:
				question['attachmenttype'] = AttachmentType.objects.get(pk=question['type'])
				try:
					question['answer'] = [{'id':attachment.id,'filename':attachment.filename(),'url':attachment.file.url,'chosen':(key in entry_data and u''.join([u'a',unicode(attachment.id)]) in entry_data[key])} for attachment in Attachment.objects.filter(user=entry.applicant,type__id=int(question['type']))]
				except:
					question['answer'] = ''
	return application_data
