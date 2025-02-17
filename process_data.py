#!/usr/bin/env python3

###############################################################################
# Imports
###############################################################################
import os
import sys
from datetime import datetime, timedelta
import traceback
from shared_functions import *
from classes import *
from data_plot import *
from rfid import *
from penguin_functions import *
import pytz
###############################################################################

###############################################################################
# Global dictionary variable holding all constants
###############################################################################
global CONFIG

# aws s3 cp --recursive s3://apmsbirdlife/APMS/data/stony_point/2025/20250201/ C:\Users\pierr\apms_data_processing\data\downloaded_raw\stony_point\2025\20250201
##############################################################################
# This is the main data processing function
# It gets passed a site and a list of days to process
# If "temp" is True, it will process the data in ~/apms_data_processing/temp (uncomment relevent section)
##############################################################################
def process_data (site_dict, day_obj_list = None, temp = None):

	site_name = site_dict['name']
	penguin_total_list = []

	##########################################################################################
	# Executes if temp parameter was sent. This processes data in the temp/ folder
	##########################################################################################
	if (temp):
		data_path = os.path.join(CONFIG["DATA_PATH"], 'temp')
		scale_temp_data_path = os.path.join(data_path, 'scale')
		scale_files = get_scale_files(scale_temp_data_path)

		penguin_list_all_files = []
		for file in scale_files:
			try:
				scale_file_path = os.path.join(scale_temp_data_path, file)
				file_penguin_list = process_scale_file(scale_file_path)
				print("penguin list for file")
				print_penguin_list(file_penguin_list)
				penguin_list_all_files = penguin_list_all_files + file_penguin_list
			except Exception as e:
				traceback.print_exc()

		print("penguin list for all scale files")
		print_penguin_list(penguin_list_all_files)
		return
	else:
		data_path = CONFIG["DATA_PATH"]
	##########################################################################################
	
	
	##########################################################################################
	# Go through the requested date range, day by day
	for day_obj in day_obj_list:

		day_error_counter = 0
		penguin_day_list = []
		day = day_obj.strftime("%Y%m%d")
		print("Processing data for date: ", day)
		year = day[0:4]
		
		scale_day_directory = os.path.join(data_path, 'processing', site_name, year, day, 'scale')
		rfid_data_path = os.path.join(data_path, 'processing', site_name, year, day, 'rfid')
		output_data_path = os.path.join(data_path, 'processed', site_name, year, day)

		print("Clearing {} processed directory".format(site_name))
		shutil.rmtree(output_data_path, ignore_errors = True)	

		if (not os.path.exists(scale_day_directory)):
			print("scale directory does not exist, moving on to next day")
			# move on to the next day
			continue

		# Uncomment this to process data before 11/09/2023
		# fix_overlap(scale_day_directory)

		penguin_day_list, number_of_scale_files, day_error_counter = process_scale_files(scale_day_directory, output_data_path) 

		### Finished building the penguin list from the scale files. Now check and add rfid tags
		print("Checking for RFID tags...")
		penguin_day_list, number_of_assigned_tags, number_of_tags = check_add_rfid (site_dict, rfid_data_path, scale_day_directory, penguin_day_list)
		

		# for loop done with all files for the day. Create metadata
		meta_data = {
		"site_name":site_name, 
		"number_of_scale_files":number_of_scale_files,
		"number_of_penguin_files":(number_of_scale_files - day_error_counter),
		"number_of_tags":number_of_tags,
		"number_of_assigned_tags":number_of_assigned_tags}

		csv_file_path = os.path.join(output_data_path, '{}_{}_processed_data.csv'.format(site_name,day))
		
		if len(penguin_day_list) > 0:
			
			# Sort the list first
			penguin_day_list = sorted(penguin_day_list, key = (lambda penguin: penguin.time_on_1))

			penguin_list_to_csv(penguin_day_list, csv_file_path, meta_data)

			# for loop done with all days processed
			number_of_penguin_files = number_of_scale_files - day_error_counter
			process_percentage = round(100.0*(number_of_penguin_files/number_of_scale_files))
			print("OVERVIEW")
			print("Total number of scale files for day: ", number_of_scale_files)
			print("Total number of penguin files for day: {} ({})".format(number_of_penguin_files,process_percentage))
			print("Total number of RFID tags for the day: ", number_of_tags)
			print("Total number of assigned RFID tags: ", number_of_assigned_tags)

			penguin_total_list = penguin_total_list + penguin_day_list
	
	print("Done. Found {} penguins in total".format(len(penguin_total_list)))
	print("Final Penguin List")
	print_penguin_list(penguin_list = penguin_total_list, rfid = True)
##############################################################################




##############################################################################
if __name__ == "__main__":

	now = datetime.now()
	_time = now.strftime("%H:%M:%S")
	day = now.strftime("%Y%m%d")
	print ("#########################################")
	print ("#### Penguin Data Processing Script #####")
	print ("#### Date: {}   Time: {} ####".format(day,_time))
	print ("#########################################")



	####################################################
	######## UNCOMMENT FOR TEMPORARY DATA ##############
	####################################################
	# site_dict = CONFIG["SITES"]["stony_point"]
	# process_data(site_dict = site_dict, temp = True)
	# plot_all_data_folder ()
	# sys.exit()
	####################################################
	####################################################


	# These can be used as templates. Useful to set date range when not running from terminal
	#########################################################################################
	# day_obj_list = date_range_to_object_list("20250117-20250117")
	# day_obj_list = date_range_to_object_list("20240902-20240906")
	# day_obj_list = days_back_object_list(1)
	# site = {"name": "stony_point", "rfid_location": "middle_only", "start_date": "20230603"}
	# sites = [site]
	
	# Comment this out when a specific date or site is selected
	sites, day_obj_list = analyze_arguments()	

	for site_dict in sites:

		if CONFIG["DOWNLOAD_ALL"] == True:
			download_all_files (site_dict = site_dict, day_obj_list = day_obj_list)
		
		# This makes a copy of the raw data for the date period requested.
		# Data is moved to the processing/ directory	
		copy_local_data(site_dict = site_dict, day_obj_list = day_obj_list)
		
		# Ucomment to view raw data with RFID tags superimposed
		# plot_with_rfid (site_dict = site_dict, day_obj_list = day_obj_list)

		process_data(site_dict = site_dict, day_obj_list = day_obj_list)
		# plot_with_rfid (site_dict = site_dict, day_obj_list = day_obj_list)
		# plot_daily_avg(site_dict = site_dict, day_obj_list = day_obj_list)

	print("DONE")
	sys.exit()
