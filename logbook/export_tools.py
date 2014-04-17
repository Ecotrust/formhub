from reportlab.pdfgen import canvas
from pyPdf import PdfFileWriter, PdfFileReader
import StringIO
from io import BytesIO
from reportlab.lib.pagesizes import letter
import os
import random
import datetime
from django.http import Http404
from django.conf import settings


def get_usgs_quads(pts):
    from django.contrib.gis.gdal.datasource import DataSource

    shp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                        "data", 'quadgrid_4326.shp')
    ds = DataSource(shp_path)
    layer = ds[0]

    quads = []
    for pt in pts:
        lng, lat = pt
        buf = 0.00000001
        layer.spatial_filter = (lng - buf, lat - buf, lng + buf, lat + buf)
        quads.extend([feat.get('Name') for feat in layer])

    return ', '.join(set(quads))


def get_adfg_region(pts):
    from django.contrib.gis.gdal.datasource import DataSource

    shp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                        "data", 'adfg_regions_4326.shp')
    ds = DataSource(shp_path)
    layer = ds[0]

    quads = []
    for pt in pts:
        lng, lat = pt
        buf = 0.00000001
        layer.spatial_filter = (lng - buf, lat - buf, lng + buf, lat + buf)
        quads.extend([feat.get('REGION') for feat in layer])

    return ', '.join(set(quads))


def extend_meta_profile(meta, user):
    profile = user.get_profile()
    uname = profile.name
    if uname == '':
        uname = user.get_full_name()
    meta['user']  = uname
    meta['agency'] = profile.organization
    meta['addr1'] = profile.address
    meta['addr2'] = profile.city  # TODO profile needs state, zip
    meta['today'] = datetime.datetime.now().strftime("%Y-%m-%d")
    meta['email'] = user.email
    meta['phone'] = profile.phonenumber
    return meta

def get_obs_data(pi):
    data = {
      'lat': pi.lat,
      'lng': pi.lng,
    }

    for key in settings.FIELD_MAP.keys():
        data[key] = pi.to_dict().get(settings.FIELD_MAP[key], '')

    pi_dict = pi.to_dict()
    for key in sorted(pi_dict.keys()):
        if key == settings.FRP_LOCATION_KEY:
            val = pi_dict[key]
            val_lst = val.split()
            data['lat'] = float(val_lst[0])
            data['lng'] = float(val_lst[1])

    return data

def generate_pdf(id_string, submission_type, observations, user, permit_nums):
    from odk_viewer.models import ParsedInstance

    all_instances = ParsedInstance.objects.filter(instance__user=user,
                                        instance__xform__id_string=id_string, instance__deleted_at=None)

    # We should probably use the ORM filter for better performance but
    # I havent yet figured out how to query mongodb via ORM args
    pis = [x for x in all_instances 
              if x.to_dict()[settings.FIELD_MAP['permit_num']] in permit_nums
              and x.to_dict()['meta/instanceID'] in observations]

    if len(pis) == 0:
        raise Http404

    obs_data = [ get_obs_data(pi) for pi in pis ]

    pts = [(x['lng'], x['lat']) for x in obs_data]
    awc_nums = [x['awc_num'] for x in obs_data if x['awc_num']]
    awc_num = str(awc_nums[0])       # Nominations should only be for one waterway at a time.
    waterways = [x['waterway'] for x in obs_data if x['waterway']]
    waterway = str(waterways[0])     # Nominations should only be for one waterway at a time.
    name_type = obs_data[0]['name_type']

    meta = {
        'region': get_adfg_region(pts)[:26],
        'quad': get_usgs_quads(pts)[:41],
        'awc_num': awc_num,
        'awc_name': waterway[:41], 
        'awc_name_type': name_type,
        'nomination_type': submission_type,
    }

    meta = extend_meta_profile(meta, user)

    # Create pdf
    packet = StringIO.StringIO()
    can = canvas.Canvas(packet)

    # render a new PDF with Reportlab
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont('Courier', 9)

    # render metadata
    hs = [696, 673, 650, 631]
    can.drawString(78, hs[0] , meta['region'])
    can.drawString(342, hs[0], meta['quad'])
    if meta['nomination_type'] != 'addition':
        can.drawString(240, hs[1], meta['awc_num'])
    can.drawString(118, hs[2], meta['awc_name'])

    if meta['awc_name_type'] == 'usgs name':
        can.drawString(363, hs[2]+3, u"\u2713")
    elif meta['awc_name_type'] == 'local name':
        can.drawString(466, hs[2]+3, u"\u2713")

    if meta['nomination_type'] == 'addition':
        can.drawString(59, hs[3], u"\u2713")
    elif meta['nomination_type'] == 'deletion':
        can.drawString(135, hs[3], u"\u2713")
    elif meta['nomination_type'] == 'correction':
        can.drawString(220, hs[3], u"\u2713")
    elif meta['nomination_type'] == 'backup':
        can.drawString(291, hs[3], u"\u2713")

    # Add a page for each observation, extracting comments for first page
    comments = []
    pi_pages = []
    obs_num = 1
    for pi in pis:
        obs_page, comment= get_obs_pdf(pi, user.username)
        pi_pages.append(obs_page)
        if len(comment) > 75:
            comments.append('Observation ' + str(obs_num) + ': ' + comment[:72] + '...')
        else:
            comments.append('Observation ' + str(obs_num) + ': ' + comment)
        obs_num += 1

    comment0 = "Please see additional notes in supporting documentation."
    can.drawString(110, 296, comment0)

    lineHeight = 285
    for comment in comments:
        can.drawString(40, lineHeight, comment)
        lineHeight = lineHeight - 11

    if meta['email'] and meta['phone']:
        contact_print = "Contact Info: Email %s, Phone %s " % (meta['email'], meta['phone'])
        can.drawString(40, 226, contact_print)

    can.setFont('Courier', 7)
    disclaimer = "AWC nomination form generated by aklogbook.ecotrust.org"
    can.drawString(40, 215, disclaimer)
    can.setFont('Courier', 9)

    can.drawString(220, 190, meta['user'])
    can.drawString(220, 160, meta['agency'])
    can.drawString(220, 145, meta['addr1'])
    can.drawString(220, 130, meta['addr2'])
    can.drawString(450, 175, awc_date_format(meta['today']))

    # render observational data
    for i, sd in enumerate(obs_data):
        height = 422 - 15*i
        can.drawString(35, height, sd['species'][:17])
        can.drawString(190, height, awc_date_format(sd['date']))
        if sd['observation_type'].lower() == "spawning":
            can.drawString(295, height, u"\u2713")
        if sd['observation_type'].lower() == "rearing":
            can.drawString(360, height, u"\u2713")
        if sd['observation_type'].lower() == "present":
            can.drawString(440, height, u"\u2713")
        if sd['species_group'].lower().startswith("anadromous") or sd['species_group'].lower().startswith("salmonidae"):
            can.drawString(502, height, u"\u2713")
    can.save()

    #move to the beginning of the StringIO buffer
    packet.seek(0)
    new_pdf = PdfFileReader(packet)

    # read your existing PDF
    orig = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                        "original.pdf")
    existing_pdf = PdfFileReader(file(orig, "rb"))
    output = PdfFileWriter()
    # add the "watermark" (which is the new pdf) on the existing page
    page = existing_pdf.getPage(0)
    page.mergePage(new_pdf.getPage(0))
    output.addPage(page)

    for pi_page in pi_pages:
        output.addPage(pi_page)

    # finally, return output
    outputStream = BytesIO()
    output.write(outputStream)

    final = outputStream.getvalue()
    outputStream.close()

    return final


def awc_date_format(date):
    date_parts = date.split('-')
    date_string = date_parts[1] + '/' + date_parts[2] + '/' + date_parts[0]
    return date_string

def generate_frp_xls(id_string, biol_date, user, permit_nums):
    from odk_viewer.models import ParsedInstance
    import xlrd
    from xlutils.copy import copy

    all_instances = ParsedInstance.objects.filter(instance__user=user,
                                        instance__xform__id_string=id_string, instance__deleted_at=None)

    # We should probably use the ORM filter for better performance but
    # I havent yet figured out how to query mongodb via ORM args
    if len(permit_nums) > 1:
        raise Exception("Only one permit number per FRP export")

    pis = [x for x in all_instances 
        if x.to_dict()[settings.FIELD_MAP['permit_num']] in permit_nums 
        and (
            (x.to_dict().has_key(settings.SHOW_FRP_KEY) and  x.to_dict()[settings.SHOW_FRP_KEY] == 'TRUE') 
            or #support old survey forms that don't have this
            (not x.to_dict().has_key(settings.SHOW_FRP_KEY) )
        )
    ]

    if len(pis) == 0:
        raise Http404

    obs_data = [ get_obs_data(pi) for pi in pis ]

    pts = [(x['lng'], x['lat']) for x in obs_data]

    meta = {
        'region': get_adfg_region(pts),
        'quad': get_usgs_quads(pts),
        'biologist_contact': biol_date
    }

    meta = extend_meta_profile(meta, user)

    content = StringIO.StringIO()

    # read your existing PDF
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                        "frp_original.xls")
    orig_book = xlrd.open_workbook(file_path, formatting_info=True)
    wb = copy(orig_book)
    ws = wb.get_sheet(0)
    start_row_idx = 4

    ws.write(0, 0, "ADF&G permit no. %s" % obs_data[0]['permit_num'])

    # Documentations showed some degree of finickiness with date formats. The preferred format is now enforced.
    bio_date = meta['biologist_contact'].split('-')
    ws.write(2, 0, "The area biologist was contacted on: %s/%s/%s" % (bio_date[1], bio_date[2], bio_date[0]))

    for i, obs in enumerate(obs_data):
        ws.write(start_row_idx+i,0,obs['permit_num'])
        ws.write(start_row_idx+i,1,obs['lat'])
        ws.write(start_row_idx+i,2,obs['lng'])
        ws.write(start_row_idx+i,3,"WGS84")
        ws.write(start_row_idx+i,4,"MobileGPS")
        ws.write(start_row_idx+i,5,obs['waterway'])
        date_split = obs['date'].split('-')
        ws.write(start_row_idx+i,6,date_split[1] + "/" + date_split[2] + "/" + date_split[0])
        ws.write(start_row_idx+i,7,obs['obs_name'])
        ws.write(start_row_idx+i,8,obs['fishcollectionmethod'])
        ws.write(start_row_idx+i,9,obs['species'])
        ws.write(start_row_idx+i,10,obs['lifestage'])
        ws.write(start_row_idx+i,11,obs['length'])
        ws.write(start_row_idx+i,12,obs['lengthmethod'])
        ws.write(start_row_idx+i,13,obs['weight'])
        ws.write(start_row_idx+i,14,obs['sex'])
        ws.write(start_row_idx+i,15,obs['age'])
        ws.write(start_row_idx+i,16,obs['agemethod'])
        ws.write(start_row_idx+i,17,obs['gcl'])
        ws.write(start_row_idx+i,18,obs['add_cnt1'])
        ws.write(start_row_idx+i,19,obs['disp1'])
        ws.write(start_row_idx+i,20,obs['add_cnt2'])
        ws.write(start_row_idx+i,21,obs['disp2'])
        ws.write(start_row_idx+i,22,obs['comments'])

        
    wb.save(content)

    final = content.getvalue() 
    content.close()
    return final


def get_obs_pdf(pi, username):

    import xhtml2pdf.pisa as pisa
    import cStringIO as StringIO

    DEFAULT_ZOOM = 12
    OVERVIEW_ZOOM = 8
    MAX_ZOOM = 15
    DEFAULT_WIDTH = 400
    DEFAULT_HEIGHT = 300

    points = {
      'lat': pi.lat,            #TODO get observation point if available
      'lng': pi.lng,
      'start_lat': None,
      'start_lng': None,
      'end_lat': None,
      'end_lng': None
    }

    photo_file = None
    photo_location = None

    comment = ''

    pi_dict = pi.to_dict()
    data_dict = pi.data_dictionary

    rows = ""
    for key in sorted(pi_dict.keys()):
        if key in settings.IGNORED_OUTPUT_FIELDS:
            continue
        val = pi_dict[key]
        if key == settings.FRP_LOCATION_KEY:
            val_lst = val.split()
            points['lat'] = float(val_lst[0])
            points['lng'] = float(val_lst[1])
        if key == settings.AWC_START_POINT_KEY:
            val_lst = val.split()
            points['start_lat'] = float(val_lst[0])
            points['start_lng'] = float(val_lst[1])
        if key == settings.AWC_END_POINT_KEY:
            val_lst = val.split()
            points['end_lat'] = float(val_lst[0])
            points['end_lng'] = float(val_lst[1])
        label = data_dict.get_label(key)
        rows += """
                <tr>
                   <th>%s</th>
                   <td align="left">%s</td>
                </tr>
        """ % (label, val)
        if key == settings.PHOTO_KEY:
            photo_file = str(val)
            photo_location = 'file://127.0.0.1/usr/local/apps/formhub/media/' + username + '/attachments/' + photo_file
        if key == settings.COMMENT_KEY:
            comment = val


    bbox = get_bounding_box([[points['lat'],points['lng']],[points['start_lat'],points['start_lng']],[points['end_lat'],points['end_lng']]])

    if bbox:
        zoom, center = get_zoom_center(bbox, DEFAULT_WIDTH, DEFAULT_HEIGHT)
        if zoom == False:
            zoom = MAX_ZOOM
        if zoom > 2:
            if zoom > MAX_ZOOM:
                zoom = MAX_ZOOM
            else:
                zoom = int(zoom - 1)
        else:
            zoom = 2
    else:
        zoom = DEFAULT_ZOOM
        center = {
            'lat': point('lat'),
            'lng': point('lng')
        }

    # According to https://developers.google.com/maps/documentation/staticmaps/#api_key
    # "Note that the use of a key is not required, though it is recommended."
    # ... so we go without a key for simplicity
    map_template = "http://maps.googleapis.com/maps/api/staticmap?center=" + str(center['lat']) + "," + str(center['lng']) + "&" \
              "maptype=terrain" \
              "&markers=color:red%%7C%(start_lat)f,%(start_lng)f%%7C%(end_lat)f,%(end_lng)f&sensor=false" 
    detail_map = map_template % points + "&zoom=" + str(zoom) + "&size=" + str(DEFAULT_WIDTH) + "x" + str(DEFAULT_HEIGHT) #+ "&scale=2"
    if zoom - 2 <= OVERVIEW_ZOOM:
        if zoom > 4:
            overzoom = zoom - 3
        else:
            overzoom = 2
    else:
        overzoom = OVERVIEW_ZOOM
    overview_map = map_template % points + "&zoom=" + str(overzoom) + "&size=" + str(DEFAULT_WIDTH) + "x" + str(DEFAULT_HEIGHT) #+ "&scale=2"

    if photo_file and photo_location:
        photo_html = """
        <br>
        <p> %s </p>
        <img src='%s' style='height:200px;'/>

        """ % (photo_file, photo_location)
    else:
        photo_html = ""

    html = """
    <!-- EWWW table based layout (plays nicer with pisa) -->
    <style>
      td {text-align: left; vertical-align:top}
      th {text-align: right; margin-right:20px}
    </style>

    <table>
      <tr>
        <td align="center" colspan="2">
           <h2> Observation Summary </h2>
           <br>
        </td>
      </tr>
      <tr>
        <td>
            <p> Observation Detail </p>
            <table>
            %s
            </table>
        </td>
        <td>
            <p> Detail Map </p>
            <img src="%s">  
            <br>
            <p> Overview Map </p>
            <img src="%s">  
            %s
        </td>
      </tr>
    </table>

    """ % (rows, detail_map, overview_map, photo_html)

    result = StringIO.StringIO()
    pdf = pisa.CreatePDF(html, result)
    
    if pdf.err:
        raise Exception("Pisa failed to create a pdf for observation")
    else:
        obs_pdf = PdfFileReader(result)
        obs_page = obs_pdf.getPage(0)
        return obs_page, comment

def get_bounding_box(points):
    y_vals = []
    x_vals = []

    for point in points:
        if point[0] != None and point[1] != None:
            y_vals.append(point[0])
            if point[1] > 0:
                point[1] = point[1] - 360
            x_vals.append(point[1])

    bbox = {
        'sw': {
            'lat': min(y_vals),
            'lng': min(x_vals)
        },
        'ne': {
            'lat': max(y_vals),
            'lng': max(x_vals)
        }
    }

    return bbox

def get_zoom_center(bbox, width, height):
    import numpy        #TODO - use math instead

    sw_x, sw_y = latLonToMeters(bbox['sw']['lat'], bbox['sw']['lng'])
    sw_point = {
        'lat': sw_y,
        'lng': sw_x
    }
    ne_x, ne_y = latLonToMeters(bbox['sw']['lat'], bbox['ne']['lng'])
    ne_point = {
        'lat': ne_y,
        'lng': ne_x
    }

    center = {
        'lat': numpy.mean([bbox['sw']['lat'], bbox['ne']['lat']]),
        'lng': numpy.mean([bbox['sw']['lng'], bbox['ne']['lng']])
    }

    if center['lng'] < -180:
        center['lng'] = center['lng'] + 360

    x_range = abs(ne_point['lng']-sw_point['lng'])
    y_range = abs(ne_point['lat']-sw_point['lat'])
    ratio = max(x_range/width, y_range/height)
    zoom = get_zoom(center['lat'], ratio)

    return zoom, center

def get_zoom(lat, ratio):
    import numpy        #TODO - use math instead
    EARTH_CIRC = 6372798.2          # 6372.7982 km
    rad_lat = numpy.radians(lat)
    if ratio != 0 and EARTH_CIRC * numpy.cos(lat) != 0:
        zoom = numpy.log2((EARTH_CIRC * numpy.cos(rad_lat))/ratio)-5
    else:
        return False 
    return round(zoom)
    

# The below was taken from globalMapTiles.py:

###############################################################################
# $Id$
#
# Project:  GDAL2Tiles, Google Summer of Code 2007 & 2008
#           Global Map Tiles Classes
# Purpose:  Convert a raster into TMS tiles, create KML SuperOverlay EPSG:4326,
#           generate a simple HTML viewers based on Google Maps and OpenLayers
# Author:   Klokan Petr Pridal, klokan at klokan dot cz
# Web:      http://www.klokan.cz/projects/gdal2tiles/
#
###############################################################################
# Copyright (c) 2008 Klokan Petr Pridal. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
###############################################################################


def latLonToMeters( lat, lon ):
        "Converts given lat/lon in WGS84 Datum to XY in Spherical Mercator EPSG:900913"
        import math
        originShift = 2 * math.pi * 6378137 / 2.0

        mx = lon * originShift / 180.0
        my = math.log( math.tan((90 + lat) * math.pi / 360.0 )) / (math.pi / 180.0)

        my = my * originShift / 180.0
        return mx, my