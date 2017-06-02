#!bin/python3

import click, requests, sqlite3
from datetime import datetime
from pushbullet import Pushbullet

a_protocol = ''
a_url = ''
a_port = ''
denom = 1
check_time = 300
pb = Pushbullet(pushbullet_api_key)
db = 'poolstats.db'

def dbSetup():
    global db
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS stats (pool_wallet text UNIQUE, balance int, coin_units int, updated int)''')
    conn.commit()
    conn.close()

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

def walletStats(wallet):
    global a_protocol, a_url, a_port, denom

    dbSetup()

    request_url = a_protocol + a_url + a_port + '/stats_address?address=' + wallet
    r = requests.get(request_url)
    result = r.json()

    getStats(wallet, int(result['stats']['balance']), denom)

def lastBlock():
    global a_protocol, a_url, a_port, denom
    request_url = a_protocol + a_url + a_port + '/live_stats'
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

def poolnotify(apiurl, wallet, ssl, port, check):
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
            walletStats(wallet)

    last_check = datetime.utcnow().isoformat()
    print('Last check at '+ last_check)

if __name__ == '__main__':
    poolnotify()
    