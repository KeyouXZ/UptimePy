import os, socket, time, json
from datetime import datetime
from colorama import init, Fore, Style, Back
import requests as rq
from urllib.parse import urlparse
from dotenv import load_dotenv as ld

dataMap = {}
INFO_MESSAGE = Fore.BLUE + Style.BRIGHT + "[Info] " + Style.RESET_ALL
# Load enviroments
ld()
NTFY_SERVER = os.getenv("NTFY_SERVER") or "https://ntfy.sh"
NTFY_TOPIC = os.getenv("NTFY_TOPIC")
INTERVAL = os.getenv("INTERVAL") or 120

# Analizing some enviroments
if not NTFY_TOPIC:
    print(Fore.RED + Style.BRIGHT + "[Error] You must set your ntfy topic in .env file" + Style.RESET_ALL)
    exit(1)

# Analyze whether an Interval is a number or not
try:
    int(INTERVAL)
except:
    print(Fore.RED + Style.BRIGHT + "[Error] Interval must be number" + Style.RESET_ALL)
    exit(1)

def check_NTFY_SERVER():
    try:
        get = rq.get(NTFY_SERVER, timeout=5)
        if not get:
            print(Fore.RED + Style.BRIGHT + f"[Error] Cannot connect to ntfy server ({NTFY_SERVER})" + Style.RESET_ALL)
            exit(1)
    except rq.RequestException:
        print(Fore.RED + Style.BRIGHT + f"[Error] Cannot connect to ntfy server ({NTFY_SERVER})" + Style.RESET_ALL)
        exit(1)

def save_data(url, status):
    monitor = {
        "name": dataMap[url]["name"],
        "url": url,
        "status": status
    }
    
    dataMap[url] = monitor
    

def read_data(mode):
    try:
        if mode == 1:
            urls = []
            
            for data in dataMap.values():
                urls.append(data["url"])
                
            return urls
                
        elif mode == 2:
            with open("config.json", "r") as file:   
                data = json.load(file)
            
                urls = []
                    
                for name, url in data.items():
                    urls.append(url)
                    
                    monitor = {
                        "name": name,
                        "url": url,
                        "status": None
                    }
                        
                    dataMap[url] = monitor
                        
                return urls

    except FileNotFoundError:
        print(Fore.RED + Style.BRIGHT + "[Error] Cannot get config file" + Style.RESET_ALL)
        exit(1)

def send_notification(url):
    name = dataMap[url]["name"]
    status = dataMap[url]["status"]
    post_url = f"{NTFY_SERVER}/{NTFY_TOPIC}"
    data = f"{name} is {status}\nURL: {url}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    print(INFO_MESSAGE + f"{url} is {status}")
    response = rq.post(post_url, data=data)
    
def check_tcp_connection(url):
    parsed_url = urlparse(url)
    tcp_host, tcp_port = parsed_url.hostname, parsed_url.port
    try:
         with socket.create_connection((tcp_host, tcp_port), timeout=5):
              return True
    except (socket.timeout, socket.error) as e:
        return False

def get_request(urls):
    
    for url in urls:
        print(INFO_MESSAGE + f"Checking {url} ...")
        
        index = urls.index(url)
        try:
            if url.startswith("http://") or url.startswith("https"):
                get = rq.get(url, timeout=5)
                
            elif url.startswith("tcp://") or url.startswith("udp://"):
                get = check_tcp_connection(url)
                
            else:
                print(Fore.RED + Style.BRIGHT + f"[Error] Connection type not supported: {url}" + Style.RESET_ALL)
                continue

            # Send Status
            if get:
                if dataMap[url]["status"] == "Online":
                    continue
                    
                save_data(url, "Online")
                send_notification(url)
                
            elif not get:
                if dataMap[url]["status"] == "Offline":
                    continue
                
                save_data(url, "Offline")
                send_notification(url)

                
        except rq.RequestException:
            if dataMap[url]["status"] == "Offline":
                continue
            
            save_data(url, "Offline")
            send_notification(url)
            
    print(Fore.YELLOW + Style.BRIGHT + "=" * 40 + Style.RESET_ALL)
    time.sleep(int(INTERVAL))
    get_request(read_data(1))

if __name__ == "__main__":
    try:
        check_NTFY_SERVER()
        start_message="Monitoring Device Started"
        rq.post(f"{NTFY_SERVER}/{NTFY_TOPIC}", data=start_message)
        print(Fore.YELLOW + Style.BRIGHT + "=" * 40 + Style.RESET_ALL)
        print(INFO_MESSAGE + start_message)
        print(INFO_MESSAGE + "Press CTRL+C to exit")
        print(Fore.YELLOW + Style.BRIGHT + "=" * 40 + Style.RESET_ALL)
        get_request(read_data(2))
        
    except (Exception, KeyboardInterrupt):
        stop_message = "Monitoring Device Stoped"
        rq.post(f"{NTFY_SERVER}/{NTFY_TOPIC}", data=stop_message)
        print(INFO_MESSAGE + stop_message)
        exit(1)
        
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"[Error] {e}" + Style.RESET_ALL)
        exit(1)
        


