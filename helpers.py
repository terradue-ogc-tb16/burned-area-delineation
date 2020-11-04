from pystac import *
import gdal 
import os
import numpy as np
from urllib.parse import urlparse

gdal.UseExceptions()

def set_env():
    
    if not 'PREFIX' in os.environ.keys():
    
        os.environ['PREFIX'] = '/opt/anaconda/envs/env_vi'

        os.environ['GDAL_DATA'] =  os.path.join(os.environ['PREFIX'], 'share/gdal')
        os.environ['PROJ_LIB'] = os.path.join(os.environ['PREFIX'], 'share/proj')

def get_item(catalog):
    
    cat = Catalog.from_file(catalog) 
    
    try:
        
        collection = next(cat.get_children())
        item = next(collection.get_items())
        
    except StopIteration:

        item = next(cat.get_items())
        
    return item

def get_assets(item):
    
    asset_ndvi, asset_ndwi, asset_nbr = None, None, None
    
    eo_item = extensions.eo.EOItemExt(item)
    
    for index, band in enumerate(eo_item.bands):
   
        if band.common_name in ['ndvi']:

            asset_ndvi = item.assets[band.name].get_absolute_href()

        if band.common_name in ['ndwi']:

            asset_ndwi = item.assets[band.name].get_absolute_href()

        if band.common_name in ['nbr']:

            asset_nbr = item.assets[band.name].get_absolute_href()
        
    return asset_ndvi, asset_ndwi, asset_nbr
   

def cog(input_tif, output_tif,no_data=None):
    
    translate_options = gdal.TranslateOptions(gdal.ParseCommandLine('-co TILED=YES ' \
                                                                    '-co COPY_SRC_OVERVIEWS=YES ' \
                                                                    '-co COMPRESS=DEFLATE '))
    
    if no_data != None:
        translate_options = gdal.TranslateOptions(gdal.ParseCommandLine('-co TILED=YES ' \
                                                                        '-co COPY_SRC_OVERVIEWS=YES ' \
                                                                        '-co COMPRESS=DEFLATE '\
                                                                        '-a_nodata {}'.format(no_data)))
    ds = gdal.Open(input_tif, gdal.OF_READONLY)

    gdal.SetConfigOption('COMPRESS_OVERVIEW', 'DEFLATE')
    ds.BuildOverviews('NEAREST', [2,4,8,16,32])
    
    ds = None

    del(ds)
    
    ds = gdal.Open(input_tif)
    gdal.Translate(output_tif,
                   ds, 
                   options=translate_options)
    ds = None

    del(ds)
    
    os.remove('{}.ovr'.format(input_tif))
    os.remove(input_tif)
    
def get_gdal_asset_path(url):
    
    username = os.environ.get('STAGEIN_USERNAME')
    password = os.environ.get('STAGEIN_PASSWORD')
    
    parsed = urlparse(url)
    
    if parsed.scheme.startswith('http'):
        
        return get_vsi_url(url, username, password)
    
    else:
    
        return url
    
def get_vsi_url(url, username=None, password=None):
    
    
    parsed_url = urlparse(url)

    if username is not None:
        
        url = '/vsicurl/{}://{}:{}@{}/{}'.format(list(parsed_url)[0],
                                                username, 
                                                password, 
                                                list(parsed_url)[1],
                                                list(parsed_url)[2])
    
    else:
        
        url = '/vsicurl/{}://{}/{}'.format(list(parsed_url)[0],
                                              list(parsed_url)[1],
                                              list(parsed_url)[2])
    
    return url