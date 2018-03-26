## Script to create supply-only and supply-demand capacity tables for pollination potential
## Before running this script, you must run scripts 1_PollinationDataProcessing, 2_PollinationSupplyOnly, and 3_PollinationSupplyDemand

# Import modules, reset environments
import arcpy
arcpy.CheckOutExtension("spatial")
arcpy.ResetEnvironments()

import tkFileDialog
import csv


# Set years of analysis
years = raw_input("Enter years of analysis separated by spaces:")
years_list = years.split()

# Select geodatabase where the state and NLCD rasters are stored
inputFolder = tkFileDialog.askdirectory(initialdir="/", title='Please select the geodatabase where the state and NLCD rasters are stored.')

# Set state dataset
states = inputFolder+"/studystates"

# Select directory where results from scripts 2 and 3 are saved
outputFolder = tkFileDialog.askdirectory(initialdir="/", title='Please select the directory where the results of scripts 2 and 3 are saved.')

#Set output folder as working directory
arcpy.env.workspace = outputFolder

#Loop rest of processing through each year of analysis
for year in years_list:
    # Set input datasets
    if arcpy.Exists(outputFolder+"/"+year+"_TotalPollHab.tif"):
        TotPollHab = outputFolder+"/"+year+"_TotalPollHab.tif"
    else:
        raise Exception('Pollinator habitat dataset does not exist.  Run script 2 to create it.')

    if arcpy.Exists(outputFolder+"/"+year+"PDCPollHab.tif"):
        PDCPollHab = outputFolder+"/"+year+"PDCPollHab.tif"
    else:
        raise Exception('PDC pollinator habitat dataset does not exist.  Run script 3 to create it.')

    if arcpy.Exists(inputFolder + "/NLCD_56m_" + year):
        NLCD = inputFolder + "/NLCD_56m_" + year
    else:
        raise Exception('NLCD dataset does not exist.  Run script 1 to create it.')

    #Get count of TotPollHab pixels by state and NLCD class
    arcpy.env.snapRaster = TotPollHab
    output = "TotPH_NLCD_state_" + year + ".tif"
    Combo = arcpy.sa.Combine([TotPollHab, NLCD, states])
    Combo.save(output)

    #Write result to csv
    rat = outputFolder + "/" + "TotPH_NLCD_state_" + year + ".tif"
    csv_out = outputFolder + "/" + "TotPH_NLCD_state_" + year + ".csv"
    fields = arcpy.ListFields(rat)
    field_Names = [field.name for field in fields]
    with open(csv_out, 'wb') as f:
        w = csv.writer(f)
        w.writerow(field_Names)
        for row in arcpy.SearchCursor(output):
            field_vals = [row.getValue(field.name) for field in fields]
            w.writerow(field_vals)
        del row

    #Get count of PDCPollHab pixels by state and NLCD class
    output = "PDCPH_NLCD_state_" + year + ".tif"
    Combo = arcpy.sa.Combine([PDCPollHab, NLCD, states])
    Combo.save(output)

    #Write result to csv
    rat = outputFolder + "/" + "PDCPH_NLCD_state_" + year + ".tif"
    csv_out = outputFolder + "/" + "PDCPH_NLCD_state_" + year + ".csv"
    fields = arcpy.ListFields(rat)
    field_Names = [field.name for field in fields]
    with open(csv_out, 'wb') as f:
        w = csv.writer(f)
        w.writerow(field_Names)
        for row in arcpy.SearchCursor(output):
            field_vals = [row.getValue(field.name) for field in fields]
            w.writerow(field_vals)
        del row
