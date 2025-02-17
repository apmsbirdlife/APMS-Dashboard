'''
File to hold all the Classes and Exceptions
Note Scale 1 is colony side and Scale 2 Ocean side
'''
import pandas as pd

###############################################################################
class Scale:
	def __init__(self, name):
		self.name = name
		self.weights = pd.Series()
		self.sub_events_list = []
		# self.event_array = []
		# self.event_transitions = []
		self.event_penguin_list = []
		self.dead_event_list = []
		self.weight_events_list = []
		# self.offset = 0
###############################################################################


###############################################################################
class Penguin:
	def __init__(self, 
		ID = None, 
		weight_obj = None, 
		direction = None,
		scale_file = None, 
		time_on_1 = None, 
		time_off_1 = None, 
		time_on_2 = None, 
		time_off_2 = None):

		self.id = ID
		self.info = {}
		self.weight_obj = weight_obj
		self.direction = direction	
		self.scale_file = scale_file
		self.time_on_1 = time_on_1
		self.time_off_1 = time_off_1
		self.time_on_2 = time_on_2
		self.time_off_2 = time_off_2
		self.scales_difference = 0
		self.weight_type = None
		self.rfid_jump_flag = False
		self.rfid_crossing_flag = False
		self.rfid_alone_crossing_flag = False
###############################################################################


###############################################################################
class Weight:
	def __init__ (self, weight = None, weight_difference = None, weight_type = None):
		self.weight = weight
		self.weight_difference = weight_difference
		self.weight_type = weight_type
###############################################################################


###############################################################################
class TimingJumpException(Exception):
	error_directory = 'timing_jump'

class FrequencyErrorException(Exception):
	error_directory = 'frequency_error'

class NoSubEventsException(Exception):
	error_directory = 'no_sub_events'

class UnequalNumberOfPenguinsException(Exception):
	error_directory = 'unequal_num_penguins'

class NoPenguinsException(Exception):
	error_directory = 'no_penguins'

class PenguinDirectionException(Exception):
	error_directory = 'direction_error'

class PenguinWeightException(Exception):
	error_directory = 'penguin_weight_error'

class WeightTooHighException(Exception):
	error_directory = 'weight_too_high'

class OverloadException(Exception):
	error_directory = 'overload'

class DuplicateEntriesException(Exception):
	error_directory = 'duplicate_timestamps'

class LargePenguinWeightDifferenceException(Exception):
	error_directory = 'large_penguin_weight_difference'

class NoDeadWeightEventsException(Exception):
	error_directory = 'NoDeadWeightEvents'	

class LargeDeadWeightException(Exception):
	error_directory = 'large_dead_weight'		

class LargeDeadWeightDifferenceException(Exception):
 	error_directory = 'large_dead_weight_difference'

class NegativeScaleJumpDuration(Exception):
 	error_directory = 'negative_jump_time'

class NegativeTimeOnScale(Exception):
	error_directory = 'negative_time_on_scale'
###############################################################################
