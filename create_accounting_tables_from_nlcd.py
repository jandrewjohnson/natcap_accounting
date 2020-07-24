import calc_change_in_lulc_by_subwatersheds
import hazelbean as hb

if __name__=='__main__':
    nlcd_lulc_folder = 'C:/bulk_data/nlcd'
    nlcd_lulc_uris = [
        'C:/bulk_data/nlcd\\nlcd_2001_landcover_2011_edition_2014_10_10\\nlcd_2001_landcover_2011_edition_2014_10_10_compressed.tif',
        'C:/bulk_data/nlcd\\nlcd_2006_landcover_2011_edition_2014_10_10\\nlcd_2006_landcover_2011_edition_2014_10_10_compressed.tif',
        'C:/bulk_data/nlcd\\nlcd_2011_landcover_2011_edition_2014_10_10\\nlcd_2011_landcover_2011_edition_2014_10_10_compressed.tif',
    ]

    values_that_might_exist = list(hb.config.nlcd_category_names.keys())
    run_dir = hb.make_run_dir()
    layer_names = [2001, 2006, 2011]
    input_shapefile_uri = "c:\\onedrive\\projects\\base_data\\cartographic\\us\\cb_2015_us_county_500k_nad83.shp"

    calc_change_in_lulc_by_subwatersheds.count_unique_values_by_shape_for_uris_list(nlcd_lulc_uris, layer_names, input_shapefile_uri, run_dir, 'GEOID', values_that_might_exist)


