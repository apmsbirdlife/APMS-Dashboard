# Script to handle functions related to events
import pandas as pd
import shutil
from data_plot import *
from penguin_functions import *
from check_data import *
from classes import *
import matplotlib.pyplot as plt


###############################################################################
# Global dictionary variable holding all constants
###############################################################################
global CONFIG


###############################################################################
# Create a list of tuples, of start- and end times of all the sub-events.
# First create a list of dead weight events. The subevents are in between the dead weights
###############################################################################
def find_sub_events (scale):
	
	sub_events_list = []
	dead_event_list	= []
	window_size = 10
	min_consec = CONFIG["MIN_TIME_BETWEEN_SUB_EVENTS"]*CONFIG["SAMPLING_FREQ"]
	max_std_dev = 0.03

	rolling_std_dev = scale.weights.rolling(window=window_size).std()
	
	# plt.plot(rolling_std_dev)
	# plt.show()

	mask = rolling_std_dev > max_std_dev


	cumul_sum = mask.cumsum()
	consec_counts = (cumul_sum.groupby(cumul_sum)).count()
	consec_counts = consec_counts[consec_counts > min_consec]

	for group_name, val in consec_counts.items():
		# print(group_name)
		
		series = cumul_sum[cumul_sum == group_name]
		timestamp_1 = series.index[0]
		timestamp_2 = series.index[-1]

		if (scale.weights[timestamp_1] < CONFIG["MAX_DEAD_WEIGHT"] and scale.weights[timestamp_2] < CONFIG["MAX_DEAD_WEIGHT"]):
			dead_event = (timestamp_1,timestamp_2)
			dead_event_list.append(dead_event)
		

	if len(dead_event_list) == 0:
		raise NoDeadWeightEventsException("No dead weight events found")
	scale.dead_event_list = dead_event_list

	# Now that we have all our dead events, the sub_events are between them
	for i in range (0,len(dead_event_list)-1):
		sub_event_start = dead_event_list[i][1]
		sub_event_end = dead_event_list[i+1][0]
		sub_event = (sub_event_start,sub_event_end)
		sub_events_list.append(sub_event)
	
	if len(sub_events_list) == 0:
		# plot_scale_data(scale.weights)
		raise NoSubEventsException("No sub-events found")

	
	######################################
	### DEBUG ###
	# print("Printing sub-event list...")
	# for sub_event in sub_events_list:
	# 	print(sub_event[0], sub_event[1])
	### DEBUG ###
	######################################
	
	scale.sub_events_list = sub_events_list
	return scale
##############################################################################
