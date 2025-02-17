from influxdb import InfluxDBClient
from datetime import datetime, timedelta
import os
import sys
import boto3
import traceback
import shutil
from shared_functions import *


###############################################################################
# Global dictionary variable holding all constants
###############################################################################
global CONFIG


###############################################################################
# Classes
###############################################################################
class System_State:
	def __init__(self):
		self.timestamp = None
		self.site_name = None
		self.cpu_temp = None
		self.cpu_load = None
		self.sd_used = None
		self.usb_used = None
		self.mem_used = None        
		self.arduino_last_boot = None
		self.rpi_last_boot = None
		self.mobile_num = None
		self.ambient_temp = None
		self._4V = None
		self._5V = None
		self._12V = None
		self._24V = None
###############################################################################



###############################################################################
# Function to create and return an influxDB client
###############################################################################
def get_influxdb_client ():
	client = InfluxDBClient(host=CONFIG["HOST_IP"], port=8086)
	# Create a new database (if it doesn't exist already)
	client.create_database('mydb')
	# Switch to the new database
	client.switch_database('mydb')
	# Define some data points
	return client
###############################################################################

###############################################################################
def write_status_files_to_influx (system_state_obj_list):
	
	# print_object(system_state_obj_list)
	# sys.exit()

	influxdb_client = get_influxdb_client()
	# print("There are {} states".format(len(system_state_obj_list)))
	for system_state_obj in system_state_obj_list:
		json_body = [
			{
				"measurement": "site_stats",
				"tags": {"site_name":system_state_obj.site_name},
				"time": system_state_obj.timestamp,
				"fields": 
				{
					"cpu_temp"          : system_state_obj.cpu_temp,
					"cpu_load"          : system_state_obj.cpu_load,
					"sd_used"           : system_state_obj.sd_used,
					"usb_used"          : system_state_obj.usb_used,
					"mem_used"          : system_state_obj.mem_used,
					"arduino_last_boot"	: system_state_obj.arduino_last_boot,
					"rpi_last_boot"   	: system_state_obj.rpi_last_boot,
					"mobile_num"        : system_state_obj.mobile_num,
					"ambient_temp"      : system_state_obj.ambient_temp,
					"_4V"               : system_state_obj._4V,
					"_5V"               : system_state_obj._5V,
					"_12V"              : system_state_obj._12V,
					"_24V"              : system_state_obj._24V
				}
			}
		]
		# print("json: ",json_body)

		# Write the data to the database
		output = influxdb_client.write_points(json_body)
		# print("output: ",output)
###############################################################################



# ##############################################################################
# def print_object (system_state_obj_list):
	
# 	for system_state_obj in system_state_obj_list:
		
# 		print("------------------------------------")
# 		print("timestamp (UTC):", system_state_obj.timestamp)
# 		print("Site name:", system_state_obj.site_name)
# 		print("cpu_temp: ",system_state_obj.cpu_temp)
# 		print("cpu_load: ",system_state_obj.cpu_load)
# 		print("SD storage used: ",system_state_obj.sd_used)
# 		print("USB storage used: ",system_state_obj.usb_used)
# 		print("Memory used: ",system_state_obj.mem_used)
# 		print("Arduino ON Time: ",system_state_obj.arduino_last_boot)
# 		print("Stored Mobile Number: ",system_state_obj.mobile_num)
# 		print("Ambient temperature: ",system_state_obj.ambient_temp)
# 		print("4V (SIM800L): ",system_state_obj._4V)
# 		print("5V (Raspberry Pi): ",system_state_obj._5V)
# 		print("12V (Router, Scales): ",system_state_obj._12V)
# 		print("24V (Solar Supply): ",system_state_obj._24V)
# ##############################################################################
	 









##############################################################################
def extract_status_data (day_log):

	system_state_obj = System_State()
	system_state_obj_list = []

	for line in day_log:

		if "Start of APMS Status Report - Date:" in line:
			date_str = line.split('Date:')[1].split()[0]
			time_str = line.split('Time:')[1].split()[0]
			
			# Create a datetime object holding the timestamp (In SA time)
			date_time = datetime.strptime(date_str + time_str, '%Y%m%d%H:%M:%S')
			
			# Convert to UTC
			# date_time = date_time - timedelta(hours=2)

			# Convert the UTC datetime object to a Unix timestamp (EPOCH)
			system_state_obj.timestamp = int(date_time.timestamp() * 1000000000)

			# print("timestamp:", system_state_obj.timestamp)

		elif "Site Name:" in line:
			system_state_obj.site_name = line.split(':')[-1].strip()
			# print("Site name:, system_state_obj.site_name)

		elif "CPU temperature:" in line:
			temp_str = line.split(':')[-1].strip()
			system_state_obj.cpu_temp = float(temp_str.split()[0])
			# print("cpu_temp: ",system_state_obj.cpu_temp)
		  
		elif "CPU load:" in line:
			temp_str = line.split(':')[-1].strip()
			system_state_obj.cpu_load = float(temp_str.split()[0])
			# print("cpu_load: ",system_state_obj.cpu_load)

		elif "SD storage used:" in line:
			temp_str = line.split(':')[-1].strip()
			system_state_obj.sd_used = float(temp_str.split()[0])
			# print("SD storage used: ",system_state_obj.sd_used)

		elif "USB drive storage used:" in line:
			temp_str = line.split(':')[-1].strip()
			system_state_obj.usb_used = float(temp_str.split()[0])
			# print("USB storage used: ",system_state_obj.usb_used)

		elif "Memory used:" in line:
			temp_str = line.split(':')[-1].strip()
			system_state_obj.mem_used = float(temp_str.split()[0])
			# print("Memory used: ",system_state_obj.mem_used)

		elif "Raspberry Pi last boot:" in line:
			temp_str_list = line.split() # split on white spaces
			# print(temp_str_list)
			rpi_last_boot_date = temp_str_list[4].strip()
			rpi_last_boot_date = rpi_last_boot_date.replace('-','/')
			rpi_last_boot_time = temp_str_list[5].strip()
			# print(rpi_last_boot_date + ' ' + rpi_last_boot_time)
			system_state_obj.rpi_last_boot = rpi_last_boot_date + ' - ' + rpi_last_boot_time
			




			# 2023-11-15 17:50:42
			# 2023/09/12 - 08:03:48
			# 2023A11A15E

		elif "Arduino boot time:" in line:

			temp_str_list = line.split() # split on white spaces
	
			if len(temp_str_list) == 5:	# New format

				arduino_last_boot_date = temp_str_list[3].strip()
				arduino_last_boot_date = arduino_last_boot_date.replace('-','/')
				arduino_last_boot_time = temp_str_list[4].strip()
				system_state_obj.arduino_last_boot = arduino_last_boot_date + ' - ' + arduino_last_boot_time
			
		elif "Stored Mobile Number:" in line:
			temp_str = line.split(':')
			system_state_obj.mobile_num = temp_str[1].strip()
			# print("Stored Mobile Number: ",system_state_obj.mobile_num)


		elif "Ambient temperature:" in line:
			temp_str = line.split(':')[1].strip()
			system_state_obj.ambient_temp = float(temp_str.split()[0])
			# print("Ambient temperature: ",system_state_obj.ambient_temp)


		elif "4V SIM800L Supply:" in line:
			temp_str = line.split(':')[1].strip()
			system_state_obj._4V = float(temp_str.split()[0])
			# print("4V (SIM800L): ",system_state_obj._4V)


		elif "5V (Raspberry Pi):" in line:
			temp_str = line.split(':')[1].strip()
			system_state_obj._5V = float(temp_str.split()[0])
			# print("5V (Raspberry Pi): ",system_state_obj._5V)

		elif "12V (Router, scales):" in line:
			temp_str = line.split(':')[1].strip()
			system_state_obj._12V = float(temp_str.split()[0])
			# print("12V (Router, Scales): ",system_state_obj._12V)

		elif "24V Solar Supply:" in line:
			temp_str = line.split(':')[1].strip()
			system_state_obj._24V = float(temp_str.split()[0])
			# print("24V (Solar Supply): ",system_state_obj._24V)

		elif "End of APMS Status Report" in line:
			system_state_obj_list.append(system_state_obj)
			# Recreate object to clear it
			system_state_obj = System_State()

	# print("Log File Anaylyzed. {} status_files were recorded.".format(len(system_state_obj_list)))
	return system_state_obj_list
##############################################################################






##############################################################################
def status_data_to_influx (site_dict, day_obj_list):

	site = site_dict['name']

	for day_obj in day_obj_list:

		day = day_obj.strftime("%Y%m%d")
		year = day[0:4]

		filename = day + '_STATUS.txt'
		file_path = os.path.join(CONFIG["DATA_PATH"], 'downloaded_raw', site, year, day, filename)
		print("Processing ", file_path)
		# file_path = os.path.join(status_file_directory,)

		if os.path.exists(file_path):
			try:
				with open(file_path, 'r') as f:
					day_log = f.readlines()
					system_state_obj_list = extract_status_data(day_log)
					print("Writing status data to InfluxDB {}".format(file_path))
					write_status_files_to_influx(system_state_obj_list)
			
			except Exception as e:
				print("Could not process status file: ",file_path)
				traceback.print_exc()
				continue

	print("Done loading status files")

##############################################################################



##############################################################################
def log_to_influx (site_dict):
	site_name = site_dict['name']
	influxdb_client = get_influxdb_client()

	file_path = os.path.join(CONFIG["DATA_PATH"], 'logs', site_name, 'log.txt')
	try:
		with open(file_path, 'r') as f:
			log = f.readlines()
			# each line starts with date and time. Example: "2023/10/20 19:36"
			for line in log:
				
				date_time   = line.split(' - ')[0]
				description = line.split(' - ')[1].strip()

				# Create a datetime object holding the timestamp (In SA time)
				input_format = "%Y/%m/%d %H:%M"
				timestamp_obj = datetime.strptime(date_time, input_format)
				timestamp = int(timestamp_obj.timestamp() * 1000000000)

				json_body = [
				{
					"measurement": "log",
					"tags": {"site_name":site_name},
					"time": timestamp,
					"fields": 
					{
						"description" : description,
						
					}
				}]

				# print("json: ",json_body)
				# Write the data to the database
				try:
					output = influxdb_client.write_points(json_body)
				except:
					print("Could not write penguin data to influx")

	except Exception as e:
		print("Could not open log file: ",file_path)
		# traceback.print_exc()
		# continue





##############################################################################
def penguin_data_to_influx (site_dict, day_obj_list):
	site = site_dict['name']
	influxdb_client = get_influxdb_client()

	data = {'timestamp': [], 'weight': [], 'direction': []}
	df_all_data = pd.DataFrame(data)
	# df_all_data.index = df_all_data.index.shift(-2, freq='H')


	# For each day, load the processed csv file, and add to the main df
	for day_obj in day_obj_list:

		day = day_obj.strftime("%Y%m%d")
		year = day[0:4]

		penguin_file_directory = os.path.join(CONFIG["DATA_PATH"], 'processed', site, year, day)

		# Add error data
		
		csv_file_path = os.path.join(penguin_file_directory, '{}_{}_processed_data.csv'.format(site,day))
		
		if os.path.exists(csv_file_path):
			
			print("Loading penguin file: ", csv_file_path)
			
			print("Getting meta data")
			with open(csv_file_path, 'r') as file:
				meta_data = file.readline()
			meta_data_to_influx(meta_data, day_obj, influxdb_client)
			
			
			print("Writing penguin data to InfluxDB...")
			df = pd.read_csv(csv_file_path, header=[1])
			for index, row in df.iterrows():
				
				timestamp_str = row['TIMESTAMP']
				timestamp_object = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
				timestamp = int(timestamp_object.timestamp() * 1000000000)

				weight = row['WEIGHT']
				# print("weight ", weight)

				direction = row['DIRECTION']
				# print("direction ", direction)
				
				json_body = [
				{
					"measurement": "penguins",
					"tags": {"site_name":site, "direction" : direction},
					"time": timestamp,
					"fields": 
					{
						"weight" : weight,
						
					}
				}]

				# print("json: ",json_body)
				# Write the data to the database
				try:
					output = influxdb_client.write_points(json_body)
				except:
					print("Could not write penguin data to influx")
			

		else:
			print("Could not open penguin file: ",csv_file_path)
##############################################################################



#############################################################################
def count_files (path):

	try:
        # Create a Path object for the directory
		directory = Path(path)
		# Count the number of files
		return sum(1 for item in directory.iterdir() if item.is_file())
	except FileNotFoundError:
		print("The specified directory does not exist.")
		return 0    
#############################################################################




##############################################################################
def meta_data_to_influx (meta_data, timestamp_obj, influxdb_client):

	timestamp = int(timestamp_obj.timestamp() * 1000000000)

	# EXAMPLE: Site: stony_point Total Number of Files: 6	Number of Unprocessed Files: 4 Total number of RFID tags: 1 Number of assigned RFID tags: 0
	
	site_name 				= meta_data.split("Site: ")[1].split()[0]
	number_of_scale_files	= meta_data.split("Total Number of Files: ")[1].split()[0]
	number_of_penguin_files	= meta_data.split("Number of Penguin Files: ")[1].split()[0]
	number_of_tags			= meta_data.split("Total number of RFID tags: ")[1].split()[0]
	number_of_assigned_tags	= meta_data.split("Number of assigned RFID tags: ")[1].split()[0]

	json_body = [
	{
		"measurement": "meta_data",
		"tags": {"site_name":site_name},
		"time": timestamp,
		"fields": 
		{
			"number_of_scale_files" : int(number_of_scale_files),	
			"number_of_penguin_files" : int(number_of_penguin_files),
			"number_of_tags" : int(number_of_tags),			
			"number_of_assigned_tags" : int(number_of_assigned_tags),
		}
	}]


	try:
		output = influxdb_client.write_points(json_body)
	except:
		print("Could not write to influxdb")
##############################################################################




##############################################################################
def daily_avg_to_influx (site, day_obj_list):
	
	influxdb_client = get_influxdb_client()

	data = {'DATE': [], 'AVG_OUT_TO_OCEAN': [], 'AVG_BACK_FROM_OCEAN': []}
	df_all_data = pd.DataFrame(data)

	# For each day, load the processed csv file, and add to the main df
	for day_obj in day_obj_list:
		day = day_obj.strftime("%Y%m%d")
		year = day[0:4]

		# timestamp = day_obj.timestamp()
		timestamp = int(day_obj.timestamp() * 1000000000)


		csv_file_path = os.path.join(os.getcwd(), 'data','processed', site, year, day, '{}_{}_processed_data.csv'.format(site,day))
		if os.path.exists(csv_file_path):
			print(csv_file_path)
			df = pd.read_csv(csv_file_path, header=[1])
			df_out_to_ocean = df[df['DIRECTION'] == 'out_to_ocean']
			avg_out_to_ocean = df_out_to_ocean['WEIGHT'].median()
			number_penguins_out_to_ocean = len(df_out_to_ocean)
			max_weight_out_to_ocean = df_out_to_ocean['WEIGHT'].max()
			min_weight_out_to_ocean = df_out_to_ocean['WEIGHT'].min()

			df_back_from_ocean = df[df['DIRECTION'] == 'back_from_ocean']
			avg_back_from_ocean = df_back_from_ocean['WEIGHT'].median()
			number_penguins_back_from_ocean = len(df_back_from_ocean)
			max_weight_back_from_ocean = df_back_from_ocean['WEIGHT'].max()
			min_weight_back_from_ocean = df_back_from_ocean['WEIGHT'].min()

			json_body = [
			{
				"measurement": "avg_penguins",
				"tags": {"site_name":site},
				"time": timestamp,
				"fields": 
				{
					"avg_out_to_ocean"          		: avg_out_to_ocean,
					"number_penguins_out_to_ocean"		: number_penguins_out_to_ocean,
					"max_weight_out_to_ocean"			: max_weight_out_to_ocean,
					"min_weight_out_to_ocean"      		: min_weight_out_to_ocean,
					"avg_back_from_ocean"          		: avg_back_from_ocean,
					"number_penguins_back_from_ocean"   : number_penguins_back_from_ocean,
					"max_weight_back_from_ocean"        : max_weight_back_from_ocean,
					"min_weight_back_from_ocean"		: min_weight_back_from_ocean,
				}
			}]

			# print("JSON: \n", json_body)
			try:
				output = influxdb_client.write_points(json_body)
			except:
				print("Could not write points for ", day_obj)







##############################################################################
##############################################################################
if __name__ == "__main__":
	
	now = datetime.now()
	time_now = now.strftime("%H:%M:%S")
	day = now.strftime("%Y%m%d")
	
	print("#########################################")
	print ("#### 	   APMS Dashboard	    #####")
	print ("#### Date: {}   Time: {} ####".format(day,time_now))
	print("#########################################")



	# error_data_to_influx("C:\\Users\\pierr\\apms_data_processing\\data\\processed\\bird_island\\2024\\20240106")



	sites, day_obj_list = analyze_arguments()
	# sites = CONFIG["SITES"]
	# day_obj_list = date_range_to_object_list(date_range = '20230601-20231101')
	# day_obj_list = days_back_to_object_list(days_back = 10)

	for site_dict in sites:

		if CONFIG["DOWNLOAD_STATUS_FILES"] == True:
			download_status_files(site_dict, day_obj_list)
		
		if CONFIG["DOWNLOAD_LOG_FILE"] == True:
			download_log_file(site_dict)

		if CONFIG["LOG_TO_INFLUX"] == True:
			log_to_influx (site_dict)	

		if CONFIG["STATUS_TO_INFLUX"] == True:
			status_data_to_influx (site_dict, day_obj_list)

		if CONFIG["PENGUINS_TO_INFLUX"] == True:
			penguin_data_to_influx (site_dict, day_obj_list)

	print("#########################################")
	print ("#### APMS Dashboard Script Finished ####")
	print ("#### Date: {}   Time: {} ####".format(day,time_now))
	print("#########################################")
##############################################################################
##############################################################################




