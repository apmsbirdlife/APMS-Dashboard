from correct_data import *
from data_plot import *
from classes import *
from shared_functions import *

###############################################################################
# Global dictionary variable holding all constants
###############################################################################
global CONFIG

###############################################################################


###############################################################################
# Checks if any weights exceeded the scale maximum
# Checks the weights are being saved at the correct rate
# 
###############################################################################
def check_data (scale_1,scale_2):
	
	print("Checking data...")
	max_weight = check_overload(scale_1)
	max_weight = check_overload(scale_2)

	frequency =	check_avg_sampling_period (scale_1)
	frequency =	check_avg_sampling_period (scale_2)

	check_duplicate_index(scale_1)
	check_duplicate_index(scale_2)

	check_time_between_samples(scale_1)
	check_time_between_samples(scale_2)

	print("Data check completed. Max Weight: {}   Sampling Frequency: {:.2f} Hz".format(max_weight,frequency))
###############################################################################


###############################################################################
# Checks if the maximum weight was exceeded, 
# as set in the config file: "SCALE_OVERLOAD"
###############################################################################
def check_overload (scale):
	series_data = scale.weights
	overload_flag = 0
	overloaded = series_data[series_data > CONFIG["SCALE_OVERLOAD"]]
	max_weight = series_data.max()
	if (len(overloaded)):
		raise OverloadException ("Scale overload detected: > {}: {}".format(CONFIG["SCALE_OVERLOAD"], overloaded))
	else:
		print("No overload detected on ", scale.name)
		return max_weight

###############################################################################




###############################################################################
# Checks if sampling rate falls within limits. As set in the config file
# EXAMPLE: 
# MAX_AVG_SAMPLING_PERIOD : 0.0101
# MIN_AVG_SAMPLING_PERIOD : 0.0099
# 100Hz = every 10ms or 0.010 seconds. 
# 1% error tolerance gives upper limit of 0.0101 and lower limit of 0.0099.
###############################################################################
def check_avg_sampling_period (scale):

	scale_data = scale.weights
	number_of_samples = len(scale_data)
	duration = (scale_data.index[-1] - scale_data.index[0]).total_seconds()
	avg_period = duration / number_of_samples
	
	if (avg_period > CONFIG["MAX_AVG_SAMPLING_PERIOD"] or avg_period < CONFIG["MIN_AVG_SAMPLING_PERIOD"]):
		raise FrequencyErrorException("Average sampling period outside allowable limits: {}	Frequency: {}".format(avg_period, 1/avg_period))
	else:
		# print("Frequency OK: {:.3f}".format(1/avg_period))
		return 1/avg_period
###############################################################################


###############################################################################
# If any two weight reading have the same timestamp, assume a timing glitch of 
# some sort and do not process the file
###############################################################################
def check_duplicate_index (scale):
	
	index = scale.weights.index.to_list()

	index_series = pd.Series(index)

	if (index_series.duplicated().any()):
		raise DuplicateEntriesException ("Duplicate timestamps found")
###############################################################################



###############################################################################
# If ever there is more than 1 second between samples, assume a timing jump occured
###############################################################################
def check_time_between_samples (scale):
	
	scale_data = scale.weights
	time_between_samples = scale_data.index.to_series().diff()
	
	time_delta_object = pd.Timedelta(seconds = 1)
	
	if any(time_between_samples > time_delta_object):
		# check_jump_error()
		raise TimingJumpException ("Time difference between samples too large: ", time_between_samples.max())   		
###############################################################################