import requests
url = 'https://www.cs.bgu.ac.il/~lich/imageUpload.php'
files = {'fileToUpload': open("picture.jpg", 'rb')}
requests.post(url, files=files)