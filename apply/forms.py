from datetime import date
from django import forms
from django.forms.extras import widgets
from django.forms.models import inlineformset_factory
from django.forms.util import to_current_timezone
from django.utils import timezone
from models import *
from widgets import *

years = range(date.today().year,1914,-1)

class ContactForm(forms.Form):
	sender = forms.EmailField(widget=forms.TextInput(attrs={'class':'input-block-level'}))
	recipient = forms.ModelChoiceField(queryset=ContactEmail.objects.all(),widget=forms.Select(attrs={'onload':'updateRecipient(this)','onchange':'updateRecipient(this)','class':'input-block-level'}))
	subject = forms.CharField(widget=forms.TextInput(attrs={'class':'input-block-level'}))
	message = forms.CharField(widget=forms.Textarea(attrs={'class':'input-block-level','rows':'8'}))

class EmailForm(forms.Form):
	sender = forms.EmailField(widget=forms.TextInput(attrs={}))
	recipients = forms.CharField()
	subject = forms.CharField()
	message = forms.CharField()

class ProfileForm(forms.ModelForm):
	def __init__(self,*args,**kwargs):
		super(ProfileForm,self).__init__(*args,**kwargs)
		for field_name in self.fields:
			field = self.fields.get(field_name)
			if field and type(field.widget) == forms.TextInput:
				field.widget = forms.TextInput(attrs={'placeholder':field.label})
	class Meta:
		model = Profile
		exclude = ('user','state','race')
		widgets = {
			'birth':widgets.SelectDateWidget(years=years),
		}

class AttachmentForm(forms.ModelForm):
	class Meta:
		model = Attachment
		exclude = ('user',)

class ProfileSearchForm(forms.Form):
	p = forms.IntegerField()
	pp = forms.IntegerField()
	position = forms.CharField(required=False,help_text='Position',widget=forms.TextInput(attrs={'placeholder':'Position'}))
	status = forms.ModelMultipleChoiceField(queryset=ProfileStatus.objects.all())
	name = forms.CharField(required=False,help_text='Name',widget=forms.TextInput(attrs={'placeholder':'Name'}))
	email = forms.CharField(required=False,help_text='Email Address',widget=forms.TextInput(attrs={'placeholder':'Email'}))
	gender = forms.CharField(required=False,help_text='Gender',widget=forms.TextInput(attrs={'placeholder':'Male/Female/etc'}))
	num_mob = forms.CharField(required=False,help_text='Mobile Number',widget=forms.TextInput(attrs={'placeholder':'Mobile Phone'}))
	num_prm = forms.CharField(required=False,help_text='Permanent Number',widget=forms.TextInput(attrs={'placeholder':'Permanent Phone'}))
	addr_loc = forms.CharField(required=False,help_text='Local Adddress',widget=forms.TextInput(attrs={'placeholder':'Local Address'}))
	addr_prm = forms.CharField(required=False,help_text='Permanent Address',widget=forms.TextInput(attrs={'placeholder':'Permanent Address'}))
	major = forms.CharField(required=False,help_text='Major',widget=forms.TextInput(attrs={'placeholder':'Major'}))
	quarter = forms.MultipleChoiceField(choices=QUARTERS)
	year_low = forms.IntegerField(required=False,min_value=1000,max_value=9999,help_text='Lower Bound',widget=forms.TextInput(attrs={'placeholder':'Graduating On/After'}))
	year_high = forms.IntegerField(required=False,min_value=1000,max_value=9999,help_text='Upper Bound',widget=forms.TextInput(attrs={'placeholder':'Graduating On/Before'}))
	high = forms.CharField(required=False,help_text='High School',widget=forms.TextInput(attrs={'placeholder':'High School'}))

class EntrySearchForm(ProfileSearchForm):
	ufilter = forms.ChoiceField(choices=(('u','Unique'),('d','Duplicate')),widget=forms.RadioSelect)
	entry_status = forms.MultipleChoiceField(choices=Entry.STATUSES,widget=forms.SelectMultiple(attrs={'size':6}))
	pub = forms.MultipleChoiceField(required=False,choices=sorted(list(set([(pub.slug,pub.title) for pub in Publication.objects.all()]))),widget=forms.SelectMultiple(attrs={'id':'pub','onchange':'updatePub(this)'}))
	pos = forms.MultipleChoiceField(required=False,choices=sorted(list(set([(pos.slug,pos.title) for pos in Position.objects.all()]))),widget=forms.SelectMultiple(attrs={'id':'pos','onchange':'updatePos(this)'}))
	#app = forms.MultipleChoiceField(required=False,choices=sorted(list(set([(app.slug,unicode(app)) for app in Application.objects.all()]))),widget=forms.SelectMultiple(attrs={'id':'app'}))
	e_quarter = forms.MultipleChoiceField(required=False,choices=QUARTERS,widget=forms.SelectMultiple(attrs={'id':'e_quarter'}))
	e_year = forms.MultipleChoiceField(required=False,choices=sorted(list(set([(ent.year,ent.year) for ent in Entry.objects.all()]))),widget=forms.SelectMultiple(attrs={'id':'e_year'}))

class NewAppForm(forms.Form):
	pos = forms.IntegerField(min_value=1)
	quarter = forms.ChoiceField(choices=QUARTERS,widget=forms.Select(attrs={'class':'search-query'}))
	year = forms.IntegerField(min_value=1000,max_value=9999,widget=forms.TextInput(attrs={'placeholder':'YYYY'}))

class NewsForm(forms.ModelForm):
	class Meta:
		model = News

class PublicationForm(forms.ModelForm):
	class Meta:
		model = Publication
		exclude = ('active','slug','rank')

class PositionForm(forms.ModelForm):
	class Meta:
		model = Position
		exclude = ('active','slug','rank')

AppAttachmentFormSet = inlineformset_factory(Application,AppAttachment)

class ApplicationForm(forms.ModelForm):
	class Meta:
		model = Application
		exclude = ('position','data','slug')
		widgets = {
			'notice':forms.Textarea(attrs={'class':'input-block-level','rows':'8'}),
			'open':SuperDateTimeWidget(),
			'close':SuperDateTimeWidget(),
			'staff_notes':forms.Textarea(attrs={'class':'input-block-level','rows':'8','placeholder':'This is only visible to editors; it will not show up on the final application.'}),
		}
	def __init__(self,*args,**kwargs):
		disabled = kwargs.pop('disabled',None)
		super(ApplicationForm,self).__init__(*args,**kwargs)
		if disabled:
			for key in self.fields:
				self.fields[key].widget.attrs['disabled'] = 'disabled'

class EntryForm(forms.ModelForm):
	class Meta:
		model = Entry
		exclude = ('applicant','application','status','start','submit','data')
