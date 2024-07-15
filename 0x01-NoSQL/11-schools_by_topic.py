#!/usr/bin/env python3
"""list of schools with topics"""
import pymongo


def schools_by_topic(mongo_collection, topic):
    """find by specific value"""

    return mongo_collection.find({"topics": topic})
