'''
Script to handle all rfid related functions
'''

import pandas as pd
import os
from datetime import datetime, timedelta
from pytz import timezone
import traceback

from shared_functions import *

###############################################################################
# Global dictionary variable holding all constants
###############################################################################
global CONFIG


###############################################################################
# Create a series with timestamps as the index and tag number as value
###############################################################################
def get_rfid_series (rfid_data_path, remove_duplicates = True, remove_dummy_tags = True):
	
	rfid_series = pd.Series()

	if not os.path.exists(rfid_data_path):
		print("RFID data directory not found")
		return rfid_series

	
	rfid_files = os.listdir(rfid_data_path)

	for file in rfid_files:
		try:
			if file.startswith('R') and file.endswith('.csv'):
				rfid_file_path = os.path.join(rfid_data_path, file)
				with open(rfid_file_path, 'r') as rfid_file:
					line = rfid_file.readline().strip()
			
					# Split the line at the comma
					parts = line.split(',')

					# Extract the timestamp and tag number
					timestamp = pd.Timestamp(float(parts[0]), unit = 's', tz='Africa/Johannesburg')
					# timestamp = timestamp + pd.Timedelta(hours=2)				

					parts_2 = parts[1].split(' ')
					tag_number = parts_2[5]

					rfid_series[timestamp] = tag_number

		except:
			traceback.print_exc()

	# print("Starting with {} tags".format(len(rfid_series)))

	if remove_dummy_tags == True:
		# print("Removing test tags")
		rfid_series = remove_test_tags(rfid_series)

	if remove_duplicates == True:
		# print("Removing duplicate tags")
		rfid_series = remove_duplicate_tags(rfid_series)
	
	# print("Ending with {} tags".format(len(rfid_series)))
	return rfid_series
###############################################################################

###############################################################################
# This function removes tags that were picked up numerous times
###############################################################################
def remove_duplicate_tags (rfid_series):

	rfid_series = rfid_series.sort_index()
	
	rfid_series_copy = rfid_series.copy()
	
	# print("rfid_series ", rfid_series)

	for rfid_timestamp, tag in rfid_series.items():
		# If this tag is found again within *** min, remove it and go on to the next tag
		if (check_for_duplicate(rfid_timestamp, tag, rfid_series)):
			rfid_series_copy = rfid_series_copy.drop(rfid_timestamp)

	# print("Removed {} duplicates".format( len(rfid_series) - len(rfid_series_copy)))
	return rfid_series_copy
###############################################################################



###############################################################################
# This removes any test tags from being processed together with bird data
###############################################################################
def remove_test_tags (rfid_series):

	# print("rfid_series ", rfid_series)
	rfid_series = rfid_series.sort_index()
	
	rfid_series_copy = rfid_series.copy()
	
	for rfid_timestamp, tag in rfid_series.items():
		
		if tag in CONFIG["TEST_TAGS"]:
			rfid_series_copy = rfid_series_copy.drop(rfid_timestamp)
	
	# print("Removed {} test tags".format( len(rfid_series) - len(rfid_series_copy)))
	return rfid_series_copy
###############################################################################



###############################################################################
# This fucnction checks if the given tag is found again within x minutes. If so, return 1
# x is set in the config file as "RFID_IGNORE_INTERVAL"
###############################################################################
def check_for_duplicate (rfid_timestamp, tag, rfid_series):
	# print("rfid_timestamp start",rfid_timestamp)
	shortened_series = rfid_series[rfid_timestamp:]
	
	for timestamp_compare, tag_compare in shortened_series.items():
	
		time_difference = (timestamp_compare - rfid_timestamp).total_seconds()
		
		if (time_difference > 0 and time_difference < CONFIG["RFID_IGNORE_INTERVAL"] and tag == tag_compare):
			return 1
	return 0
###############################################################################



###############################################################################
# This checks if an RFID tag was picked up as a penguin was jumping from one
# scale to another
###############################################################################
def check_rfid_during_jump (penguin, rfid_timestamp):

	# scale 1 first, then scale 2
	if penguin.direction == 'out_to_ocean':

		if (rfid_timestamp > penguin.time_off_1 and rfid_timestamp < penguin.time_on_2):

			print ("RFID detected during jump from scale 1 to scale 2.")
			return True

	elif penguin.direction == 'back_from_ocean':

		if (rfid_timestamp > penguin.time_off_2 and rfid_timestamp < penguin.time_on_1):

			print ("RFID detected during jump from scale 2 to scale 1.")
			return True

	return False
###############################################################################




###############################################################################
# Here we are checking for an RFID tag that was picked up anywhere during the crossing
# There must be only 1 tag found during the crossing
###############################################################################
def check_unique_rfid_during_crossing (penguin, penguin_list, rfid_timestamp, rfid_series):

	penguin_crossing_start = min([penguin.time_on_1, penguin.time_off_1, penguin.time_on_2, penguin.time_off_2])
	penguin_crossing_end = max([penguin.time_on_1, penguin.time_off_1, penguin.time_on_2, penguin.time_off_2])

	# Tag picked up during crossing
	if (penguin_crossing_start < rfid_timestamp and rfid_timestamp < penguin_crossing_end):

		# Check no other tags picked up during crossing
		rfid_series_copy = rfid_series.copy()

		for rfid_timestamp_check, tag in rfid_series_copy.items():
			
			# Ignore original tag while checking the rest
			if rfid_timestamp_check == rfid_timestamp:
				continue

			# Another tag was picked up during the crossing
			if (penguin_crossing_start < rfid_timestamp_check and rfid_timestamp_check < penguin_crossing_end):
				print("More than one tag picked up during penguin crossing ", rfid_timestamp_check)
				return False

		return True
###############################################################################



###############################################################################
##### Check if the rfid tag was by itself #########
###############################################################################
def rfid_in_isolation (rfid_timestamp, rfid_series):

	for temp_timestamp, tag in rfid_series.items():
		# If this tag is found again within *** min, remove it and go on to the next tag
		time_between_tags = abs((rfid_timestamp - temp_timestamp).total_seconds())

		if time_between_tags > 0 and time_between_tags < CONFIG["RFID_ISOLATION_INTERVAL"]:
			return False

	return True
###############################################################################





###############################################################################
# Check if rfid tag was registered within x min of a penguin crossing scales
# x is set in config file as "RFID_TO_PENGUIN_INTERVAL"
###############################################################################
def rfid_close_to_penguin (penguin, rfid_timestamp):

	penguin_crossing_start = min([penguin.time_on_1, penguin.time_off_1, penguin.time_on_2, penguin.time_off_2])
	penguin_crossing_end = max([penguin.time_on_1, penguin.time_off_1, penguin.time_on_2, penguin.time_off_2])

	# print("penguin_crossing_start ", penguin_crossing_start)
	# print("penguin_crossing_end ", penguin_crossing_end)
	# print("rfid_timestamp ", rfid_timestamp)

	# Get a single crossing time for the penguin, taken as halfway though its crossing
	penguin_crossing_time = penguin_crossing_start + (penguin_crossing_end - penguin_crossing_start)/2

	duration_between_rfid_and_penguin = abs((penguin_crossing_time - rfid_timestamp).total_seconds())

	if duration_between_rfid_and_penguin < CONFIG["RFID_TO_PENGUIN_INTERVAL"]:
		return True

	else:
		return False
###############################################################################


###############################################################################
# This function checks if the RFID tag passes certain tests and then assigns
# it to a penguin
###############################################################################
def check_add_rfid (site_dict, rfid_data_path, scale_data_path, penguin_list):

	rfid_series = get_rfid_series(rfid_data_path, remove_duplicates = True, remove_dummy_tags = True)
	penguin_list_with_rfid = []
	num_of_tags = len(rfid_series)
	rfid_counter = 0

	# penguin_list_copy = penguin_list.copy()

	# Check for each penguin in list
	for penguin in penguin_list:

		for rfid_timestamp, tag in rfid_series.items(): 

			if rfid_close_to_penguin (penguin, rfid_timestamp) == True:
	
				print("RFID detected close to penguin. Checking further... ", rfid_timestamp)

				# No other RFID tags detected within time interval (set RFID_ISOLATION_INTERVAL in config.json)
				if rfid_in_isolation(rfid_timestamp, rfid_series) == True:
					rfid_isolation = True
				else:
					print("RFID not in isolation")
					rfid_isolation = False				

				# No other event files within time interval (set EVENT_FILE_ISOLATION_INTERVAL in config.json)
				if check_scale_file_isolation(penguin.scale_file, scale_data_path) == True:
					scale_file_isolation = True
				else:
					print("scale_file not in isolation: ")
					scale_file_isolation = False

				# Check that there was only one penguin in the event
				if find_number_of_penguins_event(penguin, penguin_list) == 1:
					penguin_alone_event = True
				else:
					print("penguin not alone in event")
					penguin_alone_event = False

				if site_dict['rfid_location'] == 'middle_only':
					
					# Only one RFID tag picked up during this penguin's crossing
					if check_unique_rfid_during_crossing(penguin, penguin_list, rfid_timestamp, rfid_series) == True:
						penguin.rfid_crossing_flag = True

						# If an rfid tag was triggered during the jump, assign it to the penguin
						if check_rfid_during_jump(penguin, rfid_timestamp) == True:
							print("RFID detected during jump. Timestamp: ", rfid_timestamp)
							rfid_counter = rfid_counter + 1
							penguin.id = tag
							penguin.rfid_jump_flag = True
							break
				
						# If it is not during the jump, we can still assign it if no other penguin's crossing is overlapping
						elif penguin_alone_during_crossing (penguin, penguin_list) == True:
							print("Penguin alone during crossing")
							rfid_counter = rfid_counter + 1
							penguin.id = tag
							penguin.rfid_alone_crossing_flag = True
							break
					
				if rfid_isolation and scale_file_isolation and penguin_alone_event:
					
					print("RFID and event file in isolation. Penguin alone during event. Assigning tag")
					rfid_counter = rfid_counter + 1
					penguin.id = tag
					break
				
		penguin_list_with_rfid.append(penguin)

	# return penguin_list_with_rfid

	return penguin_list_with_rfid, rfid_counter, num_of_tags
###############################################################################





###############################################################################
# END
###############################################################################
