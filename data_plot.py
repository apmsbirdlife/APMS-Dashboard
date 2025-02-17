###############################################################################
# Functions used for plotting of raw data
###############################################################################
import os
import sys
import matplotlib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from rfid import get_rfid_series
from shared_functions import *

import matplotlib.dates as mdates
###############################################################################
# These plotting functions were used during testing.
###############################################################################


###############################################################################
# Global dictionary variable holding all constants
###############################################################################
global CONFIG
SCALES = ('scale_1','scale_2')
SAMPLING_FREQ = 100

###############################################################################



###############################################################################
def plot_scale_data(scale_data):
	
	fig, ax1 = plt.subplots()
	# print("scale.weights", scale.weights)
	ax1.plot(scale_data.index, scale_data, color='blue')
	plt.show()
###############################################################################

###############################################################################
def plot_scale_data2(scale, scale_2 = None):
	
	if scale_2 == None:
		fig, ax1 = plt.subplots()
		# print("scale.weights", scale.weights)
		ax1.plot(scale.weights.index, scale.weights, color='blue')
	

	else:
		fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 5), sharex=True)

		# Plot the first subplot	ax1.plot(scale.weights.index, scale.weights, color='blue')
		ax1.plot(scale.weights.index, scale.weights, color='blue')
		ax2.plot(scale_2.weights.index, scale_2.weights, color='blue')

	plt.show()
###############################################################################





###############################################################################
def plot_with_transitions (scale_data,transitions,title="plot with transitions"):


	fig, ax1 = plt.subplots()
	fig.set_size_inches(13, 6)
   
	# Plot the data on the subplots
	ax1.plot(scale_data.index, scale_data, color='blue')

	for transition_obj in transitions:

		if (transition_obj.transition_type == "on"):
			ax1.axvline(x=transition_obj.start_time, color='red', linewidth=1)
			ax1.axvline(x=transition_obj.end_time, color='red', linewidth=2)
		
		elif (transition_obj.transition_type == 'off'):
			ax1.axvline(x=transition_obj.start_time, color='blue', linewidth=1)
			ax1.axvline(x=transition_obj.end_time, color='blue', linewidth=2)
	ax1.set_title(title)
	plt.show()
###############################################################################




###############################################################################
def plot_with_avg_transitions (scale_data, transitions, title="plot with avg transitions"):
# ax1 = plot()
# ax1.plot(scale_data.index, scale_data, color='blue')
	fig, ax1 = plt.subplots()
   
# Plot the data on the subplots
	ax1.plot(scale_data.index, scale_data, color='blue')
# #ax2.plot(df.index, df['sc

	for transition_obj in transitions:

		timestamp = (transition_obj.end_time-transition_obj.start_time)/2 + transition_obj.start_time
		# print("Timestamp: {}  Type: {}".format(timestamp,transition_obj.transition_type))

		if (transition_obj.transition_type == "on"):
			ax1.axvline(x=((transition_obj.end_time-transition_obj.start_time)/2+transition_obj.start_time), color='red', linewidth=1)
			
		elif (transition_obj.transition_type == 'off'):
			ax1.axvline(x=((transition_obj.end_time-transition_obj.start_time)/2+transition_obj.start_time), color='black', linewidth=1)

		else:
			pass


	ax1.set_title(title)
	# fig.canvas.manager.full_screen_toggle() # toggle fullscreen mode
	plt.tight_layout() # adjust layout of plot
	
	fig.set_size_inches(10, 5) # set size of plot window
	plt.show()

###############################################################################








###############################################################################

def plot_both_without_transitions (scale_1_weights, scale_2_weights, title="plot of both"):

	fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True)	
	fig.set_size_inches(13, 6)
   
	# Plot the data on the subplots
	ax1.plot(scale_1_weights.index, scale_1_weights, color='blue')

	# Plot the data on the subplots
	ax2.plot(scale_2_weights.index, scale_2_weights, color='blue')

	ax1.set_ylim(0,8)
	ax2.set_ylim(0,8)
	fig.suptitle(title)
	plt.show()

###############################################################################


###############################################################################
# def plot_sub_events(scale):
# 	plt.plot(scale.weights.index, scale.weights)
# 	for i in range(0,len(scale.sub_events_list)):
# 		start_time = scale.sub_events_list[i][0]
# 		end_time = scale.sub_events_list[i][1]
# 		plt.axvline(x=start_time, color='r', linestyle='--')
# 		plt.axvline(x=end_time, color='b', linestyle='--')
# 	plt.show()
###############################################################################





###############################################################################
def plot_all_transitions (scale_1, scale_2):
	
	series_1 = scale_1.weights
	scale_1_transitions = scale_1.transitions

	series_2 = scale_2.weights
	scale_2_transitions = scale_2.transitions

	fig, (ax_1, ax_2) = plt.subplots(nrows=2, ncols=1, sharex=True)	
	ax_1.plot(series_1.index, series_1, color='blue')
	ax_2.plot(series_2.index, series_2, color='blue')
	
	for transition_obj in scale_1_transitions:
		
		if (transition_obj.transition_type == "on"):
			ax_1.axvline(x=transition_obj.start_time, color='red', linewidth=1)
			ax_1.axvline(x=transition_obj.end_time, color='red', linewidth=2)
		
		elif (transition_obj.transition_type == 'off'):
			ax_1.axvline(x=transition_obj.start_time, color='blue', linewidth=1)
			ax_1.axvline(x=transition_obj.end_time, color='blue', linewidth=2)

		else:
			print("transition type error")

	for transition_obj in scale_2_transitions:
		
		if (transition_obj.transition_type == "on"):
			ax_2.axvline(x=transition_obj.start_time, color='red', linewidth=1)
			ax_2.axvline(x=transition_obj.end_time, color='red', linewidth=2)
		
		elif (transition_obj.transition_type == 'off'):
			ax_2.axvline(x=transition_obj.start_time, color='blue', linewidth=1)
			ax_2.axvline(x=transition_obj.end_time, color='blue', linewidth=2)

		else:
			print("transition type error")
	
	plt.show()


   



def plot_delta_t (scale, title = "delta t"):
	time_diffs = scale.weights.index.to_series().diff()
	diffs_ns = time_diffs.iloc[1:] # Throw away the NaN value
	diffs_ms = diffs_ns / 1000000


	fig, ax1 = plt.subplots()
	fig.set_size_inches(15, 6)
   
	# Plot the data on the subplots
	ax1.plot(diffs_ms.index, diffs_ms, color='blue')

	# ax1.set_ylim(0,0.025)


	# ax1.set_title(title)
	plt.show()



	# plt.plot(diffs)	

	# fig = plt.figure(figsize=(13, 4))  # set size of figure
	# # plt.xlabel('Time')
	# # plt.ylabel('Time difference')
	# # plt.title(title)
	# plt.show()



def plot_fft(df):

	window_size = 10
	rolling_avg_1 = df['scale_1'].rolling(window_size, center=True).mean()
	df['scale_1'] = df['scale_1'] - rolling_avg_1

	# Get the sampling rate from the timestamp index
	sampling_rate = SAMPLING_FREQ

	# Compute the FFT for each column
	fft_scale1 = np.fft.fft(df['scale_1'])
	fft_scale2 = np.fft.fft(df['scale_2'])

	# Compute the frequency range for plotting
	freq_range = np.fft.fftfreq(len(df), d=1/sampling_rate)

	# Create a figure with four subplots
	fig, axs = plt.subplots(2, 2, figsize=(12, 8))

	# Plot the time domain signal for scale_1
	axs[0, 0].plot(df.index, df['scale_1'])
	axs[0, 0].set_title('Time Domain of Scale 1')
	axs[0, 0].set_xlabel('Time (s)')
	axs[0, 0].set_ylabel('Value')

	# Plot the FFT for scale_1
	axs[0, 1].plot(freq_range, np.abs(fft_scale1))
	axs[0, 1].set_title('FFT of Scale 1')
	axs[0, 1].set_xlabel('Frequency (Hz)')
	axs[0, 1].set_ylabel('Amplitude')

	# Plot the time domain signal for scale_2
	axs[1, 0].plot(df.index, df['scale_2'])
	axs[1, 0].set_title('Time Domain of Scale 2')
	axs[1, 0].set_xlabel('Time (s)')
	axs[1, 0].set_ylabel('Value')

	# Plot the FFT for scale_2
	axs[1, 1].plot(freq_range, np.abs(fft_scale2))
	axs[1, 1].set_title('FFT of Scale 2')
	axs[1, 1].set_xlabel('Frequency (Hz)')
	axs[1, 1].set_ylabel('Amplitude')

	# Set the x-axis limits for the time domain plots
	x_min = df.index.min()
	x_max = df.index.max()
	axs[0, 0].set_xlim([x_min, x_max])
	axs[1, 0].set_xlim([x_min, x_max])

	# Adjust subplot spacing and display the figure
	fig.tight_layout()
	plt.show()


###############################################################################
def plot_csv_file(csv_file_path):

	df = pd.read_csv(csv_file_path, header=None, names=['timestamp', 'scale_1', 'scale_2'])

	# Set 'timestamp' column as the index
	df.set_index('timestamp', inplace=True)
	df.index = pd.to_datetime(df.index, unit='s', utc=True)
	df.index = df.index.shift(2, freq='H')
	# print(type(series))
	scale_1_weights = df['scale_1']
	scale_2_weights = df['scale_2']

	fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True)	
	fig.set_size_inches(13, 6)
   
	# Plot the data on the subplots
	ax1.plot(scale_1_weights.index, scale_1_weights, color='blue')

	# Plot the data on the subplots
	ax2.plot(scale_2_weights.index, scale_2_weights, color='blue')

	ax1.set_ylim(0,5)
	ax2.set_ylim(0,5)
	plt.show()
###############################################################################


###############################################################################
def plot_daily_avg(site_dict, day_obj_list, title = None, save_path = None, trend_line = None, show_num_penguins = True):
	
	site = site_dict['name']
	data_path = CONFIG["DATA_PATH"]

	# Create a dataframe that will hold the averages and be used for plotting
	# Index used for this dataframe will just be integers
	data = {'DATE': [], 'AVG_OUT_TO_OCEAN': [], 'AVG_BACK_FROM_OCEAN': []}
	df_all_data = pd.DataFrame(data)

	# For each day, load the processed csv file, and add to the main df
	for day_obj in day_obj_list:
		day = day_obj.strftime("%Y%m%d")
		year = day[0:4]

		csv_file_path = os.path.join(data_path,'processed', site, year, day, '{}_{}_processed_data.csv'.format(site,day))
		
		# print("csv file path: ", csv_file_path)

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
		
			entry = {'DATE': [day], 
			'AVG_OUT_TO_OCEAN': [avg_out_to_ocean], 
			'NUM_PENGUINS_TO_OCEAN':[number_penguins_out_to_ocean],
			'MAX_OUT_TO_OCEAN' : [max_weight_out_to_ocean],
			'MIN_OUT_TO_OCEAN' : [min_weight_out_to_ocean],

			'AVG_BACK_FROM_OCEAN': [avg_back_from_ocean],
			'NUM_PENGUINS_FROM_OCEAN':[number_penguins_back_from_ocean],
			'MAX_BACK_FROM_OCEAN' : [max_weight_back_from_ocean],
			'MIN_BACK_FROM_OCEAN' : [min_weight_back_from_ocean]}
			
			df_entry = pd.DataFrame(entry)
			
			df_all_data = pd.concat([df_all_data, df_entry], ignore_index=True)

			df_all_data['DATE'] = pd.to_datetime(df_all_data['DATE'])

	plt.figure(figsize=(40, 10))  # Adjust the values (width, height) as needed

	df_all_data.set_index('DATE', inplace=True)
	df_all_data = df_all_data.sort_values('DATE')

	if show_num_penguins == True:
		for i in range(0,len(df_all_data.index)):

			# plt.text(x-position, y-position, data to print)
			plt.text(df_all_data.index[i], 
				df_all_data['AVG_OUT_TO_OCEAN'][i]-0.05, 
				round(df_all_data['NUM_PENGUINS_TO_OCEAN'][i]), 
				color = 'red', 
				ha='center', 
				va='top')

			plt.text(df_all_data.index[i], 
				df_all_data['AVG_BACK_FROM_OCEAN'][i]+0.05, 
				round(df_all_data['NUM_PENGUINS_FROM_OCEAN'][i]), 
				color = 'blue', 
				ha='center', 
				va='bottom')

	
	plt.plot(df_all_data.index, df_all_data['AVG_OUT_TO_OCEAN'], label = 'avg going out to ocean', color = 'red', linestyle='-', marker = 'o', markersize = 4,linewidth=1)
	# plt.plot(df_all_data.index, df_all_data['MAX_OUT_TO_OCEAN'], label = 'max weight out to ocean', color = 'red', linestyle='--', marker = 'o', markersize = 1,linewidth=1)
	# plt.plot(df_all_data.index, df_all_data['MIN_OUT_TO_OCEAN'], label = 'min weight out to ocean', color = 'red', linestyle='--', marker = 'o', markersize = 1, linewidth=1)
	
	plt.plot(df_all_data.index, df_all_data['AVG_BACK_FROM_OCEAN'], label = 'avg coming back from ocean', color = 'blue', linestyle='-', marker = 'o', markersize = 4,linewidth=1)
	# plt.plot(df_all_data.index, df_all_data['MAX_BACK_FROM_OCEAN'], label = 'max weight back from ocean', color = 'blue', linestyle='--', marker = 'o', markersize = 1,linewidth=1)
	# plt.plot(df_all_data.index, df_all_data['MIN_BACK_FROM_OCEAN'], label = 'min weight back from ocean', color = 'blue', linestyle='--', marker = 'o', markersize = 1, linewidth=1)
	
	# plt.scatter(df_all_data.index, df_all_data['AVG_BACK_FROM_OCEAN'],  color = 'blue')
	# plt.scatter(df_all_data.index, df_all_data['MIN_BACK_FROM_OCEAN'], color = 'blue', s=1)
	# plt.plot(df_all_data.index, df_all_data['AVG_BACK_FROM_OCEAN'], label = 'coming back from ocean', color = 'blue')


	# If no trend line was sent as a parameter, create one for the currently selected data and return that trend line
	if trend_line == None:
		trend_out_to_ocean = df_all_data['AVG_OUT_TO_OCEAN'].median()
		trend_back_from_ocean = df_all_data['AVG_BACK_FROM_OCEAN'].median()
		trend_line = {'out_to_ocean':trend_out_to_ocean, 'back_from_ocean':trend_back_from_ocean}

	if len(trend_line) == 2:
		plt.axhline(y=trend_line['out_to_ocean'], color='red', linestyle='--', label = 'long term avg (going out to ocean)')
		plt.axhline(y=trend_line['back_from_ocean'], color='blue', linestyle='--', label = 'long term avg (coming back from ocean)')





	plt.xlabel('Date', fontsize=30)
	plt.ylabel('Weight [kg]', fontsize=30)

	plt.title('Average daily weight of incoming/outgoing penguins for: {}'.format(site), fontsize=35)
	
	# date_labels = df_all_data.index.strftime('%Y-%m-%d')
	# plt.xticks(df_all_data.index, date_labels, rotation=45)  # Set the x-axis ticks and labels with rotation for better readability
	# plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
	plt.xticks(fontsize=25)
	plt.yticks(fontsize=25)
	plt.ylim(CONFIG["MIN_PENGUIN_WEIGHT"], CONFIG["MAX_PENGUIN_WEIGHT"])  # Set y-axis limits
	plt.legend(fontsize=20)


	if save_path:
		
		plt.savefig(save_path)

	else:
		plt.show()

	return trend_line




###############################################################################


# This plots all the scale files and RFID files in the data folder directory
def plot_all_data_folder ():
	data_path = CONFIG["DATA_PATH"]

	rfid_data_path = os.path.join(data_path	, 'temp', 'rfid')
	scale_data_path = os.path.join(data_path, 'temp', 'scale')

	scale_files = os.listdir(scale_data_path)
	rfid_files = os.listdir(rfid_data_path)

	fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True)	
	fig.set_size_inches(13, 6)


	try:
		rfid_series = get_rfid_series(rfid_data_path)
		# rfid_series.index = rfid_series.index.shift(2, freq='H')
		
		# print(rfid_series)	
	except Exception as e:
		print("Could not create rfid series: ",e)

	# Now check if any tags appeared more than once
	# use Series.value_counts() to get a series of counts

	unique_rfid = rfid_series.unique()
	# colours = plt.cm.viridis(np.linspace(0, 1, len(rfid_series)))

	# print(rfid_series)
	for i in range(0, len(rfid_series)):
		ax1.axvline(x=rfid_series.index[i] , color='red', linewidth=1.5)
		ax2.axvline(x=rfid_series.index[i] , color='red', linewidth=1.5)

	for scale_file in scale_files:
		
		if (scale_file.startswith('S') and scale_file.endswith('.csv') ):
			pass
		else:
			continue

		csv_file_path = os.path.join(scale_data_path, scale_file)
		
		df =load_df_two_scales(csv_file_path)
		scale_1_weights = df['scale_1']
		scale_2_weights = df['scale_2']

		# Plot the data on the subplots
		ax1.plot(scale_1_weights.index, scale_1_weights, color='blue')

		# Plot the data on the subplots
		ax2.plot(scale_2_weights.index, scale_2_weights, color='blue')

		ax1.set_ylim(0,8)
		ax2.set_ylim(0,8)
	plt.show()
###############################################################################



###############################################################################
def plot_with_rfid (site_dict, day_obj_list, hide_test_tags = True):
	
	site = site_dict['name']

	scale_files = []
	rfid_files = []

	data_path = CONFIG["DATA_PATH"]
	
	fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True)	
	fig.set_size_inches(13, 6)

	for day_obj in day_obj_list:
		day = day_obj.strftime("%Y%m%d")
		year = day[0:4]
	
		scale_data_path = os.path.join(data_path, 'processing', site, year, day, 'scale')
		rfid_data_path = os.path.join(data_path, 'processing', site, year, day, 'rfid')

		if os.path.exists(scale_data_path):
			scale_files = os.listdir(scale_data_path)
		else:
			print(f"Scale directory {scale_data_path} not found")
			continue



		if os.path.exists(rfid_data_path):
			rfid_files = os.listdir(rfid_data_path)

		# print("Loading RFID tags")
		try:
			rfid_series = get_rfid_series(rfid_data_path)
			for rfid_timestamp, tag in rfid_series.items(): 
				if (tag not in CONFIG["TEST_TAGS"]):
					ax1.axvline(x=rfid_timestamp , color='red', linewidth=1.5)
					ax2.axvline(x=rfid_timestamp , color='red', linewidth=1.5)

		except Exception as e:
			print("Could not create rfid series: ",e)
			break

		

		for scale_file in scale_files:

			if (scale_file.startswith('S') and scale_file.endswith('.csv') ):
				pass
			else:
				continue

			csv_file_path = os.path.join(scale_data_path, scale_file)

			# print("csv file: ")
			# print(csv_file_path)

			df = load_df_two_scales (csv_file_path)
			

			# print(df)


			scale_1_weights = df['scale_1']
			scale_2_weights = df['scale_2']
		
			formatter = mdates.DateFormatter('%m/%d %T %Z', tz=df.index.tz)
			plt.gca().xaxis.set_major_formatter(formatter)

			# Plot the data on the subplots
			# ax1.scatter(scale_1_weights.index, scale_1_weights, color='blue', s=10)
			series_1 = scale_1_weights[scale_1_weights < 40]
			ax1.plot(series_1.index, series_1, color='blue')

			# Plot the data on the subplots
			series_2 = scale_2_weights[scale_2_weights < 40]
			ax2.plot(series_2.index, series_2, color='blue')

			ax1.set_ylim(0,10)
			ax2.set_ylim(0,10)
	
	plt.show()


###############################################################################
def plot_with_options(scale, scale_2 = None, sub_events = False, transitions = False, rfid_series = None):
	
	fig, (ax_1, ax_2) = plt.subplots(nrows=2, ncols=1, sharex=True)	

	if scale_2 != None:
		ax_2.plot(scale_2.weights.index, scale_2.weights, color='blue')
		ax_1.plot(scale.weights.index, scale.weights, color='blue')
	
	elif scale.name == 'scale_1':
		ax_1.plot(scale.weights.index, scale.weights, color='blue')
	
	elif scale.name == 'scale_2':
		ax_2.plot(scale.weights.index, scale.weights, color='blue')
		
#######################################
	if sub_events == True:

		if scale_2 != None:

			for i in range(0,len(scale_2.sub_events_list)):
				start_time = scale_2.sub_events_list[i][0]
				end_time = scale_2.sub_events_list[i][1]
				ax_2.axvline(x=start_time, color='r', linestyle='--')
				ax_2.axvline(x=end_time, color='b', linestyle='--')
	
			for i in range(0,len(scale.sub_events_list)):
				start_time = scale.sub_events_list[i][0]
				end_time = scale.sub_events_list[i][1]
				ax_1.axvline(x=start_time, color='r', linestyle='--')
				ax_1.axvline(x=end_time, color='b', linestyle='--')
	
		elif scale.name == 'scale_1':
	
			for i in range(0,len(scale.sub_events_list)):
				start_time = scale.sub_events_list[i][0]
				end_time = scale.sub_events_list[i][1]
				ax_1.axvline(x=start_time, color='r', linestyle='--')
				ax_1.axvline(x=end_time, color='b', linestyle='--')
	
		elif scale.name == 'scale_2':
	
			for i in range(0,len(scale.sub_events_list)):
				start_time = scale.sub_events_list[i][0]
				end_time = scale.sub_events_list[i][1]
				ax_2.axvline(x=start_time, color='r', linestyle='--')
				ax_2.axvline(x=end_time, color='b', linestyle='--')
#######################################
	if transitions == True:
		pass
#######################################

	if rfid_series:
		for rfid_timestamp, tag in rfid_series.items(): 
			if (tag not in CONFIG["TEST_TAGS"]):
				ax1.axvline(x=rfid_timestamp , color='red', linewidth=1.5)
				ax2.axvline(x=rfid_timestamp , color='red', linewidth=1.5)

#######################################




	plt.show()
###############################################################################
