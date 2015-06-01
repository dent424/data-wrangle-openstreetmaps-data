# -*- coding: utf-8 -*-
"""
Created on Mon Jun 01 17:39:59 2015

@author: Alex
"""


###Iterative Parsing
import xml.etree.ElementTree as ET
import pprint

def count_tags(filename):
    tags = {}
    for event, elem in ET.iterparse(filename):
        if elem.tag in tags:
            #print "before", elem.tag, tags[elem.tag] 
            tags[elem.tag]=tags[elem.tag]+1
            #print "after", elem.tag, tags[elem.tag]
        else:
            tags[elem.tag]=1
            #print "added", elem.tag, tags[elem.tag]
    return tags


###Tag Types
import xml.etree.ElementTree as ET
import pprint
import re

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


def key_type(element, keys):
    if element.tag == "tag":
        key = element.attrib['k']
        if re.search(lower, key):
            keys["lower"]=keys["lower"]+1
        elif re.search(lower_colon, key):
            keys["lower_colon"]=keys["lower_colon"]+1
        elif re.search(problemchars, key):
            keys["problemchars"]=keys["problemchars"]+1
        else:
            keys["other"]=keys["other"]+1
    return keys



def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys

###Exploring Users
import xml.etree.ElementTree as ET
import pprint
import re

def get_user(element):
    return


def process_map(filename):
    users = set()
    for _, element in ET.iterparse(filename):
        try: 
            if element.attrib["user"] not in users:
                users.add(element.attrib["user"])
        except:
            continue
    return users

###improving street names
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "example.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]

# UPDATE THIS VARIABLE
mapping = { "St": "Street",
            "St.": "Street",
            "Ave" : "Avenue",
            "Rd" : "Road",
            "Rd." : "Road"
            }


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])

    return street_types


def update_name(name, mapping):
    m = street_type_re.search(name)
    if m.group(0) in mapping:
        name = re.sub(street_type_re,mapping[m.group(0)],name)
    return name

###Preparing for Database
import xml.etree.ElementTree as ET
import pprint
import re
import codecs
import json
import string

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
addr = re.compile("addr:")
colon = re.compile(":")


CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
LATLON = ["lat","lon"] 

def shape_element(element):
    node = {}
    created = {}
    address = {}
    lat = ""
    lon = ""
    node_refs=[]
    if element.tag == "node" or element.tag == "way" :
        if element.tag == "node":
            node["type"]="node"
        elif element.tag == "way":
            node["type"]="way"
        for attribute in element.attrib:
            if attribute in CREATED:
                created[attribute] =element.attrib[attribute]
            elif attribute in LATLON:
                if attribute == "lat":
                    lat = float(element.attrib["lat"])
                elif attribute == "lon":
                    lon = float(element.attrib["lon"])
            else:
                node[attribute]=element.attrib[attribute]
        node["created"]=created
        if lat != 0 and lon != 0:
            node["pos"]=[lat,lon]
        for child in element:
            if child.tag == "tag":
                if re.search(problemchars, child.attrib["k"]):
                    continue
                elif re.search(addr, child.attrib["k"]):
                    key = child.attrib["k"].replace("addr:","")
                    if re.search(colon, key):
                        continue
                    else:
                        address[key]=child.attrib["v"]
                else:
                    node[child.attrib["k"]]=child.attrib["v"]
            elif child.tag == "nd":
                node_refs.append(child.attrib["ref"])
                
        if bool(address):
            node["address"]=address
        if node_refs:
            node["node_refs"]=node_refs
        return node
        
    else:
        return None


def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    pprint.pprint(data)
    return data