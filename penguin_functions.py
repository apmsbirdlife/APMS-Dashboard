# This script deals with all penguin related processing
import sys
from weights import *
from event_array import find_sub_events
from classes import *
from data_plot import *
from correct_data import *
from check_data import *
import traceback


###############################################################################
# Global dictionary variable holding all constants
###############################################################################
global CONFIG

###############################################################################
# Process a directory full of scale files, for one day
###############################################################################
def process_scale_files (scale_data_path, output_data_path):

	penguin_list_scale_files = []
	error_counter = 0

	scale_files = get_scale_files(scale_data_path)
	number_of_scale_files = len(scale_files)
	if number_of_scale_files == 0:
		print('No scale files found in scale directory')
		return [], 0, 0

	# Go through each scale file for the day
	for file in scale_files:

		print("\n\nProcessing {}".format(file))
		scale_file_path = os.path.join(scale_data_path,file)
		# plot_csv_file(scale_file_path)

		try:
			print("#################################")
			print(scale_file_path)
			file_penguin_list = process_scale_file(scale_file_path)
			print("Penguin list for Scale File")
			print_penguin_list(file_penguin_list)
			penguin_list_scale_files = penguin_list_scale_files + file_penguin_list 
			print("succesfully processed {}".format(scale_file_path))
			data_path_good = os.path.join(output_data_path, 'good')
			if_not_then_make(data_path_good)
			
			shutil.copy(scale_file_path, data_path_good)

		except Exception as exception_object:
			error_counter = error_counter + 1

			if hasattr(exception_object, "error_directory"):
				error_directory = os.path.join(output_data_path, exception_object.error_directory)					
				print("Could not process scale file: {}".format(scale_file_path))
				# print("Moving file to {}".format(error_directory))
				print("Error message: ", exception_object)
				if_not_then_make(error_directory)
				shutil.copy(scale_file_path, error_directory)

			else:
				traceback.print_exc()
	
	return penguin_list_scale_files, number_of_scale_files, error_counter
###############################################################################




###############################################################################
# Process a single Scale File
###############################################################################
def process_scale_file (scale_file_path):	

	# Old data filenmaes that did not contain site code
	if scale_file_path[-5].isdigit():
		scale_file = scale_file_path[-19:]
	else:
		scale_file = scale_file_path[-22:]

	file_penguin_list = []
	# sub_event_penguin_list = []

	scale_1 = Scale(name = 'scale_1')
	scale_2 = Scale(name = 'scale_2')

	# Load the two events from the scale file into the DataFrame
	df = load_df_two_scales (scale_file_path)

	scale_1.weights = df['scale_1']
	scale_2.weights = df['scale_2']

	check_data(scale_1,scale_2)
	scale_1 = fix_timestamp_index(scale_1)
	scale_2 = fix_timestamp_index(scale_2)

	# shift_seconds(scale_2,-1.6)

	# print("Processing data for Scale 1...")
	scale_1 = process_event(scale_1)
	# print("Scale 1 Penguin List for the event")
	print_penguin_list(scale_1.event_penguin_list)
	# print("Processing data for Scale 2...")
	scale_2 = process_event(scale_2)
	
	print_penguin_list(scale_2.event_penguin_list)

	# plot_with_options(scale_1, scale_2, sub_events = True)

	if len(scale_1.event_penguin_list) == 0 and len(scale_2.event_penguin_list) == 0:
		raise NoPenguinsException("No penguins detected on either scale")
	
	if len(scale_1.event_penguin_list) == len(scale_2.event_penguin_list) and len(scale_1.event_penguin_list) > 0:
		event_penguin_list = combine_penguin_lists(scale_1, scale_2)
	
	else:
		raise UnequalNumberOfPenguinsException("Different number of penguins detected for scale 1 and scale 2")

	for penguin in event_penguin_list:
		penguin.scale_file = scale_file

	return event_penguin_list

###############################################################################









###############################################################################
def process_event(scale):

	print("Processing data for {}:".format(scale.name))

	scale = find_sub_events(scale)

	# scale.dead_event_list will hold 1 more entry than sub_event_list
	num_of_sub_events = len(scale.sub_events_list)
	print("Number of sub-events for {}: {}".format(scale.name, num_of_sub_events))
	
	# Go through all the sub-events and find the penguins
	for i in range (0,num_of_sub_events):
		print("Analyzing sub-event: ",i+1)

		print("Finding starting dead weight...")
		dead_weight_start = find_weight(scale, scale.dead_event_list[i][0], scale.dead_event_list[i][1])
		
		
		if dead_weight_start.weight > CONFIG["MAX_DEAD_WEIGHT"]:
			raise LargeDeadWeightException("Large starting dead weight detected on: ", scale.name)

		print("Finding ending dead weight...")
		dead_weight_end = find_weight(scale, scale.dead_event_list[i+1][0], scale.dead_event_list[i+1][1])
		if dead_weight_end.weight > CONFIG["MAX_DEAD_WEIGHT"]:
			raise LargeDeadWeightException("Large ending dead weight detected on: ", scale.name)
	
		print("dead_weight_start ", dead_weight_start.weight)
		print("dead_weight_end ", dead_weight_end.weight)

		sub_event_start_time = scale.sub_events_list[i][0]
		sub_event_end_time = scale.sub_events_list[i][1]

		scale_data = scale.weights[sub_event_start_time:sub_event_end_time]

		# Taking the average of the deadweight before and after the crossing. This could be improved
		dead_weight = (dead_weight_start.weight + dead_weight_end.weight)/2

		print("Finding weights in sub-event, excluding start and end weights")
		sub_event_penguin_list = get_sub_event_penguin_list (scale, dead_weight, scale.sub_events_list[i])
	
		scale.event_penguin_list = scale.event_penguin_list + sub_event_penguin_list

	return scale
###############################################################################





###############################################################################
def get_sub_event_penguin_list (scale, dead_weight, sub_event_timestamps):

	sub_event_penguin_list = []
	penguin_id = 0

	sub_event_start_time = sub_event_timestamps[0]
	sub_event_end_time = sub_event_timestamps[1]

	scale_data = scale.weights[sub_event_start_time:sub_event_end_time]

	# Get a list of timestamps. It returns a list of start- and end-timestamps for each weight
	weights_timestamps_list = get_weights_timestamps_list(scale_data)

	num_of_weights = len(weights_timestamps_list)
	print("Number of weights in sub-event ",num_of_weights)

	for i in range(0,num_of_weights):

		print("Processing weight {} of {}".format(i+1,num_of_weights))
		weight_start_time = weights_timestamps_list[i][0]
		weight_end_time   = weights_timestamps_list[i][1]

		
		# Here the actual weight is determined
		weight_obj = find_weight(scale, weight_start_time, weight_end_time)

		weight_obj.weight = weight_obj.weight - dead_weight

		if get_number_of_penguins(weight_obj) == 1:
			
			print("Penguin Identified...")
			
			if scale.name == 'scale_1':

				penguin = Penguin(ID=penguin_id, 
					weight_obj = weight_obj, 
					time_on_1 = weight_start_time, 
					time_off_1 = weight_end_time)
				
			elif scale.name == 'scale_2':
				penguin = Penguin(ID=penguin_id, 
					weight_obj = weight_obj, 
					time_on_2 = weight_start_time, 
					time_off_2 = weight_end_time)

			penguin_id = penguin_id + 1
			sub_event_penguin_list.append(penguin)
			

	return sub_event_penguin_list
###############################################################################




###############################################################################
def combine_penguin_lists(scale_1, scale_2):

	# Maybe add to check that the time period between the penguin climbing off the scale and on to the other is reasonable

	event_penguin_list = []

	event_direction = determine_event_direction(scale_1, scale_2)
	
	penguin_list_1 = scale_1.event_penguin_list
	penguin_list_2 = scale_2.event_penguin_list
	
	number_of_penguins = len(penguin_list_1)

	for i in range(0, number_of_penguins):
		penguin_scale_1 = penguin_list_1[i]
		penguin_weight_1 = penguin_scale_1.weight_obj.weight
		
		penguin_scale_2 = penguin_list_2[i]
		penguin_weight_2 = penguin_scale_2.weight_obj.weight
		
		penguin = Penguin(ID = i)
		penguin.direction = event_direction
		penguin.time_on_1 = penguin_list_1[i].time_on_1
		penguin.time_off_1 = penguin_list_1[i].time_off_1
		penguin.time_on_2 = penguin_list_2[i].time_on_2
		penguin.time_off_2 = penguin_list_2[i].time_off_2

		weight_difference = penguin_weight_1 - penguin_weight_2
		penguin.scales_difference = weight_difference
		
		# --- ADDED NEW LINES HERE ---
		penguin.scale_1_type = penguin_list_1[i].weight_obj.weight_type
		penguin.scale_2_type = penguin_list_2[i].weight_obj.weight_type
		# ------------------------------

		if weight_difference == 0:
			print("Both scales read the same weight")

		elif weight_difference > 0:
			print("Scale 1 reads {} kg higher than scale 2".format(abs(weight_difference)))

		else:
			print("Scale 2 reads {} kg higher than scale 1".format(abs(weight_difference)))


		if  (abs(weight_difference) > CONFIG["MAX_SCALES_DIFFERENCE_ALLOWED"]):
			raise LargePenguinWeightDifferenceException("Large difference between measured weight on scale 1 and scale 2: ",weight_difference)

		
		if (penguin_list_1[i].weight_obj.weight_type == 'static' and penguin_list_2[i].weight_obj.weight_type == 'static'):
			final_weight = (penguin_list_1[i].weight_obj.weight + penguin_list_2[i].weight_obj.weight)/2
			penguin.weight_obj = weight_object = Weight(weight = round(final_weight,3), weight_difference = weight_difference, weight_type = 'avg_static')
			penguin.info['weight_type'] = 'avg_static'

		elif (penguin_list_1[i].weight_obj.weight_type == 'dynamic' and penguin_list_2[i].weight_obj.weight_type == 'dynamic'):
			# Maybe do something better here, like choosing the one with the lowest std dev
			final_weight = (penguin_list_1[i].weight_obj.weight + penguin_list_2[i].weight_obj.weight)/2
			penguin.weight_obj = weight_object = Weight(weight = round(final_weight,3), weight_difference = weight_difference, weight_type = 'avg_dynamic')
			penguin.info['weight_type'] = 'avg_dynamic'


		# Here we know both scales did not have a static weight, but scale 1 did, so use that
		elif (penguin_list_1[i].weight_obj.weight_type == 'static'):
			final_weight = penguin_list_1[i].weight_obj.weight
			penguin.weight_obj = weight_object = Weight(weight = round(final_weight,3), weight_difference = weight_difference, weight_type = 'static_1')
			penguin.info['weight_type'] = 'static_1'


		# Here we know both scales did not have a static weight, but scale 2 did, so use that
		elif (penguin_list_2[i].weight_obj.weight_type == 'static'):
			final_weight = penguin_list_2[i].weight_obj.weight
			penguin.weight_obj = weight_object = Weight(weight = round(final_weight,3), weight_difference = weight_difference, weight_type = 'static_2')
			penguin.info['weight_type'] = 'static_2'



		# Here we know both scales did not have a static weight, but scale 1 did, so use that
		elif (penguin_list_1[i].weight_obj.weight_type == 'static'):
			final_weight = penguin_list_1[i].weight_obj.weight
			penguin.weight_obj = weight_object = Weight(weight = round(final_weight,3), weight_difference = weight_difference, weight_type = 'static_1')
			penguin.info['weight_type'] = 'static_1'


		# Here we know both scales did not have a static weight, but scale 2 did, so use that
		elif (penguin_list_2[i].weight_obj.weight_type == 'static'):
			final_weight = penguin_list_2[i].weight_obj.weight
			penguin.weight_obj = weight_object = Weight(weight = round(final_weight,3), weight_difference = weight_difference, weight_type = 'static_2')
			penguin.info['weight_type'] = 'static_2'


		# Scale 1 and scale 2 both had weight readings that were too short
		elif (penguin_list_1[i].weight_obj.weight_type == 'time_too_short' and penguin_list_2[i].weight_obj.weight_type == 'time_too_short'):
			final_weight = (penguin_list_1[i].weight_obj.weight + penguin_list_2[i].weight_obj.weight)/2
			penguin.weight_obj = weight_object = Weight(weight = round(final_weight,3), weight_type = 'time_too_short_for_both')
			penguin.info['weight_type'] = 'time_too_short_for_both'


		# scale 1 had a weight reading that was too short. use scale 2 weight
		elif (penguin_list_1[i].weight_obj.weight_type == 'time_too_short'):
			final_weight = penguin_list_2[i].weight_obj.weight
			penguin.weight_obj = weight_object = Weight(weight = round(final_weight,3), weight_type = 'time_too_short_for_1')
			penguin.info['weight_type'] = 'time_too_short_for_1'

		# scale 2 had a weight reading that was too short. use scale 1 weight
		elif (penguin_list_2[i].weight_obj.weight_type == 'time_too_short'):
			final_weight = penguin_list_1[i].weight_obj.weight
			penguin.weight_obj = weight_object = Weight(weight = round(final_weight,3), weight_type = 'time_too_short_for_2')
			penguin.info['weight_type'] = 'time_too_short_for_2'

		else:
			print("Penguin weight type unknown. ERROR: CPL2")
			raise PenguinWeightException("Penguin weight type unknown")

		event_penguin_list.append(penguin)

	return event_penguin_list
###############################################################################


###############################################################################
def print_penguin_list (penguin_list, rfid = False):

	if len(penguin_list) == 0:
		print("penguin list empty")
		return 0

	for penguin in penguin_list:
		
		if penguin.time_on_1 and penguin.time_off_1 and penguin.time_on_2 and penguin.time_off_2:

			penguin_crossing_start = min([penguin.time_on_1, penguin.time_off_1, penguin.time_on_2, penguin.time_off_2])
			penguin_crossing_end = max([penguin.time_on_1, penguin.time_off_1, penguin.time_on_2, penguin.time_off_2])
	
			time_penguin = penguin_crossing_start + (penguin_crossing_end - penguin_crossing_start)/2

			print("ID: {} \t Weight: {:.3f} kg \t Weight type: {} \t Time: {} \t Direction: {} \t Difference between scales(1-2): {:.3f} kg".format(
				penguin.id, 
				penguin.weight_obj.weight, 
				penguin.weight_obj.weight_type, 
				time_penguin.strftime("%H:%M:%S"),
				penguin.direction,
				penguin.scales_difference))
		

		elif penguin.time_on_1 and penguin.time_off_1:
			time_penguin = penguin.time_on_1 + (penguin.time_off_1 - penguin.time_on_1)/2
	
			print("ID: {} Weight: {:.3f}kg Weight type: {} Time: {}".format(
				penguin.id, 
				penguin.weight_obj.weight, 
				penguin.weight_obj.weight_type, 
				time_penguin.strftime("%H:%M:%S")))


		elif penguin.time_on_2 and penguin.time_off_2:
			time_penguin = penguin.time_on_2 + (penguin.time_off_2 - penguin.time_on_2)/2
	
			print("ID: {} Weight: {:.3f}kg Weight type: {} Time: {}".format(
				penguin.id, 
				penguin.weight_obj.weight, 
				penguin.weight_obj.weight_type, 
				time_penguin.strftime("%H:%M:%S")))

		if rfid == True:

			if (penguin.rfid_jump_flag):
				print("RFID detected during jump.")
			
			elif (penguin.rfid_crossing_flag):
				
				if (penguin.rfid_alone_crossing_flag):
					print("rfid detected during crossing and penguin alone during crossing")
				else:
					print("rfid detected during crossing")
			
###############################################################################


###############################################################################
def get_number_of_penguins (weight_obj):

	if weight_obj.weight_type == 'time_too_short':
		return -1


	if weight_obj.weight_type == 'other':
		return -2


	if (weight_obj.weight < CONFIG["MIN_PENGUIN_WEIGHT"]):
		print("Weight too low to be a penguin")
		return 0
	
	elif (weight_obj.weight >= CONFIG["MIN_PENGUIN_WEIGHT"] and weight_obj.weight <= CONFIG["MAX_PENGUIN_WEIGHT"]):
		return 1

	elif (weight_obj.weight > CONFIG["MAX_PENGUIN_WEIGHT"] and weight_obj.weight <= 2*CONFIG["MAX_PENGUIN_WEIGHT"]):
		print("Weight too high to be a penguin or multiple penguins")
		return 2
	
	elif (weight_obj.weight > 3*CONFIG["MAX_PENGUIN_WEIGHT"]):
		print("Weight reading too high: ", weight_obj.weight)
		raise WeightTooHighException ("The weight reading was too high: {}".format(weight_obj.weight))
		return -3
	else:
		print("weight obj cannot be analyzed. Weight: {}  Type: {}".format(weight_obj.weight, weight_obj.weight_type))
		sys.exit
###############################################################################



###############################################################################
def determine_event_direction(scale_1, scale_2):

	# we know the penguin lists have the same length, so use scale_1
	num_of_penguins = len(scale_1.event_penguin_list)

	out_to_ocean_counter = 0
	back_from_ocean_counter = 0


	for i in range (0, num_of_penguins):

		penguin_on_1 = scale_1.event_penguin_list[i].time_on_1
		penguin_off_1 = scale_1.event_penguin_list[i].time_off_1
		penguin_on_2 = scale_2.event_penguin_list[i].time_on_2
		penguin_off_2 = scale_2.event_penguin_list[i].time_off_2


		########## DEBUG ############
		# print("penguin_on_1: ", penguin_on_1)
		# print("penguin_off_1: ", penguin_off_1)
		# print("penguin_on_2: ", penguin_on_2)
		# print("penguin_off_2: ", penguin_off_2)
		#############################


		################ Penguin heading out to ocean ###########################
		if penguin_on_1 < penguin_on_2:
			
			# This should be true
			if (penguin_on_1 < penguin_off_1) and (penguin_on_2 < penguin_off_2):
				
				# check the time gap between scales
				scale_gap = penguin_on_2 - penguin_off_1
				if scale_gap.total_seconds() < 0:
					raise NegativeScaleJumpDuration("Negative time taken to jump from scale 1 to scale 2: ", scale_gap.total_seconds())
				else:
					out_to_ocean_counter = out_to_ocean_counter + 1
			else:
				raise NegativeTimeOnScale("Negative time spent on scale", scale_gap.total_seconds())

		################ Penguin coming back from ocean ###########################
		elif (penguin_on_2 < penguin_on_1):
			# This should be true
			if penguin_on_2 < penguin_off_2 and penguin_on_1 < penguin_off_1:
				# check the time gap between scales
				scale_gap = penguin_on_1 - penguin_off_2
				if scale_gap.total_seconds() < 0:
					raise NegativeScaleJumpDuration("Negative time taken to jump from scale 2 to scale 1: ", scale_gap.total_seconds())
				else:
					back_from_ocean_counter = back_from_ocean_counter + 1
			else:
				raise NegativeTimeOnScale("Negative time spent on scale", scale_gap.total_seconds())
		
	if out_to_ocean_counter == num_of_penguins:
		return ('out_to_ocean')

	elif back_from_ocean_counter == num_of_penguins:
		return ('back_from_ocean')

	else:
		message = "Event direction could not be determined.{} penguin(s) going out to ocean and {} coming back".format(out_to_ocean_counter,back_from_ocean_counter)
		raise PenguinDirectionException(message)
###############################################################################



