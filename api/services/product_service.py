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


def enrich_and_group_by_product_name(rows):
    # 1. Pre-initialize ALL unique product names from PRODUCT_MAP with 0
    grouped = {name: 0 for name in set(PRODUCT_MAP.values())}

    # 2. Accumulate actual transactions from incoming rows
    for r in rows:
        product_name = r.get("product_name", "UNKNOWN")
        grouped[product_name] = grouped.get(product_name, 0) + r.get("total_transaction", 0)

    # 3. Output as a clean list of dicts for Grafana
    return [
        {
            "product_name": k,
            "total_transaction": v
        }
        for k, v in grouped.items()
    ]