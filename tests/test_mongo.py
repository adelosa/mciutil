#!/usr/bin/env python
import pymongo
from datetime import datetime


def insert(db):
    result = db.restaurants.insert_one(
        {
            "address": {
                "street": "2 Avenue",
                "zipcode": "10075",
                "building": "1480",
                "coord": [-73.9557413, 40.7720266]
            },
            "borough": "Manhattan",
            "cuisine": "Italian",
            "grades": [
                {
                    "date": datetime.strptime("2014-10-01", "%Y-%m-%d"),
                    "grade": "A",
                    "score": 11
                },
                {
                    "date": datetime.strptime("2014-01-16", "%Y-%m-%d"),
                    "grade": "B",
                    "score": 17
                }
            ],
            "name": "Vella",
            "restaurant_id": "41704620"
        }
    )

    print(result)
    print(result.inserted_id)


def find_data(db):
    # cursor = db.restaurants.find({"cuisine": "Australian"})
    # cursor = db.restaurants.find({"grades.grade": "A"})
    cursor = db.restaurants.find({"grades.score": {"$gt": 60},
                                  "cuisine": "Italian"}
                                 ).sort("address.zipcode", pymongo.ASCENDING)

    for document in cursor:
        print(document)

    print(
        db.restaurants.count({"grades.score": {"$gt": 60},
                              "cuisine": "Italian"})
    )


def format_string():
    item_count = 100000
    total_items = 200000
    print(
        "processed {percent_complete}%".format(
            percent_complete=(
                round(
                    item_count / float(total_items) * 100, 0
                )
            )
        )
    )


def mci_single_query(db):
    # print number of records
    print(db.mastercardtransactions.count({"DE43_POSTCODE": "4103"}))

    cursor = db.mastercardtransactions.find({"DE43_POSTCODE": "4103"})
    for doc in cursor:
        print(doc)


def mci_breakdown_by_mcc_by_ird(db):
    cursor = db.mastercardtransactions.aggregate(
        [
            # {"$match": {"DE43_POSTCODE": "4103"}},
            {"$sort": {"DE26": 1}},
            {"$group":
                {
                    "_id": {"mcc": "$DE26", "postcode": "$DE43_POSTCODE",
                            "ird": "$PDS0158"},
                    "count": {"$sum": 1},
                    "total": {"$sum": "$DE4"}
                }
             },
            {"$group":
                {
                    "_id": {"mcc": "$_id.mcc", "postcode": "$_id.postcode"},
                    "data": {"$push": "$$ROOT"}
                }

             },
            {"$group":
                {
                    "_id": "$_id.mcc",
                    "data": {"$push": "$$ROOT"}
                }
             }
        ]
    )
    for doc in cursor:
        print(doc)


def mci_queries(db):

    cursor = db.mastercardtransactions.aggregate(
        [
            {"$match": {"DE43_POSTCODE": "4103"}},
            {"$sort": {"DE42": 1}},
            {"$group":
                {
                    "_id": {"caid": "$DE42", "ird": "$PDS0158"},
                    "count": {"$sum": 1},
                    "total": {"$sum": "$DE4"}
                }
             },
            # groups into caid
            {"$group":
                {
                    "_id": "$_id.caid",
                    "data": {"$push": "$$ROOT"}
                }
             }

            # dictionary with caid and list of all transactions
            # {"$group":
            #     {
            #         "_id": "$DE42",
            #         "transactions": {"$push": "$$ROOT"}
            #     }
            # },
        ]
    )
    for doc in cursor:
        print(doc)


if __name__ == '__main__':
    client = pymongo.MongoClient("mongodb://192.168.99.100:27017")
    db = client['test']
    # insert(db)
    # find_data(db)
    # mci_queries(db)
    # mci_single_query(db)
    mci_breakdown_by_mcc_by_ird(db)
    # format_string()
