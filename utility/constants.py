import os

appdata = os.getenv("APPDATA")
if not appdata:
    # fallback for Linux/macOS
    appdata = os.path.expanduser("~")

BASEPATH = os.path.join(appdata, "TradingBot")

# Example subpaths
LOGPATH = os.path.join(BASEPATH, "logs")
CONFIGPATH = os.path.join(BASEPATH, "config")
DATAPATH = os.path.join(BASEPATH, "data")
DATA = DATAPATH
CACHEPATH = os.path.join(BASEPATH, "cache")
DATA_DUMP = os.path.join(BASEPATH, 'data_dump')
KEYPATH = os.path.join(BASEPATH, 'key')


def get_key():
    key_dict = {}
    api_file = KEYPATH +"/publicKey.txt"
    secret_file = KEYPATH +"/privateKey.txt"

    # Read the first line of each file into string variables
    with open(api_file, "r") as f:
        api_key = f.readline().strip()  # remove trailing newline

    with open(secret_file, "r") as f:
        api_secret = f.readline().strip()

    # Print to confirm
    key_dict['api_key'] = api_key
    key_dict['api_secret'] = api_secret
    return key_dict

def get_key_linux():
    home = os.path.expanduser("~")
    api_file = os.path.join(home, "publicKey.txt")
    secret_file = os.path.join(home, "privateKey.txt")

    with open(api_file, "r") as f:
        api_key = f.readline().strip()

    with open(secret_file, "r") as f:
        api_secret = f.readline().strip()

    return {"api_key": api_key, "api_secret": api_secret}

# Ensure folders exist
for path in [BASEPATH, LOGPATH, CONFIGPATH, DATAPATH, CACHEPATH]:
    os.makedirs(path, exist_ok=True)

if __name__ == "__main__":
    print(get_key_linux())
