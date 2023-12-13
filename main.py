import os, socket, time, json
from datetime import datetime
import requests as rq
from urllib.parse import urlparse

# Load Data
monit_data = [
    {"name": "Leurel", "url": "http://node2.leourel.com:25983", "status": ""},
    {"name": "Skyo", "url": "http://skyo.serveo.net", "status": ""},
    {"name": "Terraria", "url": "tcp://serveo.net:7777", "status": ""},
    {"name": "Lemehost", "url": "tcp://5.9.8.124:9254", "status": ""}
]

names = []
urls = []
statuses = []

for data in monit_data:
    names.append(data["name"])
    urls.append(data["url"])
    statuses.append(data["status"])
    
ntfy = "UptimeSkyo"
n = 0

def send_notification(url, status):
    name = names[urls.index(url)]
    post_url = f"http://ntfy.sh/{ntfy}"
    data = f"{name} is {status}\nURL: {url}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    response = rq.post(post_url, data=data)
    print(f"{url} is {status}\n")
    
def check_tcp_connection(url):
    parsed_url = urlparse(url)
    tcp_host, tcp_port = parsed_url.hostname, parsed_url.port
    try:
         with socket.create_connection((tcp_host, tcp_port), timeout=5):
              return True
    except (socket.timeout, socket.error) as e:
       return False

def get_request(urls, statuses, count):
    count = count + 1
    print("Time loop: ", count)
    
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
                
            elif not get:
                if statuses[index] == "Offline":
                    continue
                
                statuses[index] = "Offline"
                send_notification(url, statuses[index])
                
        except rq.RequestException:
            if statuses[index] == "Offline (Error)":
                continue

            statuses[index] = "Offline (Error)"
            
            send_notification(url, statuses[index])
            
    time.sleep(60)
    get_request(urls, statuses, n)

get_request(urls, statuses, n)


