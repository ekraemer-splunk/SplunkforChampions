#!/usr/bin/env python3 

import requests
import time
import sys
import json

# My Values
APIKey = "RGAPI-b9122f7a-2e28-4e45-8af0-8847417068bf"
gameName = "Splunk1conf22"
tagLine = "Spk01"
debug = True
lineBreaker = "\n"

# API URLs
infoByRiotID = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + gameName
matchesByPuuid = "https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/"
matchInfo = "https://americas.api.riotgames.com/lol/match/v5/matches/"

def getPuuid():
	try: response = requests.get(infoByRiotID, params={'api_key': APIKey})
	except requests.exceptions.RequestException as e: raise SystemExit(e)
	return response.json()

def getMatchIDs(puuid, count = 20):
	try: response = requests.get(matchesByPuuid + puuid + "/ids", params={'start': 0, 'count': count, 'api_key': APIKey})
	except requests.exceptions.RequestException as e: raise SystemExit(e) #This prints to stderr
	return response.json()

def getMatchInfo(matchID):
	try: response = requests.get(matchInfo + matchID, params={'api_key': APIKey})
	except requests.exceptions.RequestException as e: raise SystemExit(e)
	return response.json()

def main():
	# 1. Get puuid
	response = getPuuid()
	if debug: print("\nResponse: ", response)
	puuid = response['puuid']
	if debug: print('\nPUUID is: ', puuid)

	# 2. Get list of matches from puuid
	matchIDs = getMatchIDs(puuid)
	if debug: print("\nMatchIDs are: ", matchIDs)

	# 3. Get match details from a matchID
	matchInfo = getMatchInfo(matchIDs[0])

	# 4. Isolate each champion's data, and add a gameId to coorelate, add to accumulator
	# Splunk does not like multiple stdouts and stops reading (?)
	accumulator = ""
	for index, champ in enumerate(matchInfo['info']['participants']):
		champ['gameId'] = matchInfo['info']['gameId']
		accumulator += json.dumps(champ) + lineBreaker
	if debug: print(accumulator)

	# 5. Delete the participants key in the dict
	matchInfo['info'].pop('participants', None)
	if debug: print("\nThis list of keys should not include participants: ", matchInfo['info'].keys())

	#6. Output
	if not debug: sys.stdout.write(accumulator + json.dumps(matchInfo) + lineBreaker)


if __name__ == "__main__":
	main()




















