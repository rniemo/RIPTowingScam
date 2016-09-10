import pandas as pd
import os
import urllib2
import json
import uuid
import time


GEOCODE_API_KEY = 'AIzaSyB8-2pmBoUrWCbzLwPkq9WyiEkeQCgPvlA'
GEOCODE_API_KEY_2= 'AIzaSyAF-qWnBRw51IkQewmXpPg3BtfvDfeyUbU'
URL = 'https://maps.googleapis.com/maps/api/geocode/json?'
cwd = os.getcwd()
data_dir = cwd + os.sep + '..' + os.sep + 'data'
meter_data = pd.read_csv(data_dir + os.sep + 'parking_meters.csv')
zone_data = pd.read_csv(data_dir + os.sep + 'residential.csv')
print 'hey'

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
		data = [str(uuid.uuid4()), line[0][0], line[0][1], line[1][0], line[1][1], side, address, 'zone', None, None]
		# append the data to the dataframe
		series = pd.Series(data, columns)
		df = df.append(series, ignore_index=True)
		i = i + 1
		if i > 500:
			api_key = GEOCODE_API_KEY_2
	df.to_csv('line_data.csv')

def geocode(address, api_key):
	request = '%saddress=%s&key=%s' %(URL, address, api_key)
	print request
	try:
		response = urllib2.urlopen(request).read()
	except:
		print response
		return None

	# can only call server 50 times / s, so this'll guarantee we're under that
	time.sleep(.02)
	response = json.loads(response)
	latlng = response['results'][0]['geometry']['location']
	return (latlng['lat'], latlng['lng'])

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
columns = ['id', 'blat', 'blon', 'elat', 'elon', 'sides', 'address', 'type', 'rate', 'num_meters']
df = pd.DataFrame(columns=columns)

add_zone_data(df)

