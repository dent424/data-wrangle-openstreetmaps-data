# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 19:13:17 2015

@author: Alex
"""

import xml.etree.ElementTree as ET
import re
from collections import defaultdict
import codecs
import json

#expected street types
#more unusual street types "Park", "Cutoff", and "View" were confirmed with google maps.
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Terrace", "Circle", "Way", "Turnpike", "Trafficway", "Plaza", "Highway", "Park",
            "Cutoff", "View"]

expected_direction = ["North","South","East","West","Northeast","Southeast","Northwest","Southwest"]
#mappings to correct street types
mapping = { "St": "Street",
            "St.": "Street",
            "Ave" : "Avenue",
            "Rd" : "Road",
            "Rd." : "Road", #after this added second run
            "terrace" : "Terrace",
            "ter" : "Terrace",
            "street" : "Street",
            "st." : "Street",
            "st" : "Street",
            "rd" : "Road",
            "pl" : "Place",
            "dr" : "Drive",
            "ct" : "Court",
            "circle" : "Circle",
            "ave" : "Avenue",
            "STREET" : "Street",
            "ST" : "Street",
            "HWY" : "Highway",
            "Dr" : "Drive",
            "Dr.": "Drive",
            "Ct" : "Court",
            "Blvd" : "Boulevard",
            "Blvd." : "Boulevard",
            "Ln" : "Lane",
            "Pkwy" : "Parkway",
            "RD" : "Road",
            "Hwy" : "Highway",
            "Trfy" : "Trafficway",
            "cCourt" : "Court",
            "Q.S.S." : "SE Quincy Street",
            "West Market" : "West Market Street",
            "US 75 (KS)" : "US 75",
            "Southwest Indian" : "Southwest Indian Hills Road",
            "Baltimore" : "Baltimore Avenue" 
            }

direction_mapping = {"N ":"North ",
                     "n ":"North ",
                     "N. ":"North ",                                         
                     "S ":"South ",
                     "S. ":"South ",
                     "E ":"East ",
                     "E. ":"East ",
                     "w ":"West ",
                     "W ":"West ",
                     "W. ":"West ",
                     "NE ":"Northeast ",
                     "NE. ":"Northeast ",
                     "SE ":"Southeast ",
                     "SE. ":"Southeast ",
                     "NW ":"Northwest ",
                     "NW. ":"Northwest ",
                     "SW ":"Southwest ",
                     "SW. ":"Southwest "}

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
LATLON = ["lat","lon"]

data="C:\Users\Alex\Desktop\UdacityProjects\Map_data.osm"#"test.xml"

#section of regular expressions
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
directions_re = re.compile('^(N |S |E |W |N. |S. |E. |W. |NW |SW |NE |SE |NW. |SW. |NE. |SE. )', re.IGNORECASE)
addr = re.compile("addr:")
colon = re.compile(":")


def main():
    print "RUNNING NODE TEST"    
    node_test = open("node_test.txt", "w+")    
    nodes=count_tags(data)
    pprint.pprint(nodes)
    node_test.write(str(nodes))    
    node_test.close()
    print "RUNNING ERROR CHECK"
    key_test = open("key_test.txt", "w+")    
    keys = process_map(data)
    pprint.pprint(keys)
    key_test.write(str(keys))    
    key_test.close()
    print "RUNNING FIRST AUDIT"
    type_test = open("type_test.txt", "w+")    
    st_types, st_directions = audit(data)
    pprint.pprint(dict(st_directions))
    pprint.pprint(dict(st_types))
    type_test.write(str(st_types))    
    type_test.close()
    print "CREATING JSON"    
    jsonify(data)

def count_tags(filename):
    #counts tag types    
    tags = {}
    for event, elem in ET.iterparse(filename):
        if elem.tag in tags:
            #print "before", elem.tag, tags[elem.tag] 
            tags[elem.tag]=tags[elem.tag]+1
            #print "after", elem.tag, tags[elem.tag]
            elem.clear() 
        else:
            tags[elem.tag]=1
            #print "added", elem.tag, tags[elem.tag]
            elem.clear() 
    return tags

def key_type(element, keys):
    #checks keys for problems    
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
    #creates the dictionary keys and calls key_type
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)
        element.clear() 
    return keys

def audit_street_type(street_types, street_name):
    #checks to see if the street name is expected. If not, adds it to street_types dictionary
    #returns original street name if expected or returns fixed street name if not expected    
    #returns text for street type    
    m = street_type_re.search(street_name)
    if m:
        #street_type = m.group()
        #calls update_name to update street types that are updatable        
          
        street_name = update_name(street_name, mapping)        

        #returns text for updated street type        
        m = street_type_re.search(street_name)
        street_type = m.group()        
        #places unexpected street types in a dictionary        
        if street_type not in expected:
            street_types[street_type].add(street_name)           
            return street_name
        else:
            return street_name

def audit_street_direction(street_directions, street_name):
    #converts all variants of North, South, East, West to the same wording.
    if street_name:         
        m = directions_re.search(street_name)    
        if m:
            #street_direction = m.group()        
            street_name = update_direction(street_name, direction_mapping)
            m = directions_re.search(street_name)
            if m:            
                street_direction=m.group()
                if street_direction not in expected_direction:            
                    street_directions[street_direction].add(street_name)
                    return street_name
                else:
                    return street_name
            else:
                return street_name

def is_street_name(elem):
    #checks to see if something is a street      
    return (elem.attrib['k'] == "addr:street")
    
    


def audit(osmfile):
    #audits the data running the audit_street_type function on all tags that are street names
    osm_file = open(data, "r")
    street_types = defaultdict(set)
    street_directions = defaultdict(set)    
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):                    
                    street_name = audit_street_type(street_types, tag.attrib['v'])
                    street_name = audit_street_direction(street_directions, street_name)                    
                    tag.set('v', street_name)                                  
        elem.clear()        
    return street_types, street_directions
 


def update_name(name, mapping):
    #update name of street to that shown in mapping array
    m = street_type_re.search(name)
    if m.group(0) in mapping:
        name = re.sub(street_type_re,mapping[m.group(0)],name)
    return name

def update_direction(name, mapping):
    #updates the directions to be consistent. For example, makes S into South            
    m = directions_re.search(name)       
    if m.group(0) in mapping:
        name = re.sub(directions_re,mapping[m.group(0)],name)
    return name

def jsonify(file_in, pretty = False):
    # processes file into JSON
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for event, element in ET.iterparse(file_in, events=("start",)):     
            if element.tag == "node" or element.tag == "way":               
                for tag in element.iter("tag"):                   
                    if is_street_name(tag): 
                            m = street_type_re.search(tag.attrib['v'])
                            if m:
                                street_name = update_name(tag.attrib['v'], mapping)
                            m = directions_re.search(street_name)
                            if m:
                                street_name = update_direction(street_name, direction_mapping)
                                m = directions_re.search(street_name)
                                tag.set('v', street_name)
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
            element.clear()  
    #pprint.pprint(data)
    return data

def shape_element(element):
    #shapes element into JSON format
    node = {}
    created = {}
    address = {}
    lat = ""
    lon = ""
    node_refs=[]
    if element.tag == "node" or element.tag == "way" :
        if element.tag == "node":
            node["node_type"]="node"
        elif element.tag == "way":
            node["node_type"]="way"
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
        if lat != "" and lon != "":
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




main()
