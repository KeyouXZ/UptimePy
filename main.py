import os, socket, time, json
from datetime import datetime
import requests as rq
from urllib.parse import urlparse
from dotenv import load_dotenv as ld

# Load enviroments
ld()
NTFY_SERVER = os.getenv("NTFY_SERVER") or "https://ntfy.sh"
NTFY_TOPIC = os.getenv("NTFY_TOPIC")
INTERVAL = os.getenv("INTERVAL") or 120

# Validate enviroment
if not NTFY_TOPIC:
    print("You must set your ntfy topic in .env file")
    exit(1)

def save_data(data):
    with open('config.json', 'w') as file:
        json.dump(data, file, indent=4)

def read_data():
    try:
        with open("config.json", "r") as file:   
            return json.load(file)

    except FileNotFoundError as e:
        return {}

def send_notification(url, status):
    name = names[urls.index(url)]
    post_url = f"{NTFY_SERVER}/{NTFY_TOPIC}"
    data = f"{name} is {status}\nURL: {url}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    print(f"{url} is {status}")
    response = rq.post(post_url, data=data)
    
def check_tcp_connection(url):
    parsed_url = urlparse(url)
    tcp_host, tcp_port = parsed_url.hostname, parsed_url.port
    try:
         with socket.create_connection((tcp_host, tcp_port), timeout=5):
              return True
    except (socket.timeout, socket.error) as e:
        return False

def get_request(urls, statuses):
    print("=" * 30)
    
    for url in urls:
        print(f"Checking {url} ...")
        
        index = urls.index(url)
        try:
            if url.startswith("http://") or url.startswith("https"):
                get = rq.get(url, timeout=5)
                
            elif url.startswith("tcp://") or url.startswith("udp://"):
                get = check_tcp_connection(url)
                
            else:
                print(f"Connection type not supported: {url}\n")
                continue

            # Send Status
            if get:
                if statuses[index] == "Online":
                    continue
                    
                statuses[index] = "Online"
                    
                send_notification(url, statuses[index])
                save_data({"names": names, "urls": urls, "statuses": statuses})
                
            elif not get:
                if statuses[index] == "Offline":
                    continue
                
                statuses[index] = "Offline"
                send_notification(url, statuses[index])
                save_data({"names": names, "urls": urls, "statuses": statuses})

                
        except rq.RequestException:
            if statuses[index] == "Offline":
                continue

            statuses[index] = "Offline"
            
            send_notification(url, statuses[index])
            save_data({"names": names, "urls": urls, "statuses": statuses})
            
    time.sleep(int(INTERVAL))
    read_data()
    get_request(urls, statuses)

# Load Data
monit_data = read_data()

names = monit_data.get('names', [])
urls = monit_data.get("urls", [])
statuses = monit_data.get("statuses", [])

if __name__ == __name__:
    try:
        start_message="Monitoring Device Started"
        rq.post(f"{NTFY_SERVER}/{NTFY_TOPIC}", data=start_message)
        print(start_message)

        get_request(urls, statuses)
    except KeyboardInterrupt:
        stop_message = "Monitoring Device Stoped"
        rq.post(f"{NTFY_SERVER}/{NTFY_TOPIC}", data=stop_message)
        print(stop_message)
        exit(1)


