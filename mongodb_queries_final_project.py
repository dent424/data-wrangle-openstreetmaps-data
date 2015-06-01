# -*- coding: utf-8 -*-
"""
Created on Fri May 08 19:45:42 2015

@author: Alex
"""
#info from api.mongodb.org/python/current/tutorial.html
import pprint

db_names = "projectII"

def main():
    db = get_db(db_names)
    print db.maps.find_one()    
    #generate pipelines    
    users_pipeline = get_users_pipeline()
    node_pipeline = get_node_types_pipeline()
    shop_type_pipeline = get_shop_types_pipeline() 
    amenity_pipeline = get_amenity_types_pipeline()    
    top_amenity_pipeline = get_top_amenity_types_pipeline(3)    
    street_name_pipeline = get_street_names_pipeline(10)    
    street_name_number_pipeline = get_street_name_number_pipeline()  
    count_single_street_pipeline = count_single_streets_pipeline()
    result = aggregate(db, users_pipeline)    
    print "Number of users:", len(result["result"])
    result = aggregate(db, node_pipeline)
    print "Node Types:"
    pprint.pprint(result)
    result = db.maps.find({"amenity":{"$exists":1}}).count()    
    print "Number of Amenity Tags:", result    
    result = aggregate(db,amenity_pipeline)    
    pprint.pprint(result)   
    result = aggregate(db, top_amenity_pipeline)
    pprint.pprint(result)
    result = aggregate(db, street_name_number_pipeline)
    total_streets=len(result["result"])        
    print "Number of Unique Streets:", total_streets    
    result = aggregate(db, street_name_pipeline)
    pprint.pprint(result)
    result = aggregate(db, count_single_street_pipeline)
    single_streets = len(result["result"])
    print "Number of Streets Mentioned Once:", 100*single_streets/total_streets, "%"
    
    
def aggregate(db, pipeline):
    result = db.maps.aggregate(pipeline)
    return result

def get_db(db_name):
    from pymongo import MongoClient
    client = MongoClient()
    db = client[db_name]
    return db

def get_users_pipeline():
    pipeline = [{"$group":{"_id":{"user":"$created.user"}}}]
    return pipeline

def get_node_types_pipeline():
    pipeline = [{"$group":{"_id":"$node_type",
                           "count":{"$sum":1}}}]
    return pipeline    
    
def get_shop_types_pipeline():
    pipeline = {"$group":{"_id":"$shop", "count":{"$sum":1}}},{"$sort":{"count":-1}}
    return pipeline

def get_amenity_types_pipeline():
    pipeline = {"$group":{"_id":"$amenity", "count":{"$sum":1}}},{"$sort":{"count":-1}}
    return pipeline

def get_top_amenity_types_pipeline(number):
    pipeline = {"$match":{"amenity":{"$ne":None}}},{"$group":{"_id":"$amenity", "count":{"$sum":1}}},{"$sort":{"count":-1}},{"$limit":number}
    return pipeline

def get_street_name_number_pipeline():
    pipeline = {"$match":{"address.street":{"$ne":None}}},{"$group":{"_id":"$address.street", "count":{"$sum":1}}},{"$sort":{"count":-1}}
    return pipeline

def get_street_names_pipeline(number):
    pipeline = {"$match":{"address.street":{"$ne":None}}},{"$group":{"_id":"$address.street", "count":{"$sum":1}}},{"$sort":{"count":-1}},{"$limit":number}
    return pipeline

def count_single_streets_pipeline():
    pipeline = {"$match":{"address.street":{"$ne":None}}},{"$group":{"_id":"$address.street", "count":{"$sum":1}}},{"$match":{"count":1}}
    return pipeline

main()    