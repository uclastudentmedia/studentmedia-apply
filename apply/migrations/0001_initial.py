# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Contact'
        db.create_table(u'apply_contact', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('icon', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('title', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32)),
            ('info', self.gf('django.db.models.fields.TextField')()),
            ('number', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('show', self.gf('django.db.models.fields.BooleanField')()),
        ))
        db.send_create_signal(u'apply', ['Contact'])

        # Adding model 'ContactEmail'
        db.create_table(u'apply_contactemail', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('department', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
        ))
        db.send_create_signal(u'apply', ['ContactEmail'])

        # Adding model 'News'
        db.create_table(u'apply_news', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('publish', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('staff', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'apply', ['News'])

        # Adding model 'ProfileStatus'
        db.create_table(u'apply_profilestatus', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
        ))
        db.send_create_signal(u'apply', ['ProfileStatus'])

        # Adding model 'ProfileHelpText'
        db.create_table(u'apply_profilehelptext', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('field', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('info', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'apply', ['ProfileHelpText'])

        # Adding model 'Profile'
        db.create_table(u'apply_profile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('state', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['apply.ProfileStatus'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('first', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('middle', self.gf('django.db.models.fields.CharField')(max_length=16, null=True, blank=True)),
            ('last', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('email', self.gf('django.db.models.fields.EmailField')(unique=True, max_length=75)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('sid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=9)),
            ('birth', self.gf('django.db.models.fields.DateField')()),
            ('race', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('phone_perm', self.gf('django.db.models.fields.CharField')(max_length=16, null=True, blank=True)),
            ('phone_mob', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('website', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('add1_local', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('add2_local', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('city_local', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('state_local', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('postal_local', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('add1_perm', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('add2_perm', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('city_perm', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('state_perm', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('postal_perm', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('major', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('quarter', self.gf('django.db.models.fields.CharField')(default='2', max_length=1)),
            ('year', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('high', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('city_high', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('picture', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'apply', ['Profile'])

        # Adding model 'Status'
        db.create_table(u'apply_status', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['apply.Profile'])),
            ('start', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('status', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['apply.ProfileStatus'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
        ))
        db.send_create_signal(u'apply', ['Status'])

        # Adding model 'AttachmentType'
        db.create_table(u'apply_attachmenttype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal(u'apply', ['AttachmentType'])

        # Adding model 'Attachment'
        db.create_table(u'apply_attachment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['apply.AttachmentType'])),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'apply', ['Attachment'])

        # Adding model 'Publication'
        db.create_table(u'apply_publication', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=64)),
            ('rank', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
        ))
        db.send_create_signal(u'apply', ['Publication'])

        # Adding model 'Position'
        db.create_table(u'apply_position', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('publication', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['apply.Publication'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=64)),
            ('rank', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
        ))
        db.send_create_signal(u'apply', ['Position'])

        # Adding unique constraint on 'Position', fields ['publication', 'title']
        db.create_unique(u'apply_position', ['publication_id', 'title'])

        # Adding unique constraint on 'Position', fields ['slug', 'publication']
        db.create_unique(u'apply_position', ['slug', 'publication_id'])

        # Adding model 'Application'
        db.create_table(u'apply_application', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('position', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['apply.Position'])),
            ('notice', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('staff_notes', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('open', self.gf('django.db.models.fields.DateTimeField')()),
            ('close', self.gf('django.db.models.fields.DateTimeField')()),
            ('quarter', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('year', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('data', self.gf('django.db.models.fields.TextField')()),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=64)),
            ('publish', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'apply', ['Application'])

        # Adding unique constraint on 'Application', fields ['position', 'quarter', 'year']
        db.create_unique(u'apply_application', ['position_id', 'quarter', 'year'])

        # Adding unique constraint on 'Application', fields ['slug', 'position']
        db.create_unique(u'apply_application', ['slug', 'position_id'])

        # Adding model 'AppAttachment'
        db.create_table(u'apply_appattachment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('application', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['apply.Application'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal(u'apply', ['AppAttachment'])

        # Adding model 'Entry'
        db.create_table(u'apply_entry', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('quarter', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('year', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('applicant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('application', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['apply.Application'])),
            ('status', self.gf('django.db.models.fields.CharField')(default='6', max_length=1)),
            ('start', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('submit', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('data', self.gf('django.db.models.fields.TextField')(default='{}')),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'apply', ['Entry'])

        # Adding unique constraint on 'Entry', fields ['applicant', 'application']
        db.create_unique(u'apply_entry', ['applicant_id', 'application_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Entry', fields ['applicant', 'application']
        db.delete_unique(u'apply_entry', ['applicant_id', 'application_id'])

        # Removing unique constraint on 'Application', fields ['slug', 'position']
        db.delete_unique(u'apply_application', ['slug', 'position_id'])

        # Removing unique constraint on 'Application', fields ['position', 'quarter', 'year']
        db.delete_unique(u'apply_application', ['position_id', 'quarter', 'year'])

        # Removing unique constraint on 'Position', fields ['slug', 'publication']
        db.delete_unique(u'apply_position', ['slug', 'publication_id'])

        # Removing unique constraint on 'Position', fields ['publication', 'title']
        db.delete_unique(u'apply_position', ['publication_id', 'title'])

        # Deleting model 'Contact'
        db.delete_table(u'apply_contact')

        # Deleting model 'ContactEmail'
        db.delete_table(u'apply_contactemail')

        # Deleting model 'News'
        db.delete_table(u'apply_news')

        # Deleting model 'ProfileStatus'
        db.delete_table(u'apply_profilestatus')

        # Deleting model 'ProfileHelpText'
        db.delete_table(u'apply_profilehelptext')

        # Deleting model 'Profile'
        db.delete_table(u'apply_profile')

        # Deleting model 'Status'
        db.delete_table(u'apply_status')

        # Deleting model 'AttachmentType'
        db.delete_table(u'apply_attachmenttype')

        # Deleting model 'Attachment'
        db.delete_table(u'apply_attachment')

        # Deleting model 'Publication'
        db.delete_table(u'apply_publication')

        # Deleting model 'Position'
        db.delete_table(u'apply_position')

        # Deleting model 'Application'
        db.delete_table(u'apply_application')

        # Deleting model 'AppAttachment'
        db.delete_table(u'apply_appattachment')

        # Deleting model 'Entry'
        db.delete_table(u'apply_entry')


    models = {
        u'apply.appattachment': {
            'Meta': {'object_name': 'AppAttachment'},
            'application': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['apply.Application']"}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'apply.application': {
            'Meta': {'ordering': "['-quarter', '-year', 'position', '-open', '-close']", 'unique_together': "(('position', 'quarter', 'year'), ('slug', 'position'))", 'object_name': 'Application'},
            'close': ('django.db.models.fields.DateTimeField', [], {}),
            'data': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notice': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'open': ('django.db.models.fields.DateTimeField', [], {}),
            'position': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['apply.Position']"}),
            'publish': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'quarter': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '64'}),
            'staff_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'year': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        },
        u'apply.attachment': {
            'Meta': {'ordering': "['type', 'file']", 'object_name': 'Attachment'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['apply.AttachmentType']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'apply.attachmenttype': {
            'Meta': {'ordering': "['name']", 'object_name': 'AttachmentType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        u'apply.contact': {
            'Meta': {'ordering': "['number', 'title']", 'object_name': 'Contact'},
            'icon': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info': ('django.db.models.fields.TextField', [], {}),
            'number': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'show': ('django.db.models.fields.BooleanField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        },
        u'apply.contactemail': {
            'Meta': {'ordering': "['department']", 'object_name': 'ContactEmail'},
            'department': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'apply.entry': {
            'Meta': {'ordering': "['status', 'submit', 'start', 'application']", 'unique_together': "(('applicant', 'application'),)", 'object_name': 'Entry'},
            'applicant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'application': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['apply.Application']"}),
            'data': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'quarter': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'6'", 'max_length': '1'}),
            'submit': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'year': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        },
        u'apply.news': {
            'Meta': {'ordering': "['date']", 'object_name': 'News'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'publish': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'apply.position': {
            'Meta': {'ordering': "['publication', 'rank', '-active']", 'unique_together': "(('publication', 'title'), ('slug', 'publication'))", 'object_name': 'Position'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'publication': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['apply.Publication']"}),
            'rank': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '64'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'apply.profile': {
            'Meta': {'ordering': "['last', 'first', 'middle']", 'object_name': 'Profile'},
            'add1_local': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'add1_perm': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'add2_local': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'add2_perm': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'birth': ('django.db.models.fields.DateField', [], {}),
            'city_high': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'city_local': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'city_perm': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'first': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'high': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'major': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'middle': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'phone_mob': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'phone_perm': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'postal_local': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'postal_perm': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'quarter': ('django.db.models.fields.CharField', [], {'default': "'2'", 'max_length': '1'}),
            'race': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'sid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '9'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['apply.ProfileStatus']"}),
            'state_local': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'state_perm': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'}),
            'website': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'year': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        },
        u'apply.profilehelptext': {
            'Meta': {'object_name': 'ProfileHelpText'},
            'field': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info': ('django.db.models.fields.TextField', [], {})
        },
        u'apply.profilestatus': {
            'Meta': {'ordering': "['name']", 'object_name': 'ProfileStatus'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'apply.publication': {
            'Meta': {'ordering': "['rank', '-active']", 'object_name': 'Publication'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rank': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '64'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        u'apply.status': {
            'Meta': {'ordering': "['profile__last', 'profile__first', 'profile__middle', '-start']", 'object_name': 'Status'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['apply.Profile']"}),
            'start': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['apply.ProfileStatus']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['apply']