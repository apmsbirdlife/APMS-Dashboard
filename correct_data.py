import pandas as pd
from classes import *
from data_plot import *
from datetime import timedelta, datetime
import shutil
from shared_functions import *

###############################################################################
# Global dictionary variable holding all constants
###############################################################################
global CONFIG


###############################################################################
# As the Raspberry Pi cannot always read the scale fast enough, it can
# get a few weights behind. This causes the timing between samples to 
# not be 10ms (100Hz) every time, sometimes a bit more sometimes a bit less. 
# The average is still 10ms over the event however. This function spaces
# the samples out at the average sampling period (10ms) to better represent
# true events, and for better future processing using FFT and the like.
###############################################################################
def fix_timestamp_index(scale):
	
	print("Spacing out timestamps evenly for ", scale.name)
	data = scale.weights.values
	time_diff = (scale.weights.index[-1] - scale.weights.index[0]) / len(scale.weights.index)

	# generate a new index with the desired time frequency
	first_timestamp = scale.weights.index[0]
	last_timestamp = scale.weights.index[-1]
	
	new_index = pd.date_range(start=first_timestamp+time_diff, end=last_timestamp, freq=time_diff)

	scale.weights = pd.Series(data, index=new_index)

	return scale
###############################################################################




###############################################################################
# This bug caused an overlap of data for some files. 
# This was fixed on 11/09/2023 so this function does not need to be run for data after this date
###############################################################################
def fix_overlap (scale_data_directory):

	print("Checking for overlap")
	scale_files_all = get_scale_files(scale_data_directory)
	scale_files = scale_files_all.copy()
	print("scale files before")
	print(scale_files)


	for scale_file in scale_files_all:
		if "fixed" in scale_file:
			print("removing ",scale_file)
			scale_files.remove(scale_file) 

	# print("scale files after")
	# print(scale_files)


	scale_files_copy = scale_files.copy()
	scale_file_delete_list = []

	for scale_file in scale_files:
		scale_file_path = os.path.join(scale_data_directory, scale_file)
		df = load_df_two_scales(scale_file_path)

		event_start_time = df.index[0]
		event_end_time = df.index[-1]
		scale_files_copy.remove(scale_file)
		
		for temp_scale_file in scale_files_copy:
			temp_scale_file_path = os.path.join(scale_data_directory, temp_scale_file)
			temp_df = load_df_two_scales (temp_scale_file_path)
			temp_event_start_time = temp_df.index[0]
			temp_event_end_time = temp_df.index[-1]
			# print("comparing {} to temp scale file {}".format(scale_file, temp_scale_file))
			# print("event start: {}   event end: {}".format(event_start_time,event_end_time))
			# print("temp event start: {}   temp event end: {}".format(temp_event_start_time,temp_event_end_time))
			
			if temp_event_end_time < event_start_time or temp_event_start_time > event_end_time:
				pass 
				# print("no overlap")
			else:
				print("overlap detected between {} and {}".format(scale_file,temp_scale_file))

				scale_file_delete_list.append(scale_file_path)
				scale_file_delete_list.append(temp_scale_file_path)

				original_scale_1_weights = df['scale_1']
				original_scale_2_weights = df['scale_1']
				# print('original_scale_1_weights')
				# print(original_scale_1_weights)


				temp_scale_1_weights = temp_df['scale_1']
				temp_scale_2_weights = temp_df['scale_1']
				new_df = pd.concat([df,temp_df])
				

				new_df.sort_index(inplace=True)
				# new_df.drop_duplicates(inplace=True)

				new_file_path = os.path.join(scale_data_directory, 'S_fixed_' + scale_file) 
				# new_df.to_csv(new_file_path)
				
				epoch_list = []
				for temp_timestamp in new_df.index:

					# This sneaky move is because we are currently using "GMT" for everything.
					# "GMT" being SA time in this case. So convert back to real GMT
					temp_timestamp = temp_timestamp - timedelta(hours=2)
					epoch_timestamp = temp_timestamp.timestamp()
					epoch_list.append(epoch_timestamp)
				
				new_df['epoch_timestamp'] = epoch_list
				new_df.to_csv(new_file_path, index=False, header=False, columns=['epoch_timestamp', 'scale_1', 'scale_2'])

	# Done with main for loop. Remove duplicates 
	scale_file_delete_list = list(set(scale_file_delete_list))

	# Move jump error files to its own directory
	for file_path in scale_file_delete_list:
		print("moving: ",file_path)
		
		error_path = os.path.join(scale_data_directory, 'overlap')
		if_not_then_make(error_path)		
		
		try:
			shutil.move(file_path, error_path)
		except:
			print("Could not move error file. Deleting file instead")
			os.remove(file_path)

	# Noew rename fixed files back to original filename
	scale_files = get_scale_files(scale_data_directory)
	for scale_file in scale_files:
		if "S_fixed_" in scale_file:
			old_file_path = os.path.join(scale_data_directory, scale_file)
			new_file_path = old_file_path.replace("S_fixed_", "")

			print("Renaming: {} to {}".format(old_file_path,new_file_path))
			shutil.move(old_file_path, new_file_path)

###############################################################################





################################################################################
# Due to some garbage characters being mistaken for large weights, scale files would be generated erroneously.
# This function checks for a large sudden spike of greater than 30.
#################################################################################
def check_and_remove_high_error_weight (scale_data_directory):

	print("Checking for high weight glitch error")
	scale_files_all = get_scale_files(scale_data_directory)
	scale_files = scale_files_all.copy()
	scale_file_delete_list = []
	error_path = os.path.join(scale_data_directory, 'big_weight_glitch')

	for scale_file in scale_files:
		scale_file_path = os.path.join(scale_data_directory, scale_file)
		
		print(scale_file_path)
		df = load_df_two_scales(scale_file_path)
	
		if not isinstance(df, pd.core.frame.DataFrame):
			print("Could not load scale file: ", scale_file_path)
			print("Moving on to next scale file...")
			continue

		for scale in ('scale_1', 'scale_2'):
			scale_weights = df[scale]			
			num_of_weights = len(df)

			for i in range(0,num_of_weights):
	
				if (i != 0):
					scale_weight_previous = scale_weights.iloc[i-1]
				else:
					scale_weight_previous = 0

				scale_weight = scale_weights.iloc[i]
				
				if (i != num_of_weights-1):
					scale_weight_next = scale_weights.iloc[i+1]
				else:
					scale_weight_next = 0

				if scale_weight > 50 and scale_weight_previous < CONFIG["MAX_DEAD_WEIGHT"] and scale_weight_next < CONFIG["MAX_DEAD_WEIGHT"]:

					print("Big weight glitch identified on {} of {} kg. File being removed".format(scale,scale_weight))
					if_not_then_make(error_path)		
					try:
						error_file_path = os.path.join(error_path, scale_file)
						os.remove(error_file_path)
					except:
						pass

					shutil.move(scale_file_path, error_path)
					
					break
	print("Done Checking for high weight glitch error")
################################################################################
# DONE
#################################################################################