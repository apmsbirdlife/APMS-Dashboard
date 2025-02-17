import pandas as pd
from data_plot import *
from classes import *
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks

###############################################################################
# Global dictionary variable holding all constants
###############################################################################
global CONFIG


# typical penguin walk has frequency of about 2 - 5 Hz
# At 2 Hz, to get one complete waveform, we need 0.5 seconds of data

###############################################################################
def find_weight (scale, timestamp_1, timestamp_2):
	scale_data = scale.weights.loc[timestamp_1:timestamp_2]


####################### DEBUG #########################################
	# print("Data being analyzed")
	# plot_scale_data(scale_data)
	# print("This is the scale data we will look at to figure out the weight")
	# print("std dev is ",scale_data.std())
	# plt.plot(scale_data.index, scale_data)
	# plt.show()
#######################################################################

	weight_obj = Weight()


	# print("timestamp_1 ", timestamp_1)
	# print("timestamp_2 ", timestamp_2)
	weight_time = (timestamp_2 - timestamp_1).total_seconds()
	# print('tbs ',weight_time)
	if (weight_time < CONFIG["MIN_DURATION_VALID_WEIGHT"]):
		weight_obj.weight = scale_data.mean()
		weight_obj.weight_type = 'time_too_short' 

		print("Time too short")

		return weight_obj

		
	########### Determining best window size ##############
	avg_penguin_period = (CONFIG["PENGUIN_WALKING_PERIOD_MIN"] + CONFIG["PENGUIN_WALKING_PERIOD_MAX"])/2
	window_size_s = avg_penguin_period
	window_size = int(window_size_s * CONFIG["SAMPLING_FREQ"])
	rolling_std_dev = scale_data.rolling(window=window_size, center = True).std()

	
	
	# Create a mask with True when the window's std dev was greater than config MAX_STD_DEV
	# mask_static = (rolling_std_dev > CONFIG["STD_DEV_STATIC"]) & (rolling_std_dev < CONFIG["STD_DEV_DYNAMIC"])
	mask_static = rolling_std_dev > CONFIG["STD_DEV_STATIC"]

	# Create a mask with True when the window's std dev was greater than min but less than max, thus a dynamic weight
	# mask_dynamic = (rolling_std_dev > CONFIG["STD_DEV_DYNAMIC"]) & (rolling_std_dev < CONFIG["STD_DEV_MAX"])
	mask_dynamic = (rolling_std_dev > CONFIG["STD_DEV_DYNAMIC"]) & (rolling_std_dev < CONFIG["STD_DEV_MAX"])

	# Now we crate a new series where each val contains the number of True's up to that point. The index is still list of timestamps
	# When the value remains the same, it means we are in a period of low std dev, as a True would have increased the value
	# Also each "count number" can be thought of as a uniqe index for that "group"
	cumul_sum_static = mask_static.cumsum()
	cumul_sum_dynamic = mask_dynamic.cumsum()

	consec_counts_static = cumul_sum_static.groupby(cumul_sum_static).count()
	consec_counts_dynamic = cumul_sum_dynamic.groupby(cumul_sum_dynamic).count()

	'''
	Example of what consec_counts looks like:

	0     78
	1      1
	2      1
	3      1
	4      1
	5      1
	6      1
	7      1
	8      1
	9      1
	10     1
	
	# Now we have a series, showing the number of times each group number appeared, showing
	# how long it was false, indicating how long it had a low std dev. Find the max number
	# of appearances, check that its long enough, find that index number, which is the "group name" and use that 
	index number to figure out ...
	
	Also, the first appearance of this unique group number, in cum_sum is the start of the low std dev time, and the last 
	appearance is the end of the low std dev time
	'''
	# The section with the longest static session is extracted
	max_consec_static = consec_counts_static.max()

	# The section with the longest dynamic session is extracted
	max_consec_dynamic = consec_counts_dynamic.max()


	# First check for Static weight
	if (max_consec_static > CONFIG["MIN_DURATION_VALID_WEIGHT"]*CONFIG["SAMPLING_FREQ"]):

		print("Static weight detected: ", end='')
		
		group_name = consec_counts_static.idxmax()
		static_series = cumul_sum_static[cumul_sum_static == group_name]
		timestamp_start = static_series.index[0]
		timestamp_end   = static_series.index[-window_size]
		
		weight_obj.weight = (scale_data.loc[timestamp_start:timestamp_end]).mean()
			
		if (weight_obj.weight < CONFIG["MAX_DEAD_WEIGHT"]):
			weight_obj.weight_type = 'dead_weight_static'
			print("dead_weight_static: ", weight_obj.weight)
			
		elif (weight_obj.weight > CONFIG["MAX_DEAD_WEIGHT"] and weight_obj.weight < CONFIG["MIN_PENGUIN_WEIGHT"]):
			weight_obj.weight_type = 'static_low'
			print("static_low: ", weight_obj.weight)

		elif (weight_obj.weight > CONFIG["MIN_PENGUIN_WEIGHT"]):
			weight_obj.weight_type = 'static'
			print("static", weight_obj.weight)

	# Dynamic weight
	elif (max_consec_dynamic > CONFIG["MIN_DURATION_VALID_WEIGHT"]*CONFIG["SAMPLING_FREQ"]):
		

		weight_obj.weight_type = 'dynamic'
		weight_obj.weight = get_dynamic_weight(scale_data)
		print("Dynamic weight detected: ", weight_obj.weight)
	
	else:
		weight_obj.weight = scale_data.mean()
		weight_obj.weight_type = "other:"
		print("other: ", weight_obj.weight)

	# ############ DEBUG ################
	# plt.plot(scale_data)
	# plt.axvline(x=timestamp_1,	color='r', linestyle='--')
	# plt.axvline(x=timestamp_2, 	color='b', linestyle='--')
	# plt.show()
	# pd.set_option('display.max_rows', 250)
	###################################
	###############################################################################

	return weight_obj


def get_dynamic_weight (scale_data):

	weights = []
	peak_timestamps, var = find_peaks(scale_data, height = 0, prominence=0.05)
	num_peaks = len(peak_timestamps)
	
	peak_timestamps = scale_data.index[peak_timestamps]
	# plt.plot(scale_data.index, scale_data)
	# plt.plot(peak_timestamps, scale_data[peak_timestamps], "x")
	# plt.show()


	# Need at least 3 peaks since we throw the first one away
	if num_peaks >= 3:
		
		for i in range(1,num_peaks-1):
			
			timestamp_1 = peak_timestamps[i]
			timestamp_2 = peak_timestamps[i+1]
			integral = integrate(scale_data, timestamp_1, timestamp_2)
			weight = integral / (timestamp_2 - timestamp_1).total_seconds()
			print("Weight {}".format(weight))
			weights.append(weight)

		mean_weight = sum(weights) / len(weights)
		return mean_weight

	else:
		return scale_data.mean()







def integrate (data, timestamp_1, timestamp_2):

	sliced_data = data[timestamp_1:timestamp_2]
	total_sum = 0
	num_data_points = len(sliced_data)

	for i in range (1, num_data_points):

		delta_t = sliced_data.index[i] - sliced_data.index[i-1]
		val = sliced_data.iloc[i]

		partial_sum = val*delta_t.total_seconds()
		total_sum = total_sum + partial_sum

	return total_sum




