import requests

# usage banner
print("run usage example")
url = "http://localhost:7057/usage"
data = {"ip": "172.17.0.2", "port": 5055}
req = requests.get(url, files=data)
print(req.text)

print("-" * 50)

# classify sample image
print("classify sample image")
url = "http://localhost:7057/predict"
data = {"ip": "172.17.0.2", "port": 5055, "img": open("./data/cat.jpg", "rb")}
req = requests.post(url, files=data)
print(req.text)
