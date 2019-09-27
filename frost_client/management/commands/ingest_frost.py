import os
import json
import urllib3

from django.core.management.base import BaseCommand
from frost_client.models import Dataset



class Command(BaseCommand):
    args = '<client_id> <client_secret>'
    help = """
        Add metno observation station metadata to the archive. 

        Args:
            client_id : Frost API client id
            client_secret : Frost API client secret

        """
    def add_arguments(self, parser):
        parser.add_argument('--client_id',
                            action='store',
                            default=os.environ['FROST_CLIENT_ID'],
                            help='Frost API client ID')
        parser.add_argument('--client_secret',
                            action='store',
                            default=os.environ['FROST_CLIENT_SECRET'],
                            help='Frost API client secret')

    def handle(self, *args, **options):
        endpoint = 'https://frost.met.no/sources/v0.jsonld'
        http = urllib3.PoolManager(cert_reqs='CERT_NONE')
        headers = urllib3.util.make_headers(
            basic_auth=options.get('client_id')+':'+options.get('client_secret')
        )
        req = http.request('GET', endpoint, headers=headers)
        sources = json.loads(req.data)
        added = 0
        for source_data in sources['data']:
            ds, cr = Dataset.objects.get_or_create(source_data)
            if cr:
                added += 1
        self.stdout.write(
            'Successfully added metadata of %s metno observation station datasets' %added)

