import  polars          as      pl
from    sys             import  argv
from    usda_api.fas    import  fas_client


FIELDS = {
    "Output":           "",
    "Total Supply":     "Total Distribution",
    "Trade":            "MY Exports",
    "Total Use":        "Consumption and Residual",
    "Ending Stocks":    "Ending Stocks"
}


def report(
    symbol: str,
    start:  int,
    end:    int
):

    res = fas_client.get_commodity_data(symbol, start, end)
    df  = pl.from_dict(res)

    df = df.filter(
        (pl.col("CountryName") == "United States")
    ).select(
        [
            "MarketYear",
            "CalendarYear",
            "Month",
            "AttributeDescription",
            "UnitDescription",
            "Value"
        ]
    )

    rows = df.rows()
    
    for row in rows:

        print(f"{row[0]:6}{row[1]:6}{row[2]:3}{row[3]:30}{row[4]:10}{row[5]:10}")

    pass


if __name__ == "__main__":

    symbol  = argv[1]
    start   = int(argv[2])
    end     = int(argv[3])

    report(symbol, start, end)