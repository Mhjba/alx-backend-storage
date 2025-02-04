#!/usr/bin/env python3
"""List all documents in Python"""
import pymongo


def list_all(mongo_collection):
    """function to list all doc in a collection"""

    if mongo_collection is None:
        return []
    return list(mongo_collection.find())
