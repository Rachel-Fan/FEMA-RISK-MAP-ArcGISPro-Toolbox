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

def check_extention():
    try:
        if arcpy.CheckExtension("Spatial") == "Available":
            arcpy.CheckOutExtension("Spatial")
            print ("Checked out \"Spatial\" Extension")
        else:
            #raise LicenseError
            print ("Spatial Analyst license is unavailable")
    #except LicenseError:
        #print ("Spatial Analyst license is unavailable")
    except:
        print ("Exiting")

def set_environment(workspace, overwrite):
    arcpy.env.workspace = workspace
    arcpy.env.overwriteOutput = overwrite

def createDEMaboveWSE(DEM, WSE100, WSE500, DEMaboveWSERaster):         # WSE100 refers to more frequent flood event
    with arcpy.EnvManager(snapRaster=DEM, extent=WSE500, cellSize=DEM, mask=WSE500):
        output_raster = arcpy.sa.RasterCalculator(
            expression='Con((DEM  <=  WSE500)  &  (DEM  >  WSE100), Power(10.0, Log10(0.01)+(DEM - WSE100)*(Log10(0.002)-Log10(0.01))/(WSE500-WSE100)))'
        )
    output_raster.save(DEMaboveWSERaster)
    
    
def combineRaster(input_rasters, outputRaster, overlayStats):
    CellStatistics
def createPctAnnChance():
    (RoundDown("%PctAnn_tmp%" * 100.0 * 10.0 + 0.5) / 10.0)
    
def createPct30yrChance():
    (RoundDown((1.0 - Power(1.0 - "%PctAnn_tmp%", 30)) * 100.0 * 10.0 + 0.5) / 10.0 ) 
    
    
def main(outputGDB):
    check_extention()
    workspace = outputGDB
    set_environment(workspace, True)
    
    
if __name__ == "__main___":
    
    input_WSE_10pct
    input_WSE_04pct
    input_WSE_02pct  
    input_WSE_01pct
    input_WSE_0_2pct
    DEM
    outputGDB

    
    main(input_WSE_10pct,input_WSE_04pct,input_WSE_02pct ,input_WSE_01pct,input_WSE_0_2pct,DEM,outputGDB)
    print('Done')