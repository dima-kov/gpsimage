import os
import time
import datetime
import dateutil.parser
import exifread


class GPSImage(object):
    """
    """
    _exclude = ['lat', 'lng','debug','json','ok', 'help', 'x', 'y', 'path','exif', 'image']
    exif = {}

    def __init__(self, image):
        if isinstance(image, str):
            self.path = os.path.abspath(image)
            self.filename = os.path.basename(self.path)
            self.image = open(self.path)
        else:
            self.image = image

        # Initial Functions
        self._read_exif()

    def __repr__(self):
        if self.ok:
            return '<GPSImage - {0} [{1}, {2} ({3})]>'.format(self.filename, self.lat, self.lng, self.datum)
        else:
            return '<GPSImage [{1}]>'.format(self.status)

    def _read_exif(self):
        self.exif = exifread.process_file(self.image)


    def _dms_to_dd(self, dms, ref):
        if len(dms) == 3:
            degrees = dms[0].num
            minutes = dms[1].num / 60.0
            seconds = float(dms[2].num) / float(dms[2].den) / 60.0 / 60.0
            dd = degrees + minutes + seconds

            # South & West returns Negative values
            if ref in ['S', 'W']:
                dd *= -1
            return dd

    def _pretty(self, key, value, special=''):
        if special:
            key = special.get(key)
        if key:
            extra_spaces = ' ' * (20 - len(key))
            return '{0}{1}: {2}'.format(key, extra_spaces, value)

    def debug(self):
        # JSON Results
        print('## JSON Results')
        for key, value in self.json.items():
            print(self._pretty(key, value))
        print('')

        # Camera Raw
        if self._exif:
            print('## Camera Raw')
            for key, value in self._exif.items():
                print(self._pretty(key, value, TAGS))
            print('')

        # GPS Raw
        if self._GPSInfo:
            print('## GPS Raw')
            for key, value in self._GPSInfo.items():
                print(self._pretty(key, value, GPSTAGS))

    @property
    def status(self):
        if not self.exif:
            return 'ERROR - Exif not found'
        elif not self.ok:
            return 'ERROR - No Geometry'
        else:
            return 'OK'

    """
    @property
    def dpi(self):
        value = self._image.info.get('dpi')
        if value:
            if len(value) == 2:
                if bool(value[0] and value[1]):
                    return value
                # If both values are (0, 0) then change it to the standard 72DPI
                else:
                    return (72, 72)
        else:
            # Retrieves X & Y resolution from Exif instead of PIL Image
            x = self._divide(self.XResolution)
            y = self._divide(self.YResolution)
            if bool(x and y):
                return (int(x), int(y))
    """

    @property
    def ok(self):
        if bool(self.lat and self.lng):
            return True
        else:
            return False

    """
    @property
    def model(self):
        return self.Model

    @property
    def make(self):
        return self.Make

    """

    @property
    def datum(self):
        datum = self.exif.get('GPS GPSMapDatum')
        if datum:
            return datum.values
        else:
            return 'WGS-84'

    @property
    def lng(self):
        lng_dms = self.exif.get('GPS GPSLongitude')
        lng_ref = self.exif.get('GPS GPSLongitudeRef')
        if bool(lng_dms and lng_ref):
            return self._dms_to_dd(lng_dms.values, lng_ref.values)

    @property
    def x(self):
        return self.lng

    @property
    def lat(self):
        lat_dms = self.exif.get('GPS GPSLatitude')
        lat_ref = self.exif.get('GPS GPSLatitudeRef')
        if bool(lat_dms and lat_ref):
            return self._dms_to_dd(lat_dms.values, lat_ref.values)

    @property
    def y(self):
        return self.lat

    @property
    def altitude(self):
        altitude = self.exif.get('GPS GPSAltitude')
        if altitude:
            return altitude.values

    @property
    def direction(self):
        direction = self.exif.get('GPS GPSImgDirection')
        if direction:
            return direction.values

    @property
    def timestamp(self):
        # For GoPro
        timestamp = self.exif.get('Image DateTime')
        if timestamp:
            timestamp = timestamp.values.replace(':','-',2)
            return dateutil.parser.parse(timestamp)
    """
    @property
    def width(self):
        return self._image.size[0]

    @property
    def height(self):
        return self._image.size[1]

    @property
    def size(self):
        if bool(self.height and self.width):
            return (self.width, self.height)
    """

    @property
    def geometry(self):
        if self.ok:
            return {'type':'POINT', 'coordinates':[self.lng, self.lat]}

    @property
    def satellites(self):
        satellites = self.exif.get('GPS GPSSatellites').values
        if satellites:
            return int(satellites)

    @property
    def json(self):
        container = {}
        for key in dir(self):
            if bool(not key.startswith('_') and key not in self._exclude):
                value = getattr(self, key)
                if value:
                    container[key] = value
        return container
