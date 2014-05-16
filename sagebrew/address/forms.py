from django.template import Context
from django.template.loader import render_to_string
from django import forms
from django.utils.translation import ugettext_lazy as _

from localflavor.us.forms import (USStateField,)
from localflavor.us.us_states import STATE_CHOICES


# Max lengths of attributes based on database models
CITY_MAX = 150
POSTAL_CODE_MAX = 10
ST_MAX = 100
ST_ADD_MAX = 100
COUNTRY_CHOICES = ("US", "United States of America")

def module_exists(module_name):
    """
    Should move this somewhere else!
    """
    try:
        __import__(module_name)
    except ImportError:
        return False
    else:
        return True

if module_exists("crispy_forms"):
    """
    Crispy forms address fields
    """
    from crispy_forms.utils import render_field, flatatt

    class CrispyAddress(object):
        template = "crispy_address.html"

        def __init__(self, *fields, **kwargs):
            self.css_class = 'address-fields-wrapper ' + kwargs.pop(
                                 'css_class', u'ctrlHolder')
            self.css_id = kwargs.pop('css_id', None)
            self.template = kwargs.pop('template', self.template)
            self.flat_attrs = flatatt(kwargs)

            if(hasattr(self, 'css_class') and 'css_class' in kwargs):
                self.css_class += ' %s' % kwargs.pop('css_class')
            if(not hasattr(self, 'css_class')):
                self.css_class = kwargs.pop('css_class', None)

            self.css_id = kwargs.pop('css_id', '')
            self.template = kwargs.pop('template', self.template)

        def render(self, form, form_style, context):
            OPTION_STATE_CHOICES = list(STATE_CHOICES)
            OPTION_STATE_CHOICES.insert(0, ('', '---------'))

            # @mwisner May want to just use the COUNTRY_CHOICES global from
            # the models.py file. Then you can just overwrite it if it doesn't
            # match the values you want.
            COUNTRIES = (
                ('usa', 'USA'),
                )

            form.fields['street'] = forms.CharField(required=False)
            form.fields['street_additional'] = forms.CharField(required=False)
            form.fields['city'] = forms.CharField(required=False)
            form.fields['state'] = forms.ChoiceField(required=False,
                                       choices=OPTION_STATE_CHOICES)
            form.fields['postal_code'] = forms.CharField(required=False)
            form.fields['country'] = forms.ChoiceField(required=False,
                                         choices=COUNTRIES)

            fields = ''
            fields += render_field('street', form, form_style, context)
            fields += render_field('street_additional', form,
                                   form_style, context)
            fields += render_field('city', form, form_style, context)
            fields += render_field('state', form, form_style, context)
            fields += render_field('postal_code', form, form_style, context)
            fields += render_field('country', form, form_style, context)

            return render_to_string(self.template, Context({'data': self,
                                                            'fields': fields}))

REQUIRED_ERRORS = {
                    'st_address': _("Street Address is Required"),
                    'st_name': _("Please enter a street name"),
                    'st_number': _("Please enter a street number"),
                    'city': _("Please enter a City"),
                    'state': _("Please enter a State"),
                    'country': _("Please enter the country you live in"),
                    'postal_code': _("Please enter a postal code"),
                   }
LENGTH_ERRORS = {
                    'st_num_max': _("Your Street Number is too long"),
                    'st_name_max': _("Your Street Name is too long"),
                    'st_num_min': _("Your Street Number must have at \
                                        least one number in it."),
                    'st_name_min': _("Your Street Name must have more \
                                         than one letter in it"),
                }
STREET_NOT_NUM_ERROR = _("Your Street Number is not a Number")
STREET_NAME_NO_NUM_ERROR = _("Please Enter a Street Name Without Numbers")
CITY_NO_NUM_ERROR = _("Please Enter a City With No Numbers")
# This should eventually be changed to define only an id and then move the
# all the other settings to a css file.
COUNTRY_ATTRS = {'size': 1, 'style': 'width: 200px'}


class AddressForm(forms.Form):
    '''
    This class provides a default form to use to pull information from a user
    to populate an address object in your db. It currently provides checks and
    cleans data based only on US addresses but we should expand it to
    do these checks based on the country and state/providence that are
    selected. Then based on those values do some custom cleaning to populate
    the database with.
    '''
    street = forms.CharField(max_length=ST_MAX,
                    error_messages={'required': REQUIRED_ERRORS['st_address']})
    street_additional = forms.CharField(max_length=ST_ADD_MAX, required=False)
    city = forms.CharField(max_length=CITY_MAX,
                error_messages={'required': REQUIRED_ERRORS['city']})
    state = USStateField(error_messages={'required': REQUIRED_ERRORS['state']})
    postal_code = forms.CharField(max_length=POSTAL_CODE_MAX,
                  error_messages={'required': REQUIRED_ERRORS['postal_code']})
    country = forms.ChoiceField(widget=forms.Select(attrs=COUNTRY_ATTRS),
                  choices=COUNTRY_CHOICES,
                  initial=u"US",
                  error_messages={'required': REQUIRED_ERRORS['country']})

    def clean_city(self):
        '''
        clean_city(AddressForm) is a simple cleaning function that ensures that
        the city only has alphebetical values in it. This can be changed if
        someone provides a city that has numbers in it.
        '''
        city_clean = self.cleaned_data['city']
        if(not city_clean.isalpha()):
            raise forms.ValidationError(CITY_NO_NUM_ERROR)
        return self.cleaned_data['city']

    def clean_street(self):
        '''
        clean_street_info(AddressForm) is a cleaning function that splits the
        passed street info into a building number and a street name and does
        checks on both. The limitation of this function is that it was designed
        based on US addresses and therefore will only work on addresses in the
        format of $Building_Number $Street_Name. We will need to expand this
        once any of our sites start accepting customers from countries such as
        Mexico. This is because their addresses are usually in the form of
        $Street_Name $Building_Number.
        '''
        street = self.cleaned_data['street'].strip()
        street = street.split(' ')
        street_clean = ''
        if(len(street) > 0 and street[0] != u''):
            street_number = street[0]
            # This if is located after the initial if because if it was
            # before it it would require street info to be entered.
            # Want the requirement to lie completely on required=True/False
            # passed parameter of the form field declaration.
            if(len(street) < 2):
                raise forms.ValidationError(REQUIRED_ERRORS['st_name'])
            if(len(street_number) > ST_MAX):
                raise forms.ValidationError(LENGTH_ERRORS['st_num_max'])
            if(not street_number.isdigit()):
                raise forms.ValidationError(STREET_NOT_NUM_ERROR)
            if(len(street) > 1):
                street_name = street[1:]
                for item in street_name:
                    street_clean += item
                if(street_clean.strip()[len(street_clean.strip()) - 1] == '.'):
                    street_clean = street_clean.strip()
                    street_clean = street_clean[:len(street_clean.strip()) - 1]
                if(not street_clean.isalpha()):
                    raise forms.ValidationError(STREET_NAME_NO_NUM_ERROR)
                if(len(street_clean) > ST_MAX):
                    raise forms.ValidationError(LENGTH_ERRORS['st_name_max'])

        return self.cleaned_data['street']


class AddressSettingsForm(AddressForm):
    '''
    This class provides a default form for address settings. It enables you
    to provide the user with the same values located in the default
    AddressForm but without any of the fields required so that they can update
    only the fields they need to. This class extends AddressForm so it gains
    all of the cleaning functionality from it.
    '''
    street = forms.CharField(max_length=ST_MAX + ST_MAX,
                      required=False)
    city = forms.CharField(max_length=CITY_MAX, required=False)
    state = USStateField(required=False)
    postal_code = forms.CharField(max_length=POSTAL_CODE_MAX, required=False)
