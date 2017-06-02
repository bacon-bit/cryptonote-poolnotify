# Cryptonote Universal Pool Notifier

Checks [Cryptonote Universal Pool](https://github.com/fancoder/cryptonote-universal-pool) mining pools and sends notifications through Pushbullet. 

- Script was built for Python 3.6

## Setup

1. Clone the repo [] and cd into the poolnotify folder
2. Set up the virtual environment by running `python3 -m venv ./` 
3. Activate the virtual environment [docs](https://docs.python.org/3/library/venv.html#creating-virtual-environments)
    - On Mac/Linux: `source ./bin/activate` 
    - On Windows cmd.exe: `Scripts\activate.bat`
    - On Windows Powershell: `Scripts\Activate.ps1`
4. Run `pip install -r requirements.txt` to install required packages
5. Close the virtual environment `deactivate`
6. Replace "pushbullet_api_key" with your Pushbullet API key on this line in poolnotify.py:
    - `pb = Pushbullet(pushbullet_api_key)`  
7. Make sure poolnotify.py is executable (eg. `chmod +x poolnotify.py`)
8. Test the script by running `./poolnotify.py --help`
9. You can now run poolnotify.py as a script and add it as a cron task

## Run

To find the API Url, port, and whether or not the API supports SSL, go to the pool's config.js, eg. http://aminingpool.com/config.js.

Here's an example of a pool's config.js api variable, and how you would run poolnotify with that information:

```
var api = "https://aminingpool.com:8119";
```

You would run the script with the following options to be check if there was a block in the last 5 minutes:

`./poolnotify -u aminingpool.com -p 8119 -s -c 5`

You can schedule this task to run every 5 minutes with cron to be notified when a new block is found on your pool!

To be notified when your wallet balance increases after a block is confirmed, just add the address with the -w option:

`./poolnotify -u aminingpool.com -p 8119 -s -c 5 -w wallet_address_here`

## Donations

### XMR

`45gE6V1ScLtg3CLgvf2uDx6TaG996DasvMb2tx3yC6poc5y8Ljkzdk2WXj7TBJ8oMidLzbsvAYecZC9RxB33wnFaBi9uDsd`

### BTC

`1CtwQ65Ns8H8oPaY3Jc2vT18ZzAKHr6Lia`

