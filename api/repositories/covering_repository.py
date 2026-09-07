from api.mongodb import db


class CoveringRepository:

    collection = db["CoveringFlag"]

    @classmethod
    def group_by_product_and_date(cls, start_dt_str, end_dt_str):
        pipeline = cls._base_pipeline(start_dt_str, end_dt_str, only_unsynced=False)
        return list(cls.collection.aggregate(pipeline, allowDiskUse=True))

    @classmethod
    def group_by_product_and_date_unsynced(cls, start_dt_str, end_dt_str):
        pipeline = cls._base_pipeline(start_dt_str, end_dt_str, only_unsynced=True)
        return list(cls.collection.aggregate(pipeline, allowDiskUse=True))

    @classmethod
    def _base_pipeline(cls, start_dt_str, end_dt_str, only_unsynced=False):

        match_stage = {
            "transaction_at": {
                "$gte": start_dt_str,
                "$lte": end_dt_str
            }
        }

        if only_unsynced:
            match_stage["$or"] = [
                {"HasSync": None},
                {"HasSync": 0}
            ]

        return [
            {"$match": match_stage},
            {
                "$addFields": {
                    "validation_oid": {
                        "$toObjectId": "$REF_IDValidation"
                    }
                }
            },
            {
                "$lookup": {
                    "from": "CoveringValidation",
                    "localField": "validation_oid",
                    "foreignField": "_id",
                    "as": "validation"
                }
            },
            {"$unwind": "$validation"},
            {
                "$group": {
                    "_id": {
                        "transaction_date": {
                            "$substrBytes": ["$transaction_at", 0, 10]
                        },
                        "product": "$validation.REF_IDSettingProduk"
                    },
                    "total_transaction": {"$sum": 1}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "transaction_date": "$_id.transaction_date",
                    "product": "$_id.product",
                    "total_transaction": 1
                }
            },
            {
                "$sort": {
                    "transaction_date": 1,
                    "product": 1
                }
            }
        ]
        
    @classmethod
    def get_unsynced_details_with_validation(cls, start_dt_str, end_dt_str):
        pipeline = [
            {
                "$match": {
                    "transaction_at": {
                        "$gte": start_dt_str,
                        "$lte": end_dt_str
                    },
                    "$or": [
                        {"HasSync": None},
                        {"HasSync": 0}
                    ]
                }
            },
            {
                "$addFields": {
                    "validation_oid": {
                        "$toObjectId": "$REF_IDValidation"
                    }
                }
            },
            {
                "$lookup": {
                    "from": "CoveringValidation",
                    "localField": "validation_oid",
                    "foreignField": "_id",
                    "as": "validation"
                }
            },
            {"$unwind": "$validation"},
            # Construct the exact shape/view you want
            {
                "$project": {
                    "_id": 0,
                    # CoveringFlag fields
                    "transaction_at": 1,
                    "HasSync": 1,
                    "REF_IDValidation": 1,
                    # Formatted views/extracted fields
                    "transaction_date": {
                        "$substrBytes": ["$transaction_at", 0, 10]
                    },
                    # Flattened fields from CoveringValidation
                    "product_id": "$validation.REF_IDSettingProduk",
                    "RemarkPremi": "$validation.RemarkPremi",
                    "NominalPremi": "$validation.NominalPremi",
                    "NomorPeserta": "$NomorPeserta"
                    # "validation_details": "$validation"  # Keep full validation object if needed
                }
            },
            {
                "$sort": {
                    "transaction_at": 1
                }
            }
        ]

        return list(cls.collection.aggregate(pipeline, allowDiskUse=True))


