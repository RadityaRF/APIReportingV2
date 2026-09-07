PRODUCT_MAP = {
    1: "ASKRED || Briguna Kawan",
    5: "ASKRED || Briguna Karya",
    6: "AKUA",
    7: "ASMIK",
    8: "AUO",
    9: "ASKRED || BRIGUNA",
    14: "ASMIK || BRILINK",
    15: "AUO || BRILINK",
    16: "KBG",
    17: "ASMIK || BRILINK WIC",
    18: "ASMIK || BRILINK NON WIC",
    21: "AKUA KPP",
    22: "AUO || BRILINK",
    25: "KPRS"
}


def enrich_product_data(rows):
    # 1. Map existing (transaction_date, product_id) tuples to their total count
    lookup = {
        (r["transaction_date"], r["product"]): r["total_transaction"]
        for r in rows
    }
    
    # 2. Extract all unique dates present in the dataset
    distinct_dates = {r["transaction_date"] for r in rows}
    
    # 3. Build a full matrix of (dates x all products)
    result = []
    for date in sorted(distinct_dates):
        for prod_id, prod_name in PRODUCT_MAP.items():
            result.append({
                # "transaction_date": date,
                # "product": prod_id,
                "product_name": prod_name,
                "total_transaction": lookup.get((date, prod_id), 0)
            })
            
    return result