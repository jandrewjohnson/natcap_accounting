##Script to run supply-demand pollination analysis
##Before running this script, you must run scripts 1_PollinationDataProcessing and 2_PollinationSupplyOnly

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

#Set output folder (where results will be saved and where results from script 2 were saved)
outputFolder = tkFileDialog.askdirectory(initialdir="/", title='Please select the directory where output files should be saved.  This must be the same folder used for the results of script 2')

#Loop rest of processing through each year of analysis
for year in years_list:
    # Set input datasets
    if arcpy.Exists("NLCD_56m_" + year):
        NLCD = inputFolder + "/NLCD_56m_" + year
    else:
        raise Exception('NLCD dataset does not exist.  Run script 1 to create it.')

    if arcpy.Exists("CDL_56m_" + year):
        CDL = inputFolder + "/CDL_56m_" + year
    else:
        raise Exception('CDL dataset does not exist.  Run script 1 to create it.')

    arcpy.env.workspace = outputFolder
    if arcpy.Exists(outputFolder+"/"+year+"_TotalPollHab.tif"):
        TotPollHab = outputFolder+"/"+year+"_TotalPollHab.tif"
    else:
        raise Exception('Pollinator habitat dataset does not exist.  Run script 2 to create it.')

    #Create geodatabase to store intermediate datasets
    if arcpy.Exists(outputFolder + "/" + year + "SupplyDemandAnalysis.gdb") == False:
        arcpy.CreateFileGDB_management(outputFolder, year+"SupplyDemandAnalysis.gdb")
    arcpy.env.workspace = outputFolder + "/" + year + "SupplyDemandAnalysis.gdb"

    # Step 1: Identify pollinator-dependent crops in the study area
    # Reclassify CDL into directly pollinator-dependent crops (=1), all other classes (=NODATA) 
    output = "CropReclass"
    remap = arcpy.sa.RemapValue([[0,"NODATA"],[5,1],[6,1],[242,1], [250, 1], [221, 1], [72, 1], [212, 1], [50, 1], [209, 1], [213, 1],
                             [229, 1], [222, 1], [48, 1], [69, 1], [10, 1], [239, 1], [240, 1], [241, 1], [254, 1], [26, 1], [75, 1], [34, 1], [68, 1], [223, 1],
                             [66, 1], [218, 1], [211, 1], [67, 1], [77, 1], [220, 1], [210, 1]])
    Reclass = arcpy.sa.Reclassify(CDL, "Value", remap, "NODATA")
    Reclass.save(output)

    # Region Group reclassified crop layer to identify patches greater than 12 pixels
    RG_output = "RegionGroup"
    RG = arcpy.sa.RegionGroup(Reclass, "EIGHT", "CROSS", "ADD_LINK", "0")
    RG.save(RG_output)
    cutoff = "13"
    Con_output = "CropPatch"
    whereClause = "COUNT >= %s AND VALUE > 0" %cutoff
    CropPatch = arcpy.sa.Con(RG, "1", "", whereClause)
    CropPatch.save(Con_output)

    #Use resulting layer as a mask to extract the reclassified cropland layer (to exclude patches < 10 acres)Extract by Mask
    output = "FinalCrop"
    FinalCrop = arcpy.sa.ExtractByMask(Reclass, CropPatch)
    FinalCrop.save(output)

    # Step 2: Create pollinator range "buffer" around pollinator-dependent crops
    # Create a mask of areas within pollinator distance of pollinator-dependent crops
    output = "EucDist"
    EucDist = arcpy.sa.EucDistance(FinalCrop, 1308, 56)
    EucDist.save(output)

    # Create a mask of areas within pollinator distance of pollinator-dependent crops, excluding the crops themselves
    output = "PollDistMask"
    PollDistMask = arcpy.sa.Con(EucDist, "1", "", "Value > 0")
    PollDistMask.save(output)

    # Extract potential pollinator habitat that is within pollinator distance of PDCs
    arcpy.env.snapRaster = TotPollHab
    output = outputFolder+"/"+year+"PDCPollHab.tif"
    PDCPollHab = arcpy.sa.ExtractByMask(TotPollHab, PollDistMask)
    PDCPollHab.save(output)

    #Reset workspace to input folder
    arcpy.env.workspace = inputFolder
