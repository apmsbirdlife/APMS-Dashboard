# This script generates two plots for each: A short term plot and a long term plot.
# The time periods covered by the two plots can be adjusted in the config.json file
# These plots are then uploaded to the cloud for display on the website

import os
import sys
from datetime import datetime, timedelta
from shared_functions import *
from data_plot import *

###############################################################################
# Global dictionary variable holding all constants
###############################################################################
global CONFIG


###############################################################################
def generate_save_upload_long_term_plot (site_dict, local_save_dir):

	site_name = site_dict['name']
	# start_date = site_dict['start_date']
	
	# day_obj_start = datetime.strptime(start_date, "%Y%m%d") = current_datetime - timedelta(days=30 * 6)
	today = datetime.now()
	today_str = today.strftime("%Y%m%d")
	one_day = timedelta(days=1)
	day_obj_end = today - one_day
	day_obj_start = day_obj_end - timedelta(days=(30*6))
	day_obj_list = get_day_object_list(day_obj_start, day_obj_end)
	
	filename = '{}_long_term.png'.format(site_name)

	local_file_path = os.path.join(local_save_dir, filename)

	trend_line = plot_daily_avg(
		site_dict = site_dict, 
		day_obj_list = day_obj_list, 
		title = 'Average daily weight of incoming/outgoing penguins for Stony Point', 
		save_path = local_file_path, 
		show_num_penguins = True)


	s3_file_path = 'APMS/website/' + site_name + '/' + filename 
	upload_to_cloud(s3_file_path, local_file_path)

	return trend_line
###############################################################################










###############################################################################
def generate_save_upload_short_term_plot (site_dict, trend_line, local_save_dir):

	site_name = site_dict['name']
	day_obj_list = days_back_to_object_list(7)
	today = datetime.now()
	today_str = today.strftime("%Y%m%d")
	
	filename = '{}_short_term.png'.format(site_name)

	local_file_path = os.path.join(local_save_dir, filename)

	plot_daily_avg(
		site_dict = site_dict, 
		day_obj_list = day_obj_list, 
		title = 'Average daily weight of incoming/outgoing penguins for Stony Point', 
		save_path = local_file_path,
		trend_line = trend_line, 
		show_num_penguins = True)

	
	s3_file_path = 'APMS/website/' + site_name + '/' + filename 
	upload_to_cloud(s3_file_path, local_file_path)

###############################################################################



##############################################################################
def upload_to_cloud(s3_file_path, local_file_path):
	
	s3 = boto3.client('s3')
	bucket_name = CONFIG["BUCKET_NAME"]
	object_key = s3_file_path

	try:
		s3.upload_file(local_file_path, bucket_name, object_key)
		print(f'Successfully uploaded {local_file_path} to s3://{bucket_name}/{object_key}')
	except Exception as e:
		print(f'Error uploading {local_file_path} to S3: {str(e)}')

##############################################################################




##############################################################################
if __name__ == "__main__":

	now = datetime.now()
	_time = now.strftime("%H:%M:%S")
	day = now.strftime("%Y%m%d")
	print("#########################################")
	print ("#### Website Plot Generating Script #####")
	print ("#### Date: {}   Time: {} ####".format(day,_time))
	print("#########################################")

	SITES = CONFIG["SITES"]

	for site_dict in SITES:

		site_name = site_dict['name']
		local_save_dir = os.path.join(CONFIG["DATA_PATH"], 'website', site_name)
		if_not_then_make(local_save_dir)

		print("Generating long term plot for ", site_name)
		trend_line = generate_save_upload_long_term_plot(site_dict, local_save_dir)
	
		print("Generating short term plot for ", site_name)
		generate_save_upload_short_term_plot(site_dict, trend_line, local_save_dir)
###############################################################################


