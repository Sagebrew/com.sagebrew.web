import csv
from django.core.management.base import BaseCommand
from django.conf import settings

from plebs.neo_models import University, HighSchool


class Command(BaseCommand):
    args = 'None.'
    help = 'Test the conductor api endpoints.'
    universities = settings.CSV_FILES + 'university_list.csv'
    public_schools = settings.CSV_FILES + 'public_school_list.csv'

    def populate_universities(self):
        '''
        This function accesses the local file university_list.csv, converts
        it into a
        dictionary then creates a node of Universiy with the information in
        each dictionary

        :return:
        '''
        line = 0
        university_dict = csv.DictReader(open(self.universities))
        for row in university_dict:
            row.pop('', None)
            print line
            line += 1
            for item in row:
                if isinstance(item, str):
                    row[item] = row[item].decode('ASCII', 'ignore')

            my_univ = University(**row)
            my_univ.save()

    def populate_public_schools(self):
        '''
        This function accesses the local file public_school_list.csv,
        converts each row
        into a dictionary then populates a HighSchool node only if the name
        of the school
        contains 'HIGH'.

        :return:
        '''
        public_schools_dict = csv.DictReader(open(self.public_schools))
        for row in public_schools_dict:
            row.pop('', None)
            if 'HIGH' in row['school_name']:  # TODO Add better filter for
                # more accurate results
                if row[
                    'phone_number'] == 'M' or 'N':  #TODO Add better way to
                    # handle invalid phone_number
                    row['phone_number'] = 0
                my_school = HighSchool(**row)
                my_school.save()


    def handle(self, *args, **options):
        self.populate_universities()
        self.populate_public_schools()
        self.stdout.write("Finished populating schools and universities")
