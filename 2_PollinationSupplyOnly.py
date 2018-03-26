##Script to run supply-only pollination analysis
##Before running this script, you must run script 1_PollinationDataProcessing

# Import modules, reset environments
import arcpy
arcpy.CheckOutExtension("spatial")
arcpy.ResetEnvironments()

import tkFileDialog

# Select gepdatabase where input datasets (NLCD, CDL, and state rasters) are stored
inputFolder = tkFileDialog.askdirectory(initialdir="/", title='Please select the geodatabase where the NLCD, CDL, and state rasters are stored.')

#Set input folder as working directory
arcpy.env.workspace = inputFolder

# Set years of analysis
years = raw_input("Enter years of analysis separated by spaces:")
years_list = years.split()

#Get states dataset
states = inputFolder+"/studystates"

#Set output folder (where results will be stored)
outputFolder = tkFileDialog.askdirectory(initialdir="/", title='Please select the directory where output files should be saved.')

#Loop rest of processing through each year of analysis
for year in years_list:
    # Set input datasets
    if arcpy.Exists("NLCD_56m_" + year):
        NLCD = inputFolder + "/" "NLCD_56m_" + year
    else:
        raise Exception('NLCD dataset does not exist.  Run script 1 to create it.')

    # Extract NLCD classes that provide pollinator habitat 
    PollHab = arcpy.sa.Con(NLCD, "1", "0", "VALUE IN (41, 42, 43, 52, 71, 90, 95)")
    output = outputFolder+"/"+year+"_TotalPollHab.tif"
    PollHab.save(output)
    PollHab = outputFolder+"/"+year+"_TotalPollHab.tif"

    ##Currently an issue with the next part, leaving for now and will fix later
    #Count # of pixels in each state, NLCD class, and pollinator habitat status
    #output = outputFolder+"/"+year+"_TotPH_combo.tif"
    #Combo = arcpy.sa.Combine([PollHab, NLCD, states])
    #Combo.save(output)