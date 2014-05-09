from django.db import models
from localflavor.us.models import USStateField

COUNTRY_CHOICES = (
                    ('US', 'United States of America'),
                  )


class Address(models.Model):
    '''
    This class defines an address object. Reason for current design:

    Overall:
    Did not allow null and blanks set to True for all of the attributes other
    than the additional street information because we need to
    know where people live to one enable ourselves to follow regulations
    of that state and two so we can track where our customers are and
    where we should target. - Devon Bleibtrey

    Attributes: building_num and street_name
    Combined to street to adhere to both @bleib1dj and @mwisner
    forms. Adding a function to split up to building_num and street_name
    for any feasible need to do so. - Devon Bleibtrey

    Attributes: street_additional
    Need to store apartment numbers and whatnot - Matt Wisner

    Attributes: postal_code
    Postal code cannot be an int because some places have none int zipcodes,
    such as CA zip codes look like 4AC-49Z. - Matt Wisner

    Attributes: country
    Made country choice field to only allow us to select which countries can
    be input. Should create custom clean_data functions in forms.py based on
    which country and state are selected and based on those do some cleaning
    and verification on zipcode. - Matt Wisner and Devon Bleibtrey

    Attributes: city
    Placed max_lenght value at 150 since the longest name of a city in the
    world is 105 letters long (Left room for magical locations).
    FYI Longest Name is: Taumatawhakatangihangakoauauotamateahaumaitawhitiure-
    haeaturipukakapikimaungahoronukupokaiwhenuakitanatah

    Attributes: street
    Placed max_length value at 120 because longest recognized street name is
    currently 72 chars long with spaces. Left some extra space for anyone
    going for the world record. And left some space for the building number.
    '''
    street = models.CharField(max_length=120)
    street_additional = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=150)
    state = USStateField()
    postal_code = models.CharField(max_length=10)
    country = models.CharField(choices=COUNTRY_CHOICES, max_length=2)

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'
        db_table = "addresses"

    def __unicode__(self):
        return(self.street + ", " + str(self.city) + ", " + str(self.state))


def create_address(info):
    '''
    create_address(dict) takes a set of address information, splits up the
    address street into a number and name and then checks if the entire address
    already exists in the database and if so does not create it again. If
    the address does not exist it creates it. In either case it returns the
    existing or created db object to the calling function.
    Dict must have the following keys populated:
        street - US address in form of:  1234 Fake St.
        city - US City
        state - US State
        zipcode - US Zipcode
        country - Selection from COUNTRY_CHOICES
    Need to add check that ensures that Companies do not reside at the same
    address. Must have at least different Room Numbers.
    '''
    try:
        street_address = info['street'].title()
        address = Address.objects.get(
                      street__iexact=street_address,
                      city__exact=info['city'],
                      state__exact=info['state'],
                      postal_code__exact=info['postal_code'],
                      country__exact=info['country'])
    except Address.DoesNotExist:
        street_address = info['street'].title()
        address = Address(street=street_address,
                          city=info['city'], state=info['state'],
                          postal_code=info['postal_code'],
                          country=info['country'])
        address.save()

    return address


def seperate_address_us(street_address):
    '''
    Takes a full US street address and converts it into a street number and
    street name so that they both can be sorted upon or to display them
    individually.
    '''
    street_info = street_address.split(' ')
    building_num = street_info[0]
    building_num = int(building_num)
    raw_street_name = street_info[1:]
    street_name = ''

    for item in raw_street_name:
        street_name += item
        street_name += ' '
    street_name = street_name.strip()

    return {'building_num': building_num, 'street_name': street_name}
