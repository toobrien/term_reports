from    json            import  loads
import  polars          as      pl
from    sys             import  argv


WASDE_PATH = loads(open("./config.json", "r").read())["wasde_path"]


def report(
    symbol: str,
    start:  str,
    end:    str
):

    df = pl.read_parquet(WASDE_PATH)
    df = df.filter(
        (pl.col("Region") == "United States")   &
        (pl.col("ReleaseDate") >=   start)      &
        (pl.col("ReleaseDate") <    end)
    ).select(
        [
            "WasdeNumber",
            "ReportDate",
            "ReportTitle",
            "ReleaseDate",
            "Commodity",
            "MarketYear",
            "ForecastYear",
            "ForecastMonth",
            "Attribute",
            "Unit",
            "Value"
        ]
    )

    rows = df.rows()

    pass


if __name__ == "__main__":

    symbol  = argv[1]
    start   = argv[2]
    end     = argv[3]

    report(symbol, start, end)