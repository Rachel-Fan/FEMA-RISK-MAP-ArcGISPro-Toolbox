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

# Set the working environment
def set_environment(workspace, overwrite, snap_raster, extent, cell_size):
    arcpy.env.workspace = workspace
    arcpy.env.overwriteOutput = overwrite
    arcpy.env.snapRaster = snap_raster
    arcpy.env.extent = extent
    arcpy.env.cellSize = cell_size

# Calculate DEM above different Water Surface Elevations (WSE)
def create_dem_above_01PCT(dem, WSE_100YR, WSE_500YR, dem_above_01PCT):
    # Ensure all inputs are Raster objects
    dem_raster = sa.Raster(dem)
    WSE_100YR_raster = sa.Raster(WSE_100YR)
    WSE_500YR_raster = sa.Raster(WSE_500YR)

    # Perform conditional operation using arcpy.sa
    result_raster = sa.Con((dem_raster <= WSE_500YR_raster) & (dem_raster > WSE_100YR_raster),
                           sa.Power(10.0, sa.Log10(0.01) + (dem_raster - WSE_100YR_raster) * 
                           (sa.Log10(0.002) - sa.Log10(0.01)) / (WSE_500YR_raster - WSE_100YR_raster)))

    # Save the result
    result_raster.save(dem_above_01PCT)
    return dem_above_01PCT

# Calculate DEM above different Water Surface Elevations (WSE)
def create_dem_above_02PCT(dem, WSE_50YR, WSE_100YR, dem_above_02PCT):
    # Ensure all inputs are Raster objects
    dem_raster = sa.Raster(dem)
    WSE_50YR_raster = sa.Raster(WSE_50YR)
    WSE_100YR_raster = sa.Raster(WSE_100YR)

    # Perform conditional operation using arcpy.sa
    result_raster = sa.Con((dem_raster <= WSE_100YR_raster) & (dem_raster > WSE_50YR_raster),
                           sa.Power(10.0, sa.Log10(0.02) + (dem_raster - WSE_50YR_raster) * 
                           (sa.Log10(0.01) - sa.Log10(0.02)) / (WSE_100YR_raster - WSE_50YR_raster)))

    # Save the result
    result_raster.save(dem_above_02PCT)
    return dem_above_02PCT

# Calculate DEM above different Water Surface Elevations (WSE)
def create_dem_above_04PCT(dem, WSE_25YR, WSE_50YR, dem_above_04PCT):
    # Ensure all inputs are Raster objects
    dem_raster = sa.Raster(dem)
    WSE_25YR_raster = sa.Raster(WSE_25YR)
    WSE_50YR_raster = sa.Raster(WSE_50YR)

    # Perform conditional operation using arcpy.sa
    result_raster = sa.Con((dem_raster <= WSE_50YR_raster) & (dem_raster > WSE_25YR_raster),
                           sa.Power(10.0, sa.Log10(0.04) + (dem_raster - WSE_25YR_raster) * 
                           (sa.Log10(0.02) - sa.Log10(0.04)) / (WSE_50YR_raster - WSE_25YR_raster)))

    # Save the result
    result_raster.save(dem_above_04PCT)
    return dem_above_04PCT

# Calculate DEM above different Water Surface Elevations (WSE)
def create_dem_above_10PCT(dem, WSE_10YR, WSE_25YR, dem_above_10PCT):
    # Ensure all inputs are Raster objects
    dem_raster = sa.Raster(dem)
    WSE_10YR_raster = sa.Raster(WSE_10YR)
    WSE_25YR_raster = sa.Raster(WSE_25YR)

    # Perform conditional operation using arcpy.sa
    result_raster = sa.Con((dem_raster <= WSE_25YR_raster) & (dem_raster > WSE_10YR_raster),
                           sa.Power(10.0, sa.Log10(0.10) + (dem_raster - WSE_10YR_raster) * 
                           (sa.Log10(0.04) - sa.Log10(0.10)) / (WSE_25YR_raster - WSE_10YR_raster)))

    # Save the result
    result_raster.save(dem_above_10PCT)
    return dem_above_10PCT

# Calculate DEM above different Water Surface Elevations (WSE)
def create_dem_above_WSE(dem, WSE_10YR, dem_above_WSE):
    # Ensure all inputs are Raster objects
    dem_raster = sa.Raster(dem)
    WSE_10YR_raster = sa.Raster(WSE_10YR)
    
    # Perform conditional operation using arcpy.sa
    result_raster = sa.Con(dem_raster <= WSE_10YR_raster, 0.10 )

    # Save the result
    result_raster.save(dem_above_WSE)
    return dem_above_WSE

# Combine the output rasters into a single raster using Cell Statistics
def combine_raster(input_rasters, output_combined_raster):
    combined_raster = sa.CellStatistics(input_rasters, "SUM")
    combined_raster.save(output_combined_raster)
    return output_combined_raster

# Create Percentage Annual Chance Raster
def create_pct_ann_chance(input_raster, output_raster_name):
    # Ensure input is a Raster object
    input_raster_obj = sa.Raster(input_raster)
    
    # Calculate the percentage annual chance
    pct_ann_chance = sa.RoundDown(input_raster_obj * 1000.0 + 0.5) / 10.0
    
    # Save the result
    pct_ann_chance.save(output_raster_name)
    return output_raster_name


# Create Percentage 30-year Chance Raster
def create_pct_30yr_chance(input_raster, output_raster_name):
    # Ensure input is a Raster object
    input_raster_obj = sa.Raster(input_raster)
    
    # Calculate the 30-year chance
    pct_30yr_chance = sa.RoundDown((1.0 - sa.Power(1.0 - input_raster_obj, 30)) * 1000.0 + 0.5) / 10.0
    
    # Save the result
    pct_30yr_chance.save(output_raster_name)
    return output_raster_name


# Main function
def main(workspace, dem, wse_list, output_gdb):
    check_extension()
    set_environment(workspace, True, dem, wse_list[-1], dem)  # Setting environment with the least frequent WSE as extent

    output_rasters = []
    for i in range(len(wse_list)-1):
        output_raster_name = os.path.join(output_gdb, f"DEMaboveWSE_{i}")
        output_rasters.append(create_dem_above_wse(dem, wse_list[i], wse_list[i+1], output_raster_name))

    combined_raster_name = os.path.join(output_gdb, "combined_raster")
    temp_raster = combine_raster(output_rasters, combined_raster_name)

    pct_ann_chance_raster = os.path.join(output_gdb, "PctAnnChance")
    create_pct_ann_chance(temp_raster, pct_ann_chance_raster)

    pct_30yr_chance_raster = os.path.join(output_gdb, "Pct30yrChance")
    create_pct_30yr_chance(temp_raster, pct_30yr_chance_raster)
    print('Processing completed.')

# Command-line interface
if __name__ == "__main__":
    arcpy.AddMessage("Starting processing...")
    workspace = arcpy.GetParameterAsText(0)
    dem = sa.Raster(arcpy.GetParameterAsText(1))
    WSE_10YR = sa.Raster(arcpy.GetParameterAsText(2))
    WSE_25YR = sa.Raster(arcpy.GetParameterAsText(3))
    WSE_50YR = sa.Raster(arcpy.GetParameterAsText(4))
    WSE_100YR = sa.Raster(arcpy.GetParameterAsText(5))
    WSE_500YR = sa.Raster(arcpy.GetParameterAsText(6))
    
    #wse_list = [sa.Raster(arcpy.GetParameterAsText(i)) for i in range(2, 7)]  # Assuming 5 WSE inputs
    output_gdb = arcpy.GetParameterAsText(7)
    
    arcpy.AddMessage(dem)
    main(workspace, dem, wse_list, output_gdb)
    arcpy.AddMessage("Done")

