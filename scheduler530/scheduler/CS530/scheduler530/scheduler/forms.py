from django import forms

class MajorForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)

# class UploadTranscriptForm(forms.Form):
# 	title = forms.charField(max_length=75)
# 	file = forms.FileField()
	