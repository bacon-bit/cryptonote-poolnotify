#!bin/python3

import click, requests, sqlite3
from datetime import datetime
from pushbullet import Pushbullet

a_protocol = ''
a_url = ''
a_port = ''
denom = 1
check_time = 300

with open ("pushbullet.config", "r") as configfile:
    pushbullet_api_key=configfile.read().replace('\n', '')

pb = Pushbullet(pushbullet_api_key)
db = 'poolstats.db'

hashrate_translations = {
    'H' : 1,
    'KH' : 1000,
    'MH' : 1000000,
    'GH' : 1000000000,
    'TH' : 1000000000000,
    'PH' : 1000000000000000
}

def dbSetup():
    global db
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS stats (pool_wallet text UNIQUE, balance int, coin_units int, updated int)''')
    c.execute('''CREATE TABLE IF NOT EXISTS hashrate_history (pool_wallet text, hashrate int, timestamp int)''')
    conn.commit()
    conn.close()

def updateHashRate(wallet, hashrate):
    global db, a_url
    conn = sqlite3.connect(db)
    c = conn.cursor()
    pool_wallet = a_url + wallet
    # Add latest
    c.execute('''INSERT INTO hashrate_history (pool_wallet, hashrate, timestamp) VALUES (?, ?, ?)''', (pool_wallet, hashrate, datetime.utcnow().timestamp()))
    conn.commit()
    # Remove all but last 24
    
    c.execute('''DELETE FROM hashrate_history WHERE rowid NOT IN ( SELECT rowid FROM hashrate_history WHERE pool_wallet = ? ORDER BY timestamp DESC LIMIT 24 )''', (pool_wallet,))
    conn.commit()
    c.execute('''SELECT *, rowid FROM hashrate_history WHERE pool_wallet = ?''', (pool_wallet,))
    results = c.fetchall()
    conn.close()

    return results

def updateStats(wallet, balance, units):
    global db, a_url
    conn = sqlite3.connect(db)
    c = conn.cursor()
    pool_wallet = a_url + wallet
    c.execute('''INSERT OR REPLACE INTO stats (pool_wallet, balance, coin_units, updated) VALUES (?, ?, ?, ?)''', (pool_wallet, balance, units, datetime.utcnow().timestamp()))
    conn.commit()
    conn.close()
    pb.push_note(a_url + ' Balance Updated', 'New Balance: ' + str(balance) + ' (' + str(balance / units) + ' XMR)')

def getStats(wallet, balance, units):
    global db, a_url
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    pool_wallet = a_url + wallet
    c.execute('''SELECT *, rowid FROM stats WHERE pool_wallet = ? LIMIT 1''', (pool_wallet,))
    existing = c.fetchone()

    if existing is None:
        updateStats(wallet, balance, units)
    elif existing['balance'] != balance:
        updateStats(wallet, balance, units)

    wallet_xmr_formatted = str(balance/units)
    print('Wallet balance: '+ wallet_xmr_formatted +' XMR')

    conn.commit()
    conn.close()

def walletStats(wallet, monitor_hashrate, percentage_drop):
    global a_protocol, a_url, a_port, denom, hashrate_translations

    dbSetup()

    request_url = a_protocol + a_url + a_port + '/stats_address?address=' + wallet
    r = requests.get(request_url)
    result = r.json()

    getStats(wallet, int(result['stats']['balance']), denom)

    if monitor_hashrate:

        current_hashrate = result['stats']['hashrate']
        hash_elements = current_hashrate.split(' ')
        base_hash = int( float(hash_elements[0]) * hashrate_translations[hash_elements[1]] )

        previous_hash_rates = updateHashRate(wallet, base_hash)
        
        if (len(previous_hash_rates) >= 2):
            hashrate_only = [row[1] for row in previous_hash_rates]

            last_rate = hashrate_only[-1:][0]
            second_last = hashrate_only[-2:-1][0]

            mean = sum(hashrate_only[:-1]) / len(hashrate_only[:-1])
            calculated_percentage = (100 - percentage_drop) / 100

            check_one = check_two = False
            if (last_rate / second_last) < calculated_percentage:
                check_one = True
                print('Latest hash rate is ' + str(percentage_drop) + '% lower than second-latest hash rate')
                
            if (last_rate / mean) < calculated_percentage:
                check_two = True
                print('Latest hash rate is ' + str(percentage_drop) + '% lower than average hash rate')

            if check_one & check_two:
                print('Sending hashrate notification...')
                pb.push_note(str(percentage_drop) + '% Hash Rate Drop on ' + a_url, 'Latest hash rate of ' + current_hashrate + ' is ' + str(percentage_drop) + '% lower than previous and average hash rate.')
            else:
                print('Latest hash rate is within ' + str(percentage_drop) + '% of previous and average hash rate')

def lastBlock():
    global a_protocol, a_url, a_port, denom
    request_url = a_protocol + a_url + a_port + '/stats'
    r = requests.get(request_url)
    result = r.json()
    denom = int(result['config']['coinUnits'])
    date = datetime.utcfromtimestamp(int(result['pool']['stats']['lastBlockFound']) / 1000)
    now = datetime.utcnow()
    delta = now - date

    if delta.total_seconds() <= check_time:
        print('New block found in the last '+ str(check_time/60) +' minutes! Yay!')
        pb.push_note('New Block Found on ' + a_url + '!', 'New block found at ' + date.isoformat())
    else:
        print('No new blocks in the last '+ str(check_time/60) +' minutes')

@click.command()
@click.option('-u', '--apiurl', required=True, type=click.STRING, help='Pool API URL')
@click.option('-p', '--port', required=True, default=80, help='Pool API port')
@click.option('-s', '--ssl', default=False, is_flag=True, help='SSL mequest mode')
@click.option('-c', '--check', default=5, help='Number of minutes in the past to check for found block')
@click.option('-w', '--wallet', default=False, help='Wallet address for wallet stats')
@click.option('-m', '--hashratemonitorpercent', type=click.IntRange(1, 100, clamp=True), help='Notify if hashrate falls below set percentage between 1 and 100 (as an integer). 20 or more is recommended. Must be used with a wallet address.')

def poolnotify(apiurl, wallet, ssl, port, check, hashratemonitorpercent):
    """ Script to monitor Cryptonote Universal Pool API for new blocks """
    global a_protocol, a_url, a_port, db, check_time

    check_time = check * 60

    if ssl:
        a_protocol = 'https://'
    else:
        a_protocol = 'http://'

    if port != 80:
        a_port = ':' + str(port)

    if apiurl:
        a_url = apiurl
        lastBlock()

        if wallet:
            
            monitor_hashrate = False
            if hashratemonitorpercent:
                monitor_hashrate = True

            walletStats(wallet, monitor_hashrate, hashratemonitorpercent)


    last_check = datetime.utcnow().isoformat()
    print('Last check at '+ last_check)

if __name__ == '__main__':
    poolnotify()
    