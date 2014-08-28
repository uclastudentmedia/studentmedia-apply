import datetime
from datetime import date
from django import forms
from django.forms.util import to_current_timezone
from django.utils import timezone

class SuperDateTimeWidget(forms.MultiWidget):
	def __init__(self,attrs={}):
		attrs['class'] = 'input-mini'
		widgets = (
			forms.Select(choices=((i,i) for i in range(1,13)),attrs=attrs),
			forms.Select(choices=((i,i) for i in range(1,32)),attrs=attrs),
			forms.TextInput(attrs=attrs),
			forms.Select(choices=((i,i) for i in [12]+range(1,12)),attrs=attrs),
			forms.Select(choices=((i,i) for i in range(60)),attrs=attrs),
			forms.Select(choices=((i,i) for i in range(60)),attrs=attrs),
			forms.Select(choices=(('a','a.m.'),('p','p.m.')),attrs=attrs)
		)
		super(SuperDateTimeWidget,self).__init__(widgets,attrs)
	def decompress(self,value):
		if value:
			value = to_current_timezone(value)
			hour = value.hour%12
			if hour == 0:
				hour = 12
			return [value.month,value.day,value.year,hour,value.minute,value.second,'a' if value.hour < 12 else 'p']
		return [None,None,None,None,None,None]
	def format_output(self,rendered_widgets):
		return u''.join([u'Date: ',rendered_widgets[0],u' / ',rendered_widgets[1],u' / ',rendered_widgets[2],u' Time: ',rendered_widgets[3],u' : ',rendered_widgets[4],u' : ',rendered_widgets[5],rendered_widgets[6]])
	def value_from_datadict(self,data,files,name):
		datelist = [widget.value_from_datadict(data,files,name+'_%s'%i) for i,widget in enumerate(self.widgets)]
		hour = int(datelist[3])
		if hour == 12:
			hour = 0
		if datelist[6] == 'p':
			hour+=12
		day = int(datelist[1])
		try:
			D = datetime.datetime(month=int(datelist[0]),day=day,year=int(datelist[2]),hour=hour,minute=int(datelist[4]),second=int(datelist[5]))
			return D
		except:
			return None
