import pandas as pd
import os
import urllib2
import json
import uuid
import time
import random
import numpy as np


GEOCODE_API_KEY = 'AIzaSyCDLLv7B3zkbayizbk7pNp8m2eDbDDEJpA'
GEOCODE_API_KEY_2= 'AIzaSyAF-qWnBRw51IkQewmXpPg3BtfvDfeyUbU'
URL = 'https://maps.googleapis.com/maps/api/geocode/json?'
cwd = os.getcwd()
data_dir = cwd + os.sep + '..' + os.sep + 'data'
meter_data = pd.read_csv(data_dir + os.sep + 'parking_meters.csv')
zone_data = pd.read_csv(data_dir + os.sep + 'residential.csv')

# take poorly formatted data and make it not dumpster tier
def add_zone_data(df):
	zone_data.drop_duplicates(inplace=True)
	zone_data.dropna(inplace=True)
	geocoded = {}
	api_key = GEOCODE_API_KEY
	i = 0
	for row_num, row_data in zone_data.iterrows():
		# round block to nearest 100
		block = int(round(float(row_data['BLOCK']), -2))
		# split string into street address vs philly/zip/latlng part
		index = row_data['Location'].find('\n(')
		street = row_data['Location'][0:index]
		address = '%d %s' % (block, street)
		end_address = '%d %s' % (block + 100, street)
		# thanks, obama
		address = address.replace('\n', ' ')
		end_address = end_address.replace('\n', ' ')
		address = address.replace(' ', '+')
		end_address = end_address.replace(' ', '+')
		if address not in geocoded:
			start_latlng = geocode(address, api_key)
			end_latlng = geocode(end_address, api_key)
			geocoded[address] = (start_latlng, end_latlng)
		line = geocoded[address]
		print line
		if None in line:
			continue
		# returns the side you can park on, N/E/S/W or B for both sides
		side = row_data['Side'][0]
		# form array of data
		data = [str(uuid.uuid4()), line[0][0], line[0][1], line[1][0], line[1][1], side, address, 'zone', None, None, None, None]
		# append the data to the dataframe
		series = pd.Series(data, columns)
		df = df.append(series, ignore_index=True)
		i = i + 1
		if i > 500:
			api_key = GEOCODE_API_KEY_2
	df.to_csv('line_data.csv')

def add_meter_data(df):
	#x = meter_data[['BLOCK/LIMITS', 'STREET']]
#x.drop_duplicates()
	meter_data.drop_duplicates(inplace=True)
	meter_streets = meter_data[['BLOCK/LIMITS', 'STREET', 'SIDE']]
	meter_streets = meter_streets.drop_duplicates()

	unique_meters = meter_data.drop_duplicates(subset='METER NUMBER')
	grouped = unique_meters.groupby(['BLOCK/LIMITS', 'STREET'])
	num_meter_table = grouped.count()
	geocoded = {}
	i = 0
	# f['METER NUMBER']['*blocklimits*']['*street*']
	for row_num, row_data in meter_streets.iterrows():
		# if we aren't looking at an address, skip that
		if not row_data['BLOCK/LIMITS'].isdigit():
			continue
		# round block to nearest 100
		block = int(round(float(row_data['BLOCK/LIMITS']), -2))
		street = row_data['STREET'] + ' Philadelphia, PA'
		address = '%d %s' % (block, street)
		end_address = '%d %s' % (block + 100, street)
		# thanks, obama
		address = address.replace('\n', ' ')
		end_address = end_address.replace('\n', ' ')
		address = address.replace(' ', '+')
		end_address = end_address.replace(' ', '+')
		if address not in geocoded:
			start_latlng = geocode(address, GEOCODE_API_KEY)
			end_latlng = geocode(end_address, GEOCODE_API_KEY)
			geocoded[address] = (start_latlng, end_latlng)
		line = geocoded[address]
		if None in line:
			continue
		# returns the side you can park on, N/E/S/W or B for both sides
		side = row_data['SIDE'][0]
		rate_row = meter_data[np.logical_and(meter_data['SIDE'] == row_data['SIDE'], \
				np.logical_and(meter_data['BLOCK/LIMITS'] == row_data['BLOCK/LIMITS'], \
					meter_data['STREET'] == row_data['STREET']))].head(1)
		
		rate = float(rate_row['RATE'].values[0][1:])
		num_meters = num_meter_table['METER NUMBER'][row_data['BLOCK/LIMITS']][row_data['STREET']]
		# form array of data
		data = [str(uuid.uuid4()), line[0][0], line[0][1], line[1][0], line[1][1], side, address, 'meter', rate, num_meters, None, None]
		# append the data to the dataframe
		series = pd.Series(data, columns)
		df = df.append(series, ignore_index=True)
	df.to_csv('temp.csv')

def geocode(address, api_key):
	#return (.5, .5)
	request = '%saddress=%s&key=%s' %(URL, address, api_key)
	try:
		response = urllib2.urlopen(request).read()
	except:
		return None
	try:
		# can only call server 50 times / s, so this'll guarantee we're under that
		time.sleep(.02)
		response = json.loads(response)
		latlng = response['results'][0]['geometry']['location']
		return (latlng['lat'], latlng['lng'])
	except:
		print request
	return None

def create_availability_df():
	columns = ['avalability_id', 'start_day', 'end_day', 'start_time', 'end_time', 'limit']
	df = pd.DataFrame(columns=columns)
	times = meter_data[['FROM DAY', 'TO DAY', 'FROM TIME', 'TO TIME', 'LIMIT HR', 'LIMIT MIN']]
	times = times.drop_duplicates()
	for row_num, row_data in times.iterrows():
		if np.isnan(row_data['LIMIT MIN']):
			limit = row_data['LIMIT HR']
		else:
			limit = row_data['LIMIT MIN'] / 60.0
		data = [str(uuid.uuid4()), row_data['FROM DAY'], row_data['TO DAY'], \
					row_data['FROM TIME'], row_data['TO TIME'], limit]
		series = pd.Series(data, columns)
		df = df.append(series, ignore_index=True)
	return df


def create_availability_meter_table():
	columns = ['meter_id', 'availability_id']
	df = pd.DataFrame(columns = columns)
	lines = pd.read_csv(data_dir + os.sep + 'meter_line_data.csv')
	availabilities = pd.read_csv(data_dir + os.sep + 'availability_data.csv')
	for row_num, row_data in lines.iterrows():
		addr = row_data['address']
		indx = addr.find('+')
		block = addr[:indx]
		street = addr[indx+1:addr.find('Philadelphia')-1]
		street = street.replace('+', ' ')
		line_meter_data = meter_data[np.logical_and(meter_data['BLOCK/LIMITS'] == block, meter_data['STREET'] == street)]
		seen_time_ids = []
		for x, time_data in line_meter_data.iterrows():
			#print availabilities[availabilities['start_day'] == time_data['FROM DAY']]

			match = availabilities[np.logical_and(availabilities['start_day'] == time_data['FROM DAY'], \
						np.logical_and(availabilities['end_day'] == time_data['TO DAY'], \
							np.logical_and(availabilities['start_time'] == time_data['FROM TIME'], \
								np.logical_and(availabilities['end_time'] == time_data['TO TIME'], \
									availabilities['limit'] == time_data['LIMIT HR']))))]
			match = match.head(1)
			match_id = match['avalability_id']
			if len(match_id.values) > 0:
				match_id  = match_id.values[0]
				if match_id not in seen_time_ids:
					seen_time_ids.append(match_id)
					series = pd.Series([row_data['id'], match_id], columns)
					df = df.append(series, ignore_index = True)
	df.to_csv('availability_map.csv')

def create_line_json():
	result = []
	filenames = ['meter_line_data.csv']
	for filename in filenames:
		lines = pd.read_csv(data_dir + os.sep + filename)
		for row_num, line in lines.iterrows():
			dic = {'id': line['id'], 'blat': line['blat'], 'blon': line['blon'], 'elat': line['elat'], \
				'elon': line['elon'], 'sides': line['sides'], 'address': line['address'], \
				'type': line['type'], 'rate': line['rate'], 'num_meters': line['num_meters']}
			result.append(dic)
	print json.dumps(result)

create_line_json()



# id: the id of this line
# blat: beginning latitude
# blon: beginning longitude
# elat: ending latitude
# elon: ending longitude
# sides: what sides can be parked on ('N', 'S', 'E', 'W' or 'B' for both)
# address: address of the starting block e.g. 2500 Pine St. Philadelphia, PA
# type: 'meter' or 'zone' if there are meters or if it's residential zoned
# The following fields are applicable for meter typed lines:
# rate: if it's a meter type, the cost/Hr in dollars
# availability_id: the id that maps to a different table containing time availability info.
# num_meters: the number of meters on this line (this might not work lmao)

#columns = ['id', 'blat', 'blon', 'elat', 'elon', 'sides', 'address', 'type', 'rate', 'num_meters', 'num_safe', 'num_towed']
#df = pd.DataFrame(columns=columns)


#add_meter_data(df)
#add_zone_data(df)

#availability_df = create_availability_df()
#availability_df.to_csv('availability_data.csv')

#create_availability_meter_table()













