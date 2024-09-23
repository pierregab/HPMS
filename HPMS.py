#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from astroquery.utils.tap.core import TapPlus
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from astropy import units as u
from astropy.units import UnitTypeError
from astropy.time import Time
from astroplan import Observer
import datetime
import warnings
import argparse
import sys
import os
import pickle

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# ASCII Art to be displayed in the header
ASCII_ART = r"""
 /$$   /$$ /$$$$$$$  /$$      /$$  /$$$$$$ 
| $$  | $$| $$__  $$| $$$    /$$$ /$$__  $$
| $$  | $$| $$  \ $$| $$$$  /$$$$| $$  \__/
| $$$$$$$$| $$$$$$$/| $$ $$/$$ $$|  $$$$$$ 
| $$__  $$| $$____/ | $$  $$$| $$ \____  $$
| $$  | $$| $$      | $$\  $ | $$ /$$  \ $$
| $$  | $$| $$      | $$ \/  | $$|  $$$$$$/
|__/  |__/|__/      |__/     |__/ \______/ 
                                       
"""

# Path to cache file (stored in the same directory as the script)
CACHE_FILE = os.path.join(os.path.dirname(__file__), 'last_query.pkl')

def parse_arguments():
    """
    Parse command-line arguments for observation hour, reuse option, and minimum altitude.
    """
    parser = argparse.ArgumentParser(
        description='Identify high proper motion stars visible from Strasbourg at a specified hour.'
    )
    parser.add_argument(
        '-t', '--time',
        type=float,
        default=None,
        help='Observation hour in local time (24-hour format). Example: 22.5 for 22:30.'
    )
    parser.add_argument(
        '-r', '--reuse',
        action='store_true',
        help='Reuse the last query result from the cache.'
    )
    parser.add_argument(
        '-m', '--min-altitude',
        type=float,
        default=30.0,
        help='Minimum altitude (in degrees) for a star to be considered visible. Default is 30 degrees.'
    )
    return parser.parse_args()

def get_observation_time(specified_hour):
    """
    Determine the observation time based on the specified hour or current time.
    """
    now = datetime.datetime.now()
    if specified_hour is not None:
        if not (0 <= specified_hour < 24):
            print("Error: Observation hour must be between 0 and 24.")
            sys.exit(1)
        # Replace hour and minute with specified_hour
        hour = int(specified_hour)
        minute = int(round((specified_hour - hour) * 60))
        observation_datetime = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        # If the specified time has already passed today, assume it's for the next day
        if observation_datetime < now:
            observation_datetime += datetime.timedelta(days=1)
    else:
        observation_datetime = now  # Current time
    return Time(observation_datetime)

def prompt_sort_options():
    """
    Prompt the user to choose a column to sort by and the sort order.
    """
    sort_columns = {
        '1': 'Main Identifier',
        '2': 'RA (deg)',
        '3': 'DEC (deg)',
        '4': 'pmRA (mas/yr)',
        '5': 'pmDEC (mas/yr)',
        '6': 'V_mag',
        '7': 'Total Movement (mas/yr)'  # Renamed from "Mean Movement"
    }
    print("\nSort Options:")
    for key, value in sort_columns.items():
        print(f"{key}. {value}")
    
    while True:
        choice = input("Enter the number corresponding to the column you want to sort by (or press Enter to skip): ").strip()
        if choice == '':
            return None, None
        elif choice in sort_columns:
            break
        else:
            print("Invalid choice. Please enter a valid number from the list.")
    
    # Choose sort order
    while True:
        order = input("Enter 'a' for ascending or 'd' for descending order: ").strip().lower()
        if order in ['a', 'd']:
            break
        else:
            print("Invalid input. Please enter 'a' or 'd'.")
    
    sort_column = sort_columns[choice]
    sort_order = 'ascending' if order == 'a' else 'descending'
    return sort_column, sort_order

def load_cache():
    """
    Load the last query result from the cache.
    """
    if not os.path.exists(CACHE_FILE):
        print("Error: No cached query found. Please run the script without the '-r' option first.")
        sys.exit(1)
    try:
        with open(CACHE_FILE, 'rb') as f:
            cached_data = pickle.load(f)
        return cached_data
    except Exception as e:
        print(f"Error loading cache: {e}")
        sys.exit(1)

def save_cache(results):
    """
    Save the query results to the cache.
    """
    try:
        with open(CACHE_FILE, 'wb') as f:
            pickle.dump(results, f)
    except Exception as e:
        print(f"Warning: Failed to save cache. {e}")

def assign_units_if_needed(data, desired_unit):
    """
    Assign units to data if they don't already have units.
    If data has units and they are compatible with desired_unit, convert to desired_unit.
    If data has incompatible units, raise an error.
    """
    if data.unit is None:
        return data * desired_unit
    elif data.unit.is_equivalent(desired_unit):
        return data.to(desired_unit)
    else:
        raise UnitTypeError(f"Data has unit {data.unit}, which is not compatible with {desired_unit}.")

def main():
    # Parse command-line arguments
    args = parse_arguments()
    
    # Validate min_altitude
    if not (0 <= args.min_altitude <= 90):
        print("Error: Minimum altitude must be between 0 and 90 degrees.")
        sys.exit(1)
    
    # Define Strasbourg's location
    strasbourg_location = EarthLocation(lat=48.5833*u.deg, lon=7.7500*u.deg, height=140*u.m)
    observer = Observer(location=strasbourg_location, timezone="Europe/Berlin", name="Strasbourg")

    # Define observation time
    observation_time = get_observation_time(args.time)
    initial_time = Time("J2000.0")
    delta_time = observation_time - initial_time
    delta_years = delta_time.to(u.year).value
    observation_hour = observation_time.datetime.strftime("%H:%M")

    # Load or perform query
    if args.reuse:
        results = load_cache()
        print("Reusing the last query result from the cache.")
    else:
        # Connect to the SIMBAD TAP service
        tap_url = "https://simbad.cds.unistra.fr/simbad/sim-tap/"
        tap = TapPlus(url=tap_url)

        # Define the ADQL query
        adql_query = """
        SELECT basic.oid,
               basic.ra,
               basic.dec,
               basic.main_id AS "Main_Identifier",
               basic.pmra, basic.pmdec,
               flux.flux AS "V_Magnitude"
        FROM basic
        JOIN flux ON basic.oid=flux.oidref
        WHERE SQRT(basic.pmra*basic.pmra + basic.pmdec*basic.pmdec) > 1000
          AND flux.filter = 'V'
          AND flux.flux >= 6
          AND flux.flux <= 15
        """

        print("Querying SIMBAD TAP service for high proper motion stars...")
    
        try:
            job = tap.launch_job(adql_query)
            results = job.get_results()
            save_cache(results)
            print("Query completed and results cached.")
        except Exception as e:
            print(f"An error occurred while querying the TAP service: {e}")
            sys.exit(1)

    if len(results) == 0:
        print("No stars found matching the criteria.")
        sys.exit(0)

    print(f"Number of stars retrieved: {len(results)}")
    print("Columns returned by the query:")
    print(results.colnames)

    # Extract data with corrected column names
    try:
        ra = results['ra']  # in degrees
        dec = results['dec']  # in degrees
        main_id = results['Main_Identifier']
        pmra = results['pmra']  # in mas/year
        pmdec = results['pmdec']  # in mas/year
        v_mag = results['V_Magnitude']
    except KeyError as e:
        print(f"KeyError: {e}. Please check the column names.")
        sys.exit(1)

    # Update positions based on proper motion using SkyCoord's apply_space_motion
    print("Updating star positions based on proper motion...")
    
    try:
        # Assign units only if data is unitless
        ra = assign_units_if_needed(ra, u.deg)
        dec = assign_units_if_needed(dec, u.deg)
        pmra = assign_units_if_needed(pmra, u.mas/u.yr)
        pmdec = assign_units_if_needed(pmdec, u.mas/u.yr)
        
        # Calculate pm_ra_cosdec correctly
        pm_ra_cosdec = (pmra * np.cos(dec.to(u.rad))).to(u.mas/u.yr)
        
        # Create SkyCoord object with proper motion
        coords = SkyCoord(ra=ra,
                          dec=dec,
                          pm_ra_cosdec=pm_ra_cosdec,
                          pm_dec=pmdec,
                          frame='icrs',
                          obstime=initial_time)

        # Apply space motion to get updated coordinates
        coords_updated = coords.apply_space_motion(observation_time)

        updated_ra = coords_updated.ra.deg
        updated_dec = coords_updated.dec.deg
    except UnitTypeError as e:
        print(f"UnitTypeError: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred while updating coordinates: {e}")
        sys.exit(1)

    # Determine if it's currently night at Strasbourg at the observation time
    is_night = observer.is_night(observation_time)

    # Display header with ASCII art and observation hour
    print("\n" + ASCII_ART)
    print(f"High Proper Motion Stars Visible from Strasbourg at {observation_hour}\n")

    if not is_night:
        print("It is not night in Strasbourg at the specified observation time. No stars will be visible.")
        sys.exit(0)

    print("Checking visibility of stars at the specified observation time in Strasbourg...")

    # Transform coordinates to AltAz frame
    try:
        altaz_frame = AltAz(obstime=observation_time, location=strasbourg_location)
        altaz_coords = SkyCoord(ra=updated_ra * u.deg, dec=updated_dec * u.deg).transform_to(altaz_frame)
    except Exception as e:
        print(f"An error occurred during coordinate transformation: {e}")
        sys.exit(1)

    # Define a minimum altitude for visibility (user-specified or default)
    min_altitude = args.min_altitude * u.deg

    # Check which stars are above the minimum altitude
    visible = altaz_coords.alt >= min_altitude

    # Filter visible stars
    visible_indices = np.where(visible)[0]

    if len(visible_indices) == 0:
        print(f"No high proper motion stars are currently visible above {min_altitude}.")
        sys.exit(0)

    print(f"Number of stars visible above {min_altitude}: {len(visible_indices)}\n")
    print("List of visible high proper motion stars:\n")
    
    # Updated header to include both J2000 and Corrected RA/Dec, along with Total Movement
    print("{:<30} {:>12} {:>12} {:>12} {:>12} {:>15} {:>15} {:>20} {:>10}".format(
        "Main Identifier", "J2000 RA", "J2000 Dec", "Updated RA", "Updated Dec", 
        "pmRA (mas/yr)", "pmDEC (mas/yr)", "Total Movement (mas/yr)", "V_mag"))

    # Prepare data for display and sorting
    visible_data = {
        'Main Identifier': main_id[visible_indices],
        'J2000 RA (deg)': ra[visible_indices].value,
        'J2000 Dec (deg)': dec[visible_indices].value,
        'Updated RA (deg)': updated_ra[visible_indices],
        'Updated Dec (deg)': updated_dec[visible_indices],
        'pmRA (mas/yr)': pmra[visible_indices].value,
        'pmDEC (mas/yr)': pmdec[visible_indices].value,
        'Total Movement (mas/yr)': np.sqrt(pmra[visible_indices].value**2 + pmdec[visible_indices].value**2),
        'V_mag': v_mag[visible_indices]
    }

    for i in range(len(visible_data['Main Identifier'])):
        print("{:<30} {:>12.5f} {:>12.5f} {:>12.5f} {:>12.5f} {:>15.2f} {:>15.2f} {:>20.2f} {:>10.2f}".format(
            visible_data['Main Identifier'][i],
            visible_data['J2000 RA (deg)'][i],
            visible_data['J2000 Dec (deg)'][i],
            visible_data['Updated RA (deg)'][i],
            visible_data['Updated Dec (deg)'][i],
            visible_data['pmRA (mas/yr)'][i],
            visible_data['pmDEC (mas/yr)'][i],
            visible_data['Total Movement (mas/yr)'][i],
            visible_data['V_mag'][i]
        ))

    # Prompt user for sorting options
    sort_column, sort_order = prompt_sort_options()
    if sort_column:
        # Create a list of indices sorted based on the chosen column
        if sort_column == 'Main Identifier':
            sorted_indices = np.argsort(visible_data['Main Identifier'])
        elif sort_column == 'Total Movement (mas/yr)':
            sorted_indices = np.argsort(visible_data['Total Movement (mas/yr)'])
        else:
            sorted_indices = np.argsort(visible_data[sort_column])
    
        if sort_order == 'descending':
            sorted_indices = sorted_indices[::-1]
    
        print(f"\nStars sorted by {sort_column} in {sort_order} order:\n")
        
        # Updated header to include both J2000 and Corrected RA/Dec, along with Total Movement
        print("{:<30} {:>12} {:>12} {:>12} {:>12} {:>15} {:>15} {:>20} {:>10}".format(
            "Main Identifier", "J2000 RA", "J2000 Dec", "Updated RA", "Updated Dec", 
            "pmRA (mas/yr)", "pmDEC (mas/yr)", "Total Movement (mas/yr)", "V_mag"))

        for i in sorted_indices:
            print("{:<30} {:>12.5f} {:>12.5f} {:>12.5f} {:>12.5f} {:>15.2f} {:>15.2f} {:>20.2f} {:>10.2f}".format(
                visible_data['Main Identifier'][i],
                visible_data['J2000 RA (deg)'][i],
                visible_data['J2000 Dec (deg)'][i],
                visible_data['Updated RA (deg)'][i],
                visible_data['Updated Dec (deg)'][i],
                visible_data['pmRA (mas/yr)'][i],
                visible_data['pmDEC (mas/yr)'][i],
                visible_data['Total Movement (mas/yr)'][i],
                visible_data['V_mag'][i]
            ))

if __name__ == "__main__":
    main()
