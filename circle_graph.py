#!/usr/bin/python

import math
from random import randint, random
import Image, ImageDraw, ImageFont
        
def draw_circle_graph(packageDict, image_name):
    package_count = len(packageDict)
    
    width, height = 1080, 1080
    radius = width/2.0 - 300
    
    image = Image.new('RGBA', (width,height))
    draw = ImageDraw.Draw(image)
    arial = ImageFont.truetype('./arialn.ttf', 20)
    
    #calculate x,y positions for packages
    for index, key in enumerate(sorted(packageDict.iterkeys())):
        package = packageDict[key]
        x = radius*math.cos(index/(0.5*package_count)*math.pi)
        y = radius*math.sin(index/(0.5*package_count)*math.pi)
        package.position = (width/2.0 + x, height/2.0 + y)
        package.colour = (randint(0,255), randint(0,255), randint(0,255), 255)
        while package.colour[0] + package.colour[1] + package.colour[2] < 255:
            package.colour = (randint(0,255), randint(0,255), randint(0,255), 255)
        sizeX = len(package.dependancies)
        sizeY = math.log(1 + len(package.rdeps)**40)
        
        rect = (package.position[0] - sizeX/2.0, package.position[1] - sizeY/2.0, sizeX, sizeY)
        x2 = width/2.0 + (sizeY+radius)*math.cos(index/(0.5*package_count)*math.pi)
        y2 = height/2.0 + (sizeY+radius)*math.sin(index/(0.5*package_count)*math.pi)
        draw.line( package.position + (x2, y2), package.colour)
        
        text = '{0} ({1},{2})'.format(package.name, len(package.dependancies), len(package.rdeps))
        tx = x2
        ty = y2
        tw, th = draw.textsize(text, font=arial)
        if index > 0.25*package_count and index < 0.75*package_count:
            tx -= draw.textsize(text, font=arial)[0]
        
        draw.text((tx, ty), text, font=arial, fill=(255,255,255,255))

    for package in packageDict.itervalues():
        print ('drawing {0} dependancies'.format(package.name))
        for dep in package.dependancies:
            # only draw deps that is in the package dictionary
            if dep.name in packageDict:
                x1, y1 = package.position
                x2, y2 = dep.position
                draw.line((x1, y1, x2, y2), dep.colour)
                
    image.save("{0}.jpg".format(image_name), "JPEG")
