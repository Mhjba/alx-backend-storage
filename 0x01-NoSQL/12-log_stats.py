#!/usr/bin/env python3
""" Task 12's module."""

from pymongo import MongoClient

    nginx_collection = client.logs.nginx

    total_logs = nginx_collection.count_documents({})
    print(f'{total_logs} logs')
    methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]
    print('Methods:')
    for method in methods:
        count = nginx_collection.count_documents({"method": method})
        print(f'\tmethod {method}: {count}')

    status_check = nginx_collection.count_documents(
        {"method": "GET", "path": "/status"}
        )
    print(f'{status_check} status check')

if __name__ == "__main__":
    client = MongoClient('mongodb://127.0.0.1:27017')
