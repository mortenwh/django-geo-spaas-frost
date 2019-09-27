import urllib3
import warnings
from dateutil.parser import parse

import pythesint as pti

from django.db import models
from django.contrib.gis.geos import GEOSGeometry

from geospaas.vocabularies.models import Platform
from geospaas.vocabularies.models import Instrument
from geospaas.vocabularies.models import DataCenter
from geospaas.vocabularies.models import Parameter
from geospaas.vocabularies.models import ISOTopicCategory
from geospaas.catalog.models import GeographicLocation
from geospaas.catalog.models import DatasetURI, Source, Dataset, DatasetParameter

class FrostManager(models.Manager):

    def get_or_create(self, source_data, *args, **kwargs):
        """ Create dataset and corresponding metadata

        Parameters:
        ----------
            source_data : 

        Returns:
        -------
            dataset and flag
        """

        entry_id = source_data['id']

        # check if dataset already exists
        ds = Dataset.objects.filter(entry_id=entry_id)
        if len(ds) > 0:
            return ds[0], False

        # set source
        platform = pti.get_gcmd_platform('meteorological stations')
        instrument = pti.get_gcmd_instrument('in situ/laboratory instruments')

        pp = Platform.objects.get(
                category=platform['Category'],
                series_entity=platform['Series_Entity'],
                short_name=platform['Short_Name'],
                long_name=platform['Long_Name']
            )
        ii = Instrument.objects.get(
                category = instrument['Category'],
                instrument_class = instrument['Class'],
                type = instrument['Type'],
                subtype = instrument['Subtype'],
                short_name = instrument['Short_Name'],
                long_name = instrument['Long_Name']
            )
        source = Source.objects.get_or_create(
            platform = pp,
            instrument = ii)[0]

        try:
            station_name = source_data['name']
        except KeyError:
            return None, False
        try:
            longitude = source_data['geometry']['coordinates'][0]
        except KeyError:
            return None, False
        latitude = source_data['geometry']['coordinates'][1]
        location = GEOSGeometry('%s(%s %s)' % (source_data['geometry']['@type'], longitude,
            latitude))

        geolocation = GeographicLocation.objects.get_or_create(
                            geometry=location)[0]

        entrytitle = source_data['name'] + ' ' + source_data['@type']
        dc = DataCenter.objects.get(short_name='NO/MET')
        iso_category = ISOTopicCategory.objects.get(name='Climatology/Meteorology/Atmosphere')
        summary = ''

        ds = Dataset(
                entry_id = entry_id,
                entry_title = entrytitle,
                ISO_topic_category = iso_category,
                data_center = dc,
                summary = summary,
                time_coverage_start=parse(source_data['validFrom']),
                source=source,
                geographic_location=geolocation)
        ds.save()

        #ds_uri = DatasetURI.objects.get_or_create(uri=uri, dataset=ds)[0]

        ## Add dataset parameters
        #vars = nc_dataset.variables
        #time = vars.pop('time')
        #lat = vars.pop('latitude')
        #lon = vars.pop('longitude')
        #id = vars.pop('station_id')
        #for key in vars.keys():
        #    if not 'standard_name' in vars[key].ncattrs():
        #        continue
        #    try:
        #        par = Parameter.objects.get(standard_name=vars[key].standard_name)
        #    except Parameter.DoesNotExist as e:
        #        warnings.warn('{}: {}'.format(vars[key].standard_name, e.args[0]))
        #        continue
        #    dsp = DatasetParameter(dataset=ds, parameter=par)
        #    dsp.save()

        return ds, True

