##Script to prepare data for pollination analyses
##Before running, you must have the NLCD and CDL rasters for your year(s) of analysis and the states raster in one folder

# Import modules, reset environments
import arcpy
arcpy.CheckOutExtension("spatial")
arcpy.ResetEnvironments()

import tkFileDialog

# Select geodatabase where input datasets (NLCD, CDL, and state rasters) are stored
inputFolder = tkFileDialog.askdirectory(initialdir="/", title='Please select the geodatabase where the NLCD, CDL, and state rasters are stored.')

#Set input folder as working directory
arcpy.env.workspace = inputFolder

# Set years of analysis
years = raw_input("Enter years of analysis separated by spaces:")
years_list = years.split()

#Get states dataset
states = inputFolder+"/studystates"

#Loop rest of processing through each year of analysis
for year in years_list:
    # Set input datasets
    rawCDL = inputFolder+"/CDL_" + year
    rawNLCD = inputFolder+"/NLCD_" + year

    #Resample NLCD to 56 m, using states as snap raster
    arcpy.env.snapRaster = states
    NLCD = arcpy.Resample_management(rawNLCD, "NLCD_56m_" + year, 56, "MAJORITY")

    #Resample CDL to 56 m, using states as snap raster
    arcpy.env.snapRaster = states
    CDL = arcpy.Resample_management(rawCDL, "CDL_56m_" + year, 56, "MAJORITY")

   
