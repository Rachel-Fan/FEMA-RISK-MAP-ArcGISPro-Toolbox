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
def create_dem_above_wse(dem, more_frequent_wse, less_frequent_wse, output_raster_name):
    # Ensure all inputs are Raster objects
    dem_raster = sa.Raster(dem)
    more_frequent_wse_raster = sa.Raster(more_frequent_wse)
    less_frequent_wse_raster = sa.Raster(less_frequent_wse)

    # Perform conditional operation using arcpy.sa
    result_raster = sa.Con((dem_raster <= less_frequent_wse_raster) & (dem_raster > more_frequent_wse_raster),
                           sa.Power(10.0, sa.Log10(0.01) + (dem_raster - more_frequent_wse_raster) * 
                           (sa.Log10(0.002) - sa.Log10(0.01)) / (less_frequent_wse_raster - more_frequent_wse_raster)))

    # Save the result
    result_raster.save(output_raster_name)
    return output_raster_name

# Combine the output rasters into a single raster using Cell Statistics
def combine_raster(input_rasters, output_combined_raster):
    combined_raster = sa.CellStatistics(input_rasters, "SUM")
    combined_raster.save(output_combined_raster)
    return output_combined_raster

# Create Percentage Annual Chance Raster
def create_pct_ann_chance(input_raster, output_raster_name):
    expression = 'RoundDown({} * 100.0 * 10.0 + 0.5) / 10.0'.format(input_raster)
    pct_ann_chance = sa.RasterCalculator(expression)
    pct_ann_chance.save(output_raster_name)

# Create Percentage 30-year Chance Raster
def create_pct_30yr_chance(input_raster, output_raster_name):
    expression = 'RoundDown((1.0 - Power(1.0 - {}, 30)) * 100.0 * 10.0 + 0.5) / 10.0'.format(input_raster)
    pct_30yr_chance = sa.RasterCalculator(expression)
    pct_30yr_chance.save(output_raster_name)

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
    wse_list = [sa.Raster(arcpy.GetParameterAsText(i)) for i in range(2, 7)]  # Assuming 5 WSE inputs
    output_gdb = arcpy.GetParameterAsText(7)
    
    arcpy.AddMessage(dem)
    main(workspace, dem, wse_list, output_gdb)
    arcpy.AddMessage("Done")

