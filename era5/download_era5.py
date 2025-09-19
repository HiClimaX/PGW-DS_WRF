#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  1 02:28:03 2024

@author: doan
"""

import cdsapi
import os #add by yuasa at 2025/2/12


# Download ERA5 pressure-level data for ungrib
def download_era5_for_ungrib(dir, area=[45, 130, 25, 150], fformat='netcdf', extension='nc'):
    # Initialize the CDS API client
    c = cdsapi.Client()

    c.retrieve(
        'reanalysis-era5-pressure-levels',
        {
            'product_type': 'reanalysis',
            'format': fformat,  # Format required for ungrib
            'variable': [
                'geopotential',
                'relative_humidity',
                'temperature',
                'u_component_of_wind',
                'v_component_of_wind',
            ],
            'pressure_level': [
                '1', '2', '3',
                '5', '7', '10',
                '20', '30', '50',
                '70', '100', '125',
                '150', '175', '200',
                '225', '250', '300',
                '350', '400', '450',
                '500', '550', '600',
                '650', '700', '750',
                '775', '800', '825',
                '850', '875', '900',
                '925', '950', '975',
                '1000',
            ],
            'year': '2023',
            'month': '01',
            'day': '01',
            'time': [
                '00:00', '06:00', '12:00', '18:00',
            ],
            'area': area ,
        },
        os.path.join(dir, 'era5_ungrib_pressure_levels_20230101.'+extension) # Output file name. fix by yuasa at 2025/2/12
    )  

    # Download ERA5 surface-level data for ungrib
    c.retrieve(
        'reanalysis-era5-single-levels',
        {
            'product_type': 'reanalysis',
            'format': fformat,  # Format required for ungrib
            'variable': [
                '10m_u_component_of_wind',
                '10m_v_component_of_wind',
                '2m_dewpoint_temperature',
                '2m_temperature',
                'land_sea_mask',
                'mean_sea_level_pressure',
                'sea_ice_cover',
                'sea_surface_temperature',
                'skin_temperature',
                'snow_depth',
                'soil_temperature_level_1',
                'soil_temperature_level_2',
                'soil_temperature_level_3',
                'soil_temperature_level_4',
                'surface_pressure',
                'volumetric_soil_water_layer_1',
                'volumetric_soil_water_layer_2',
                'volumetric_soil_water_layer_3',
                'volumetric_soil_water_layer_4',
            ],
            'year': '2023',
            'month': '01',
            'day': '01',
            'time': [
                '00:00', '06:00', '12:00', '18:00',
            ],
            'area': area ,
        },
        os.path.join(dir, 'era5_ungrib_surface_levels_20230101.'+extension)  # Output file name. fix by yuasa at 2025/2/12
    )

if __name__ == '__main__':
    
    fformat = 'grib'
    extension = 'grib'
    
    area =  [45, 130, 25, 150]   # North, West, South, East (in degrees)
    
    download_dir = './' #add by yuasa at 2025/2/12
    download_era5_for_ungrib(download_dir, area, fformat, extension)