import time
import os
import random
import logging
import requests
import json
from rich import pretty, print
pretty.install()

print("[bold magenta]Staring app[/bold magenta] [bold green]CMC-Fetcher[/bold green]")
cwd = os.getcwd()
print(f"[bold magenta]Working in[/bold magenta] [bold green]{cwd}[/bold green]")

with open(f'{cwd}/apikeys.json') as file:
	data = json.load(file)
	APIKEY_list = data['keys']
print(APIKEY_list)
print(f"[bold magenta]Found[/bold magenta] {len(APIKEY_list)} ApiKeys")

def request_url(url):
	print(f"Waiting 3 sec until request")
	time.sleep(3)
	apikey = random.choice(APIKEY_list)
	resp = requests.get(
			url,
			headers = {"X-CMC_PRO_API_KEY": apikey}
 )
	if resp.status_code == 200:
		print(f'[bold magenta]Successful[/bold magenta] with ApiKey {apikey} for {url}')
		return resp
	elif resp.status_code == 500:
		print(f'[bold magenta]Internal server error[/bold magenta] with ApiKey {apikey} for {url}')
		return resp
	elif resp.status_code == 429:
		print(f'[bold magenta]Too many requests[/bold magenta] with ApiKey {apikey} for {url}\n{resp.json()}')
		return resp
	elif resp.status_code == 400:
		print(f'[bold magenta]Bad request[/bold magenta] with ApiKey {apikey} for {url}\n{resp.json()}')
		return resp
	elif resp.status_code == 401:
		print(f'[bold magenta]Unauthorized[/bold magenta] with ApiKey {apikey} for {url}\n{resp.json()}')
		return resp

def get_chunks_coins(data):
	if data.status_code == 200:
		all_coins = data.json()['data']
		ids_coins = []
		for coin in all_coins:
			ids_coins.append(coin['id'])
		chunks = [ids_coins[x:x+100] for x in range(0, len(ids_coins), 100)]
		return chunks
	else:
		return False

def get_all_coins():
	resp = request_url('https://pro-api.coinmarketcap.com/v1/cryptocurrency/map')
	return resp


def get_metadata_coins(data):
	metadata_coins = {}
	chunks_id_coins = get_chunks_coins(data)
	for chunk in chunks_id_coins:
		ids = ','.join([str(i) for i in chunk])
		resp = request_url(f'https://pro-api.coinmarketcap.com/v1/cryptocurrency/info?id={ids}')
		if resp.status_code == 200:
			for k, v in resp.json()['data'].items():
				metadata_coins[k] = v
		else:
			return False
	return metadata_coins

def write_json(data, filename):
	with open(f'{cwd}/{filename}.json', 'w') as file:
		json.dump(data, file, indent=4)
	print(f"Saved [bold magenta]{filename}.json[/bold magenta]")


if __name__ == '__main__':
	all_coins = get_all_coins()
	metadata_coins = get_metadata_coins(all_coins)
	write_json(all_coins.json()['data'], 'all_coins')
	write_json(metadata_coins, 'metadata_coins')
	print("[bold magenta]App Closing...[/bold magenta]")


