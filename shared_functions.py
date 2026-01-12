import os
import sys
import csv
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pytz
import pandas as pd
import boto3
import shutil
import json


###############################################################################
# Global Variables
###############################################################################
global CONFIG




###############################################################################
# This function loads all the relevant constants from the config.JSON file.
###############################################################################
def load_config_file (config_file_path):
	
	global CONFIG
	CONFIG = {}

	with open(config_file_path, 'r') as config_file:
		config = json.load(config_file)
		CONFIG.update(config)

		# print(CONFIG["MAX_DEADWEIGHT_DIFF"])
		# sys.exit()
		# my_dict["location"] = "New York"

		CONFIG["DATA_PATH"] = os.path.join(os.path.dirname(config_file_path),"data")

	return CONFIG
###############################################################################


###############################################################################
# This function copies data that will be processed
###############################################################################
def copy_local_data (site_dict, day_obj_list):

	# global CONFIG

	DOWNLOAD_PATH = os.path.join(CONFIG["DATA_PATH"], 'downloaded_raw')
	DATA_PROCESSING_PATH = os.path.join(CONFIG["DATA_PATH"], 'processing')
	
	site = site_dict['name']
	for day_obj in day_obj_list:

		day = day_obj.strftime("%Y%m%d")
		year = day[0:4]
		
		src_dir = os.path.join(DOWNLOAD_PATH, site, year, day)
		dst_dir = os.path.join(DATA_PROCESSING_PATH, site, year, day)
		
		if_then_delete (dst_dir)
		if_not_then_make (dst_dir)

		if (os.path.exists(src_dir)):
			print("Copying data for {}".format(day))
			shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)
		else:
			print("Could not find data locally for {}".format(day))

	print("Done copying files")
###############################################################################



###############################################################################
# This function gets a list of scale files in the scale directory
###############################################################################
def get_scale_files (scale_data_path):

	scale_files = []
	file_list = os.listdir(scale_data_path)
	for file in file_list:
		if file.startswith('S') and file.endswith('.csv'):
			scale_files.append(file)

	return scale_files
###############################################################################


###############################################################################
# 
###############################################################################
def find_number_of_penguins_event (penguin, penguin_list):

	number_of_penguins = 0
	# First check that this is the only penguin found in that event file
	for penguin_compare in penguin_list:
		if penguin_compare.scale_file == penguin.scale_file:
			number_of_penguins = number_of_penguins + 1

	return number_of_penguins

###############################################################################



###############################################################################
##### Check if no other penguin crossing overlapped #########
###############################################################################
def penguin_alone_during_crossing (penguin, penguin_list):
	
	### First remove the penguin from the total penguin list ###
	penguin_list_copy = penguin_list.copy()
	penguin_list_copy.remove(penguin)	
	
	# print("BEFORE.....Penguin: ",penguin.time_on_1, penguin.direction)
	# print_penguin_list(penguin_list)
	
	# print("AFTER..")
	# print_penguin_list(penguin_list)
	

	penguin_crossing_start = min([penguin.time_on_1, penguin.time_off_1, penguin.time_on_2, penguin.time_off_2])
	penguin_crossing_end = max([penguin.time_on_1, penguin.time_off_1, penguin.time_on_2, penguin.time_off_2])

	for penguin_compare in penguin_list_copy:

		timestamp_list = [penguin_compare.time_on_1, penguin_compare.time_off_1, penguin_compare.time_on_2, penguin_compare.time_off_2]

		for timestamp_compare in timestamp_list:

			if timestamp_compare >= penguin_crossing_start and timestamp_compare <= penguin_crossing_end:
				return False
	return True
###############################################################################


##############################################################################
def check_scale_file_isolation (scale_file, scale_data_path):

	# 120s = 2 min. So there must be no other scale event 2 min before or after
	min_time_between_scale_files = CONFIG["SCALE_FILE_ISOLATION_INTERVAL"]

	scale_file_date_string = scale_file[1:15]

	scale_files = get_scale_files(scale_data_path)

	file_timestamp = pd.to_datetime(scale_file_date_string, format="%Y%m%d%H%M%S")

	for scale_file in scale_files:
		other_date_string = scale_file[1:15]
	
		# Create a timestamp holding the datetime object for the creation time of the other scale file being compared to
		other_timestamp = pd.to_datetime(other_date_string, format="%Y%m%d%H%M%S")

		# check if there are any other scale files triggered within a *** min window
		scale_file_gap = abs((file_timestamp - other_timestamp).total_seconds())
		if  scale_file_gap < min_time_between_scale_files and scale_file_gap != 0:
			print("Another scale file found within {} seconds".format(scale_file_gap))
			return False


	# No other scale files found close by
	return True
##############################################################################


###############################################################################
def penguin_list_to_csv (penguin_list, csv_file_path, meta_data):

	# Extract fieldnames from the first object in the list
	# header = "# Site: {}	Total Number of Files: {}	Succesfully Processed: {} ({}%)".format(site, )
	fieldnames = ['TIMESTAMP','ID','WEIGHT','WEIGHT_DIFFERENCE','DIRECTION', 'SCALE_1_TYPE', 'SCALE_2_TYPE']

	print('converting penguin list to csv file: {}'.format(csv_file_path))
	
	with open(csv_file_path, 'w', newline='') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

		info_line = "Site: {} Total Number of Files: {}	Number of Penguin Files: {} Total number of RFID tags: {} Number of assigned RFID tags: {}\n".format(
			meta_data["site_name"],
			meta_data["number_of_scale_files"],
			meta_data["number_of_penguin_files"], 
			meta_data["number_of_tags"], 
			meta_data["number_of_assigned_tags"])
		
		csvfile.write(info_line)
		writer.writeheader()

		for penguin in penguin_list:
			
			if penguin.direction == 'out_to_ocean':
				timestamp = penguin.time_on_1
			
			elif penguin.direction == 'back_from_ocean':
				timestamp = penguin.time_on_2

			else:
				print("Unknown direction")
				sys.exit()

			temp_dict = {
			'TIMESTAMP' : timestamp.strftime('%Y-%m-%d %H:%M:%S'),
			'ID': penguin.id, 
			'WEIGHT':penguin.weight_obj.weight,
			'WEIGHT_DIFFERENCE':round(penguin.weight_obj.weight_difference,3),
			'DIRECTION':penguin.direction,
			'SCALE_1_TYPE': penguin.scale_1_type, # <--- NEW LINE
			'SCALE_2_TYPE': penguin.scale_2_type} # <--- NEW LINE
			
			writer.writerow(temp_dict)
##############################################################################



###############################################################################
def load_df_two_scales (file_path):

	try:
		# print("Loading ", file_path)
		df = pd.read_csv(file_path, header=None, names=['timestamp', 'scale_1', 'scale_2'])

		# Set 'timestamp' column as the index
		df.set_index('timestamp', inplace=True)
		df.index = pd.to_datetime(df.index, unit='s')
		# df.index = df.index.shift(2, freq='H')

		sa_timezone = pytz.timezone('Africa/Johannesburg')
		df.index = df.index.tz_localize(pytz.utc).tz_convert(sa_timezone)

		return df
	except Exception as e:
		print("error: ",e)
		return 1
###############################################################################





###############################################################################
def load_series_one_scale (file_path):
	series = pd.read_csv(file_path, names=['timestamp', 'weight'])
	series.set_index('timestamp', inplace=True)
	series.index = pd.to_datetime(df.index, unit='s', utc=True)
	series.index = df.index.shift(2, freq='H')

	return series
###############################################################################



##############################################################################
def if_not_then_make (path):
    if not os.path.exists(path):
        os.makedirs(path)
##############################################################################



##############################################################################
def if_then_delete (path):
	if os.path.exists(path):
		print("Deleting ", path)
		shutil.rmtree(path)
##############################################################################



###############################################################################
def days_back_object_list (days_back):

	if days_back == 0:
		print("Getting only today's data...")
		day_obj_list = [datetime.now()]

	elif days_back == 1:
		print("Getting yesterday's data...")
		day_obj_list = [datetime.now() - timedelta(days=1)]

	else:
		day_obj_start = datetime.now() - timedelta(days=days_back)
		day_obj_end = datetime.now() - timedelta(days=1) 
		day_obj_list = get_day_object_list(day_obj_start, day_obj_end)

	return day_obj_list
###############################################################################


###############################################################################
def analyze_arguments():

	# No arguments given
	# Process data from last_dash_date till now
	if len(sys.argv) == 1:
		sites = CONFIG["SITES"]
		print("Getting yesterday's data for all sites...")
		day_obj_list = [datetime.now() - timedelta(days=1)]
		return sites, day_obj_list

	# 1 argument sent
	elif len(sys.argv) == 2:
		arg = sys.argv[1]

		# print help page
		if arg == '--help':
			print_help_process_data()
			sys.exit()

		# only date range given
		# Process all sites for this date range
		elif "-" in arg:
			date_range = arg
			day_obj_list = date_range_to_object_list(date_range)
			sites = CONFIG["SITES"]
			return sites, day_obj_list

		# only number-of-days-back given
		# Process all sites for these days
		elif arg.isnumeric():
			days_back = int(arg)
			day_obj_list = days_back_object_list(days_back)
			sites = CONFIG["SITES"]
			return sites, day_obj_list

		# only site name given
		# Process yesterday's data for the site name given
		else:
			site_name = arg
			sites = process_site_name(site_name)		
			day_obj_list = [datetime.now() - timedelta(days=1)]
			return sites, day_obj_list



	
	#######################################
	# 2 arguments sent
	elif len(sys.argv) == 3:
		
		site_name = sys.argv[1]
		sites = process_site_name(site_name)		
		
		date_range_arg = sys.argv[2]
		
		# date range given
		# Process date range for site given
		if "-" in date_range_arg:
			date_range = date_range_arg
			day_obj_list = date_range_to_object_list(date_range)

		# number of days back given
		# Process number of days back for site
		elif date_range_arg.isnumeric():
			days_back = int(date_range_arg)
			day_obj_list = days_back_object_list(days_back)
		else:
			print("Invalid arguments provided")
			sys.exit()
	else:
		return 0,0

	return sites, day_obj_list
###############################################################################


###############################################################################
def process_site_name (site_name):

	for SITE in CONFIG["SITES"]:
		if SITE['name'] == site_name:
			return [SITE]
	
	print("Invalid site name.")
	print("Site name given: ", site_name)
	sys.exit()
###############################################################################


###############################################################################
def date_range_to_object_list (date_range):
	
	date_format = "%Y%m%d"
	date_from = date_range.split('-')[0]
	day_obj_start = datetime.strptime(date_from, date_format)
	date_to = date_range.split('-')[1]
	day_obj_end = datetime.strptime(date_to, date_format)
	day_obj_list = get_day_object_list(day_obj_start, day_obj_end)
	return day_obj_list
###############################################################################


###############################################################################
# dashboard
def get_day_object_list (day_obj_start, day_obj_end):

	day_obj_list = []
	
	one_day = timedelta(days=1)

	day_obj = day_obj_start
	while (day_obj.date() <= day_obj_end.date()):

		# print("start ",day_obj_start)
		# print("end ",day_obj_end)
		day_obj_list.append(day_obj)
		day_obj = day_obj + one_day
		
	day_obj_list = sorted(day_obj_list)
	return day_obj_list
###############################################################################



# This function gets scale data and finds all the weights
# It returns a list of start- and end-timestamps for each weight
###################################################################################################################################################
def get_weights_timestamps_list (scale_data):
	
	weights_list = []
	sub_events_list = []
	dead_event_list	= []

	window_duration = CONFIG["PENGUIN_WALKING_PERIOD_MAX"]
	max_std_dev = CONFIG["STD_DEV_DYNAMIC"]
	window_size = int(CONFIG["SAMPLING_FREQ"] * window_duration)
	rolling_std_dev = scale_data.rolling(window=window_size, center=True).std()
	mask = rolling_std_dev > CONFIG["STD_DEV_DYNAMIC"]
	cumul_sum = mask.cumsum()
	consec_counts = (cumul_sum.groupby(cumul_sum)).count()
	consec_counts = consec_counts[consec_counts > int(window_size/2)]

	for group_name, val in consec_counts.items():
		# print('group_name',group_name)
		# print('val',val)
		
		series = cumul_sum[cumul_sum == group_name]
		timestamp_1 = series.index[0]
		timestamp_2 = series.index[-1]
	
		weights_list.append( (timestamp_1,timestamp_2) )
	
	# weight_list is a list of tuples.
	# Each tuple contains the start and end-timestamps of the weight
	return weights_list
###############################################################################



###############################################################################
def download_all_files (site_dict, day_obj_list):

	DOWNLOAD_PATH = os.path.join(CONFIG["DATA_PATH"], 'downloaded_raw')

	site_name = site_dict['name']

	for day_obj in day_obj_list:
		
		day = day_obj.strftime("%Y%m%d")
		year = day[0:4]

		s3_folder_path = CONFIG["S3_DATA_PATH"] + site_name + '/' + year + '/' + day + '/'
		download_folder_path = os.path.join(DOWNLOAD_PATH, site_name, year, day)

		command = "aws s3 cp --recursive s3://{}/{} {}".format(CONFIG["BUCKET_NAME"], s3_folder_path, download_folder_path )
		print(command)

		os.system(command)
###############################################################################



###############################################################################
def download_scale_files (site_dict, day_obj_list):

	DOWNLOAD_PATH = os.path.join(CONFIG["DATA_PATH"], 'downloaded_raw')

	site = site_dict['name']
	print("Fetching scale data for {}".format(site))
	


	print("DEBUG")
	print(CONFIG["AWS_ACCESS_KEY"])
	print(CONFIG["AWS_SECRET_ACCESS_KEY"])


	session = boto3.Session(
	aws_access_key_id = CONFIG["AWS_ACCESS_KEY"],
	aws_secret_access_key = CONFIG["AWS_SECRET_ACCESS_KEY"],
	region_name='af-south-1')
	s3_resource = session.resource('s3')
	bucket = s3_resource.Bucket(CONFIG["BUCKET_NAME"])

	for day_obj in day_obj_list:

		day = day_obj.strftime("%Y%m%d")
		year = day[0:4]
			
		s3_folder_path = CONFIG["S3_DATA_PATH"] + site + '/' + year + '/' + day + '/' + 'scale/'
		download_folder_path = os.path.join(DOWNLOAD_PATH, site, year, day, 'scale')

		if_not_then_make (download_folder_path)

		try:
			for obj in bucket.objects.filter(Prefix = s3_folder_path):
				key = obj.key
				# print("key ",key)
				filepath = os.path.join(download_folder_path, os.path.relpath(obj.key, s3_folder_path))
				print("Downloading ",filepath)
				bucket.download_file(obj.key, filepath)
		except Exception as e:
			print("Could not download scale data from cloud")
			print(e)
###############################################################################


###############################################################################
def download_rfid_files (site_dict, day_obj_list):
	
	DOWNLOAD_PATH = os.path.join(CONFIG["DATA_PATH"], 'downloaded_raw')
	site = site_dict['name']
	print("Fetching rfid data for {}".format(site))
	session = boto3.Session(
	aws_access_key_id = CONFIG["AWS_ACCESS_KEY"],
	aws_secret_access_key = CONFIG["AWS_SECRET_ACCESS_KEY"],
	region_name='af-south-1')
	s3_resource = session.resource('s3')
	bucket = s3_resource.Bucket(CONFIG["BUCKET_NAME"])

	for day_obj in day_obj_list:

		day = day_obj.strftime("%Y%m%d")
		year = day[0:4]
			
		s3_folder_path = CONFIG["S3_DATA_PATH"] + site + '/' + year + '/' + day + '/' + 'rfid/'
		download_folder_path = os.path.join(DOWNLOAD_PATH, site, year, day, 'rfid')
		if_not_then_make (download_folder_path)

		try:
			for obj in bucket.objects.filter(Prefix = s3_folder_path):
				key = obj.key
				# print("key ",key)
				filepath = os.path.join(download_folder_path, os.path.relpath(obj.key, s3_folder_path))
				print("Downloading ",filepath)
				bucket.download_file(obj.key, filepath)
		except Exception as e:
			print("Could not download rfid data from cloud")
			print(e)
###############################################################################


###############################################################################
def download_status_files (site_dict, day_obj_list):

	site = site_dict['name']
	s3 = boto3.client('s3',
		aws_access_key_id = CONFIG["AWS_ACCESS_KEY"],
		aws_secret_access_key = CONFIG["AWS_SECRET_ACCESS_KEY"])
	
	for day_obj in day_obj_list:

		day = day_obj.strftime("%Y%m%d")
		filename = day + '_STATUS.txt'
		year = day[0:4]
		
		download_folder_path = os.path.join(CONFIG["DATA_PATH"], 'downloaded_raw', site, year, day)

		s3_filename_path = (CONFIG["S3_DATA_PATH"] + site + '/' + year + '/' + day + '/' + filename)
		status_file_path = os.path.join(download_folder_path, filename)
		print('Downloading status files for: {} {}'.format(site, day))

		if_not_then_make(download_folder_path)

		try:
			# print('Downloading from: S3://{} to {}........'.format(s3_filename_path, status_file_path),end='')
			download = s3.download_file(CONFIG["BUCKET_NAME"], s3_filename_path, status_file_path)

		except Exception as e:
			print('Could not download: {}'.format(s3_filename_path))
			print('Error: ',e)
			download = 1

		if (download == None):
			print('Succesfully downloaded status file(s) from', site)
		else:
			print('Could not download status file from {}. Filename: {}'.format(site, filename))
###############################################################################



###############################################################################
def download_log_file(site_dict):

	site = site_dict['name']
	s3 = boto3.client('s3',
		aws_access_key_id = CONFIG["AWS_ACCESS_KEY"],
		aws_secret_access_key = CONFIG["AWS_SECRET_ACCESS_KEY"])
	
	download_folder_path = os.path.join(CONFIG["DATA_PATH"], 'logs', site)
	if_not_then_make(download_folder_path)

	print('Downloading log file for: ',site)
	s3_filename_path = (CONFIG["S3_DATA_PATH"] + site + '/' + 'log.txt')
	log_file_path = os.path.join(download_folder_path, 'log.txt')
	# print(log_file_path)
	# sys.exit()

	try:
		print('Downloading from: S3://{} to {}........'.format(s3_filename_path, log_file_path),end='')
		download = s3.download_file(CONFIG["BUCKET_NAME"], s3_filename_path, log_file_path)

	except Exception as e:
		print('Could not download: {}'.format(s3_filename_path))
		print('Error: ',e)
		download = 1

	if (download == None):
		print('Succesfully downloaded log file from', site)
	else:
		print('Could not download log file from ',site)
###############################################################################



###############################################################################
def print_help_process_data():
	print("\nAPMS data processing script V0.1")
	print("Syntax: 2 Options...\n") 
	print("Option 1:		$ process_data [A]\n")
	print("Where [A] can be a site name, date range or number of days back")
	print("If only a site name is given, yesterday's data will be processed")
	print("If only a date range was given (or number of days back), the data for each site will be processed.\n")
	print("Option 2:		$ process_data [B] [C]\n")
	print("Where B is a site name and [C] is either a date range or number of days back\n\n")
###############################################################################

PWD = os.getcwd()
config_file_path = os.path.join(PWD,"config.json")	
CONFIG = load_config_file(config_file_path)
