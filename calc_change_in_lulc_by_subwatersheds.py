


import warnings
import numpy as np
import os, sys
from matplotlib import pyplot as plt
from ggplot import *
import pandas as pd
import geopandas as gpd
import rasterio
import shapely
import affine
import fiona
import numpy
from collections import OrderedDict
from pprint import pprint
import multiprocessing


import hazelbean as hb
def count_unique_values_by_shape(input_raster_uri, input_shapefile_uri, id_col, run_dir, values_that_might_exist):
    """
    Works for data larger than memory, but it does this by clipping and creating 1 shp and 1 raster for each polygon, which is super slow.
    However, it can be run massively parallel if needed, so theres that.
        
    :param input_raster_uri: uri path to lulc raster. Expects GDAL readable file format (eg .tif)
    :param input_shapefile_uri: uri path to a shapefile with polygons that define accounting units.
    :param id_col: A column in input_shapefile_uri that is a unique identifier of each accounting unit.
    :param run_dir: Directory to output results
    :param values_that_might_exist: List of integer values that could possibly exist in the dataset. This is required because if cerain classes exist in some years/regions
    but not others, the output will be misshapen.
    :return: 
    """


    counties_gdf = gpd.read_file(input_shapefile_uri)
    id_list = []
    output_odict = OrderedDict()
    counter = 0

    input_raster_basename = os.path.splitext(os.path.split(input_raster_uri)[1])[0]

    for entry in counties_gdf[id_col]:
        id_list.append(entry)
        county_shapefile_uri = os.path.join(run_dir, 'intermediate', input_raster_basename, entry + '_county.shp')
        hb.extract_features_in_shapefile_by_attribute(input_shapefile_uri, county_shapefile_uri, id_col, entry)
        county_raster_uri = os.path.join(run_dir, 'intermediate', input_raster_basename, entry + '_county.tif')

        try: # NOTE, horrible practice to have so much happen in a try block, but the problem was when analyzing a county that is not in the continental US, the clip failed for lack of overlap.
            hb.clip_dataset_uri(input_raster_uri, county_shapefile_uri, county_raster_uri)
            a = hb.as_array(county_raster_uri)
            counts = hb.enumerate_array_as_odict(a)

            # Add in all values that didn't exist as zero. this ensures dicts from multiple years match  even when they have different presence/absense
            for class_id in values_that_might_exist:
                if class_id not in counts:
                    counts[class_id] = 0

            # Sort so that added values arent after
            counts = OrderedDict(sorted(counts.items()))

        except:
            counts = OrderedDict()



        if entry is not None and counts is not None:
            output_odict[entry] = counts
        print('Processing county', counter, entry, counts)
        counter += 1


    output_uri = os.path.join(run_dir, input_raster_basename + '_classes.csv')

    hb.python_object_to_csv(output_odict, output_uri, '2d_odict')
    return output_odict

def count_unique_values_by_shape_for_uris_list(uris_list, layer_names, input_shapefile_uri, run_dir, id_col, values_that_might_exist):

    try:
        os.mkdir(os.path.join(run_dir, 'intermediate'))
    except:
        print('already exists.')

    for uri in uris_list:
        input_raster_basename = os.path.splitext(os.path.split(uri)[1])[0]
        try:
            os.mkdir(os.path.join(run_dir, 'intermediate', input_raster_basename))
        except:
            print('already exists.')


    jobs = []
    for i, uri in enumerate(uris_list):
        input_raster_uri = uri
        output_uri = os.path.join(run_dir, str(layer_names[i]) + '_classes.csv')
        p = multiprocessing.Process(target=count_unique_values_by_shape, args=(input_raster_uri, input_shapefile_uri, id_col, run_dir, values_that_might_exist))
        jobs.append(p)
        p.start()

    # Wait for all to finish
    for j in jobs:
        j.join()

    print('count_unique_values_by_shape_for_uris_list finshed!')


main = 'here'
if __name__=='__main__':
    # USAGE:
    # replace the input variables below with links to your data and input layer names. Will create polygon-level shapefiles and geotiffs for each polygon in the shapefile.
    # Results will be summarized into CSVs with names defined in layer_names.
    print('See, e.g., create_accounting_tables_from_nlcd.py for example usage.')
# nlcd_lulc_folder = 'C:/bulk_data/nlcd'
# nlcd_lulc_uris = [
#     'C:/bulk_data/nlcd\\nlcd_2001_landcover_2011_edition_2014_10_10\\nlcd_2001_landcover_2011_edition_2014_10_10_compressed.tif',
#     'C:/bulk_data/nlcd\\nlcd_2006_landcover_2011_edition_2014_10_10\\nlcd_2006_landcover_2011_edition_2014_10_10_compressed.tif',
#     'C:/bulk_data/nlcd\\nlcd_2011_landcover_2011_edition_2014_10_10\\nlcd_2011_landcover_2011_edition_2014_10_10_compressed.tif',
# ]
#
# values_that_might_exist = list(hb.config.nlcd_category_names.keys())
#
# run_dir = hb.make_run_dir()
# layer_names = [2001, 2006, 2011]
#
# input_shapefile_uri = "c:\\onedrive\\projects\\base_data\\cartographic\\us\\cb_2015_us_county_500k_nad83.shp"
#
# count_unique_values_by_shape_for_uris_list(nlcd_lulc_uris, layer_names, input_shapefile_uri, run_dir, 'GEOID', values_that_might_exist)
#
#
