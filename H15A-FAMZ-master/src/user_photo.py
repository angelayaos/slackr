from PIL import Image
from auth_server import *
from error import *
from other import *
import pytest
from storage import data
from json import dumps
import requests
import urllib
from flask import Flask, request
from storage import data
'''
Given a URL of an image on the internet, crops the image within bounds (x_start, y_start) and (x_end, y_end). Position (0,0) is the top left.
inputs: token, img_url, x_start, y_start, x_end, y_end
METHODS=POST
InputError:
- img_url returns an HTTP status other than 200.
- any of x_start, y_start, x_end, y_end are not within the dimensions of the image at the URL.
- image uploaded is not a JPG
'''

def user_profile_upload_photo():
    #get the data
    info = request.get_json()
    token = info['token']
    img_url = info['img_url']
    x_start = info['x_start']
    x_end = info['x_end']
    y_start = info['y_start']
    y_end = info['y_end']
    #check token is valid, otherwise raise access error
    valid = False
    for user in data['users']: 
        if token == user['token']:
            valid = True
    if valid == False:
        raise AccessError("invalid token")
    #the image is opened from a url and stored in a variable 'image'
    #check the img_url link returns 200 HTTP status
    http_status = urllib.request.urlopen(img_url).getcode()
    if http_status != 200:
        raise InputError("Error retrieving image link. Please use a different link")
    image = Image.open(urllib.request.urlopen(img_url))
    #finding the width and height of the image in order to check boundaries are legal
    width, height = image.size
    #error checking for filetype - only jpg is allowed
    if ".jpg" or ".jpeg" not in image.filename:
        raise InputError("image must be jpg")
    #error checking for cropping limits
    x_width = x_end - x_start
    if (x_width > width):
        raise InputError(f"Unable to crop image. x_start->x_end must be less than {width}")
    y_height = y_end - y_start
    if (y_height > height):
        raise InputError(f"Unable to crop image. y_start->y_end must be less than {height}")        
    crop = (x_start, y_start, x_end, y_end)
    cropped_image = image.crop(box)
    
    IMAGE_DIRECTORY = os.path.join(server_dir, 'static/pictures/')    
    file.save(os.path.join(app.config['IMAGE_DIRECTORY'], cropped_image))
    os.path.realpath(os.getcwd())
    send_from_directory(app.config['UPLOAD_FOLDER'], cropped_image)
    

