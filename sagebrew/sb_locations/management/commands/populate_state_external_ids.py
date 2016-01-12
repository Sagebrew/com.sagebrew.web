from neomodel import db

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    args = 'None.'

    def populate_external_ids(self):
        built_dict = {
            "Alabama": "ChIJdf5LHzR_hogR6czIUzU0VV4",
            "Alaska": "ChIJG8CuwJzfAFQRNduKqSde27w",
            "Arizona": "ChIJaxhMy-sIK4cRcc3Bf7EnOUI",
            "Arkansas": "ChIJYSc_dD-e0ocR0NLf_z5pBaQ",
            "California": "ChIJPV4oX_65j4ARVW8IJ6IJUYs",
            "Colorado": "ChIJt1YYm3QUQIcR_6eQSTGDVMc",
            "Connecticut": "ChIJpVER8hFT5okR5XBhBVttmq4",
            "Delaware": "ChIJO9YMTXYFx4kReOgEjBItHZQ",
            "District of Columbia": "ChIJW-T2Wt7Gt4kRKl2I1CJFUsI",
            "Florida": "ChIJvypWkWV2wYgR0E7HW9MTLvc",
            "Georgia": "ChIJV4FfHcU28YgR5xBP7BC8hGY",
            "Hawaii": "ChIJBeB5Twbb_3sRKIbMdNKCd0s",
            "Idaho": "ChIJ6Znkhaj_WFMRWIf3FQUwa9A",
            "Illinois": "ChIJGSZubzgtC4gRVlkRZFCCFX8",
            "Indiana": "ChIJHRv42bxQa4gRcuwyy84vEH4",
            "Iowa": "ChIJGWD48W9e7ocR2VnHV0pj78Y",
            "Kansas": "ChIJawF8cXEXo4cRXwk-S6m0wmg",
            "Kentucky": "ChIJyVMZi0xzQogR_N_MxU5vH3c",
            "Louisiana": "ChIJZYIRslSkIIYRA0flgTL3Vck",
            "Maine": "ChIJ1YpTHd4dsEwR0KggZ2_MedY",
            "Maryland": "ChIJ35Dx6etNtokRsfZVdmU3r_I",
            "Massachusetts": "ChIJ_b9z6W1l44kRHA2DVTbQxkU",
            "Michigan": "ChIJEQTKxz2qTE0Rs8liellI3Zc",
            "Minnesota": "ChIJmwt4YJpbWE0RD6L-EJvJogI",
            "Mississippi": "ChIJGdRK5OQyKIYR2qbc6X8XDWI",
            "Missouri": "ChIJfeMiSNXmwIcRcr1mBFnEW7U",
            "Montana": "ChIJ04p7LZwrQVMRGGwqz1jWcfU",
            "Nebraska": "ChIJ7fwMtciNk4cRxArzDwyQJ6E",
            "Nevada": "ChIJcbTe-KEKmYARs5X8qooDR88",
            "New Hampshire": "ChIJ66bAnUtEs0wR64CmJa8CyNc",
            "New Jersey": "ChIJn0AAnpX7wIkRjW0_-Ad70iw",
            "New Mexico": "ChIJqVKY50NQGIcRup41Yxpuv0Y",
            "New York": "ChIJqaUj8fBLzEwRZ5UY3sHGz90",
            "North Carolina": "ChIJgRo4_MQfVIgRGa4i6fUwP60",
            "North Dakota": "ChIJY-nYVxKD11IRyc9egzmahA0",
            "Ohio": "ChIJwY5NtXrpNogRFtmfnDlkzeU",
            "Oklahoma": "ChIJnU-ssRE5rIcRSOoKQDPPHF0",
            "Oregon": "ChIJVWqfm3xuk1QRdrgLettlTH0",
            "Pennsylvania": "ChIJieUyHiaALYgRPbQiUEchRsI",
            "Rhode Island": "ChIJD9cOYhQ15IkR5wbB57wYTh4",
            "South Carolina": "ChIJ49ExeWml-IgRnhcF9TKh_7k",
            "South Dakota": "ChIJpTjphS1DfYcRt6SGMSnW8Ac",
            "Tennessee": "ChIJA8-XniNLYYgRVpGBpcEgPgM",
            "Texas": "ChIJSTKCCzZwQIYRPN4IGI8c6xY",
            "Utah": "ChIJzfkTj8drTIcRP0bXbKVK370",
            "Vermont": "ChIJ_87aSGzctEwRtGtUNnSJTSY",
            "Virginia": "ChIJzbK8vXDWTIgRlaZGt0lBTsA",
            "Washington": "ChIJ-bDD5__lhVQRuvNfbGh4QpQ",
            "West Virginia": "ChIJRQnL1KVUSogRQzrN3mjHALs",
            "Wisconsin": "ChIJr-OEkw_0qFIR1kmG-LjV1fI",
            "Wyoming": "ChIJaS7hSDTiXocRLzh90nkisCY"
        }
        for state in built_dict:
            query = 'MATCH (a:Location {name: "United States of America"})-' \
                    '[ENCOMPASSES]->(b:Location {name: "%s"}) ' \
                    'SET b.external_id="%s"' % (state, built_dict[state])
            res, _ = db.cypher_query(query)

    def handle(self, *args, **options):
        self.populate_external_ids()
