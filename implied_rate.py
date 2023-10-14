from    data.cat_df import  cat_df
import  polars      as      pl
from    sys         import  argv


# python CME_HOX2023 12 2023-08-01 2024-01-01


def report(df: pl.DataFrame):

    pass


if __name__ == "__main__":
    
    symbol  = argv[1]
    start   = argv[2]
    end     = argv[3]

    cat_df(
        "futs", 
        symbol, 
        start, 
        end
    ).sort(
        [ "date", "year", "month" ]
    ).select(
        [
            "contract_id",
            "date",
            "name",
            "month",
            "year",
            "settle",
            "dte"
        ]
    )