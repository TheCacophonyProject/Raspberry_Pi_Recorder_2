# Maximum size of previous recordings to upload in MB
RECORDINGS_FOLDER_MAX_SIZE = 2000

import json
import requests
import shutil

def post_processing(thermalCamera, irCamera, device, queue):
    if not irCamera.active:
        just_thermal_post_process(thermalCamera, device, queue)
        return

    # Do required post processing
    d = thermalCamera.post_process()
    irCamera.post_process(d)

    # Get files and metadata to upload.
    files = {
        "irVideo": open(irCamera.get_file()),
        "thermalVideo": open(thermalCamera.get_file())
        }
    data = {
        "irData": json.dumps(irCamera.get_meta()),
        "thermalData" : json.dumps(thermalCamera.get_meta())
        }

    url = device.serverUrl + '/api/v1/thermalirvideopair'
    upload(url, files, data, device)
    
    # Remove recording
    shutil.rmtree(thermalCamera.recordingFolder)

def just_thermal_post_process(thermalCamera, device, queue):

    jwt = device.privateSettings["jwt"]
    if jwt == None:
        device.get_new_jwt()
        jwt = device.jwt
        queue.put(('NEW_JWT', jwt))

    # Do required post processing
    d = thermalCamera.post_process()

    files = { "file": open(thermalCamera.get_file()) }
    data = { "data": json.dumps(thermalCamera.get_meta()) }

    url = device.serverUrl + '/api/v1/thermalvideorecordings'
    upload(url, files, data, device)

def upload(url, files, data, device):
    """ Uploads flies and data to the server. """
    # Get JWT from device. If device does not have a JWT yet then get a new JWT
    # and send it to the main process via the queue.
    jwt = device.privateSettings["jwt"]
    if jwt == None:
        device.get_new_jwt()
        jwt = device.jwt
        queue.put(('NEW_JWT', jwt))
    headers = {'authorization': device.privateSettings['jwt']}
    try:
        r = requests.post(url, files = files, data = data, headers = headers)
        print("Upload request finished with status: " + str(r.status_code))
        
    except Exception as e:
        print(e)
        print("Error with uploading files.")

    
