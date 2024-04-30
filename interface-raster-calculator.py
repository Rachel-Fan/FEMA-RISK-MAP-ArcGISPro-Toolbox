import arcpy
import arcpy.sa as sa
import os
from datetime import datetime, timedelta
import sys
import traceback

import re
import csv
import time
import pandas as pd
from arcpy.sa import *

# Check if the Spatial Analyst extension is available
def check_extension():
    try:
        if arcpy.CheckExtension("Spatial") == "Available":
            arcpy.CheckOutExtension("Spatial")
            print("Checked out 'Spatial' Extension")
        else:
            print("Spatial Analyst license is unavailable")
            sys.exit()
    except Exception as e:
        print("Error checking out Spatial Analyst license: ", e)
        sys.exit()

check_extension()
print('start!')

 
merge_terain_Clip = sa.Raster(arcpy.GetParameterAsText(0))
FY19_WSE_100YR_clip = sa.Raster(arcpy.GetParameterAsText(1))
FY19_WSE_500YR_clip = sa.Raster(arcpy.GetParameterAsText(2))

# Set environment settings
arcpy.env.snapRaster = merge_terain_Clip
arcpy.env.cellSize = merge_terain_Clip
arcpy.env.mask = FY19_WSE_500YR_clip

# Calculate the expression using arcpy.sa functions
cond_result = sa.Con((merge_terain_Clip <= FY19_WSE_500YR_clip) & (merge_terain_Clip > FY19_WSE_100YR_clip),
                     sa.Power(10.0, sa.Log10(0.01) + (merge_terain_Clip - FY19_WSE_100YR_clip) *
                              (sa.Log10(0.002) - sa.Log10(0.01)) / (FY19_WSE_500YR_clip - FY19_WSE_100YR_clip)))

# Save the output
output_raster_path = r"C:\Users\rfan\Documents\ArcGIS\Tools\FRD_DAGs\Clip_Data_test\ToolTest.gdb\DEM_above_01PCT_standalone"
cond_result.save(output_raster_path)

print('Output raster is saved at', output_raster_path)