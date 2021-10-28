from urllib import request
from django import forms
from django.core.files.base import ContentFile
from django.utils.text import slugify
from .models import Image


class  ImageCreateForm(forms.ModelForm):

    class Meta:
        model = Image
        fields = ('title', 'url', 'description',)
        widgets = {
            'url':forms.HiddenInput,
        }
    
    def clean_url(self):
        """ only accept .jpg and .jpeg iamges"""
        url = self.cleaned_data['url']
        valid_extensions = ['jpg', 'jpeg']
        extension = url.rsplit('.',1)[1].lower() #get last element and make it lower
        if extension not in valid_extensions:
            raise forms.ValidationError("the given url does not match" \
                                        "valid images extensions")
        
        return url

    

    def save(self, force_insert = False,
            force_delete = False,
            commit=True):
        
        image = super().save(commit=False)
        image_url = self.cleaned_data['url']
        name = slugify(image.title)
        extension = image_url.rsplit('.', 1)[1].lower()
        image_name = f'{name}.{extension}'

        #download the image from the given url
        response = request.urlopen(image_url)
        image.image.save(image_name, 
                         ContentFile(response.read()),
                         save=False) # do not save to the db now 
        if commit:
            image.save()
        return image
