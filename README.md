# Cryptonote Universal Pool Notifier

Checks [Cryptonote Universal Pool](https://github.com/fancoder/cryptonote-universal-pool) mining pools and sends notifications through Pushbullet. 

- Script was built for Python 3.6 but should work in other versions

## Setup

1. [Clone the repo](https://github.com/bacon-bit/cryptonote-poolnotify) and cd into the cryptonote-poolnotify folder that was just cloned
2. Run `pip install -r requirements.txt` to install required packages
3. Copy `pushbullet.config.default` to `pushbullet.config` and enter your Pushbullet API key in the newly-created file 
4. Make sure poolnotify.py is executable (eg. `chmod +x poolnotify.py`)
5. Test the script by running `./poolnotify.py --help`
6. You can now run poolnotify.py as a script or add it as a cron task

## Run

To find the API Url, port, and whether or not the API supports SSL, go to the pool's config.js, eg. http://aminingpool.com/config.js.

Here's an example of a pool's config.js api variable, and how you would run poolnotify with that information:

```
var api = "https://aminingpool.com:8119";
```

You would run the script with the following options to be check if there was a block in the last 5 minutes:

`./poolnotify.py -u aminingpool.com -p 8119 -s -c 5`

You can schedule this task to run every 5 minutes with cron to be notified when a new block is found on your pool!

### Wallet Balance Update Monitoring

To be notified when your wallet balance increases after a block is confirmed, just add the address with the -w option:

`./poolnotify.py -u aminingpool.com -p 8119 -s -c 5 -w wallet_address_here`

### Hash Rate Drop Monitoring

You can be notified when your last hash rate reported by the pool drops below a set amount using the `-m` flag with a percentage amount. Recommended amount is 20% or greater to account for regular fluctuations in hash rate.

`./poolnotify.py -u aminingpool.com -p 8119 -s -c 5 -w wallet_address_here -m 20`

You will only receive a notification if both of these conditions are true (assuming you set a check of 20%):

1. the latest hash rate is more than 20% lower than the previous hash rate
2. the latest hash rate is more than 20% lower than the average of the last 24 pool-reported hash rates

This should account for regular fluctuations and only notify you once for a sudden drop.

## Donations

### XMR

`45gE6V1ScLtg3CLgvf2uDx6TaG996DasvMb2tx3yC6poc5y8Ljkzdk2WXj7TBJ8oMidLzbsvAYecZC9RxB33wnFaBi9uDsd`

### BTC

`1CtwQ65Ns8H8oPaY3Jc2vT18ZzAKHr6Lia`

