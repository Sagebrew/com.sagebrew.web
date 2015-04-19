import csv
from django.core.management.base import BaseCommand
from django.conf import settings

from govtrack.neo_models import GTPersonHistorical


class Command(BaseCommand):
    args = 'None.'
    help = 'Test the conductor api endpoints.'
    historical_people = settings.CSV_FILES + 'legislators-historic.csv'
    # TODO set up functions to use the govtrack bulk data to get complete
    # sets of data

    def populate_historical_people(self):
        '''
        Reads from lesislators-historic.csv and populates GTPersonHistorical
        objects
        with data from the file.

        :return:
        '''
        people_dict = csv.DictReader(open(self.historical_people))
        for row in people_dict:
            row.pop('', None)

            try:
                if row['gt_id'] != '':
                    GTPersonHistorical.nodes.get(gt_id=row['gt_id'])
                else:
                    row['gt_id'] = '0'
                    raise GTPersonHistorical.DoesNotExist
            except GTPersonHistorical.DoesNotExist:

                for item in row:
                    if isinstance(item, str):
                        row[item] = row[item].decode('ASCII', 'ignore')
                my_person = GTPersonHistorical(**row)
                my_person.save()

    def handle(self, *args, **options):
        self.populate_historical_people()
