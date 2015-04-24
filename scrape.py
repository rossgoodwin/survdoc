import requests
import sys

endPt = "https://word.camera/img"
inFn = sys.stdin.readlines()
headers = {'user-agent': 'my-app/0.0.1'}
# files = [{'file': open("collection 02/"+fn.strip(), 'rb')} for fn in inFn]


i = 0
for fn in inFn[4:5]:
	print "UPLOADING " + fn
	payload = {'Script': 'Yes'}
	files = {'file': open("collection 02/"+fn.strip(), 'rb')}
	response = requests.post(endPt, data=payload, files=files)
	print response.text
	# if response.history:
	#     print "SUCCESS"
	#     for resp in response.history:
	#         print resp.status_code, resp.url
	#     print "Final destination:"
	#     print response.status_code, response.url
	# else:
	#     print "FAILURE"
	#     print response.status_code, response.url

	i+=1