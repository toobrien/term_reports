from    enum                    import  IntEnum
from    json                    import  loads
from    plotly.subplots         import  make_subplots
import  plotly.graph_objects    as      go
import  polars                  as      pl
from    sys                     import  argv


# usage: python wasde.py ZR 2022/23 2018-01-1 2024-01-01


WASDE_PATH  = loads(open("./config.json", "r").read())["wasde_path"]
SYM_MAP     = {
    #"HE":   "Pork",
    #"GF":   "Beef",
    #"LE":   "Beef",
    #"SB":   "Sugar",
    #"CT":   "Cotton",
    #"CB":   "Butter",
    #"CSC":  "Cheese",
    #"DC":   "Milk, Class III",
    #"DY":   "Dry Whey",
    #"GNF":  "Nonfat Dry Milk",
    "ZO":   "Oats",
    "ZR":   "Rice, Rough",
    "ZM":   "Meal, Soybean",
    "ZL":   "Oil, Soybean",
    "ZS":   "Oilseed, Soybean",
    "ZW":   "Soft Red Winter",
    "KE":   "Hard Red Winter",
    "ZC":   "Corn"
}
CALENDAR    = {
    0:  "F",
    1:  "G",
    2:  "H",
    3:  "J",
    4:  "K",
    5:  "M",
    6:  "N",
    7:  "Q",
    8:  "U",
    9:  "V",
    10: "X",
    11: "Z"
}


class w_rec(IntEnum):

    release_date    = 0
    market_year     = 1
    forecast_year   = 2
    forecast_month  = 3
    attribute       = 4
    unit            = 5
    value           = 6



def report(
    symbol:     str,
    crop_year:  str,
    start:      str,
    end:        str
):

    df = pl.read_parquet(WASDE_PATH)
    df = df.filter(
        (pl.col("Commodity") == SYM_MAP[symbol])    &
        (pl.col("Region") == "United States")       &
        (pl.col("ReleaseDate") >=   start)          &
        (pl.col("ReleaseDate") <    end)
    ).select(
        [
            "ReleaseDate",
            "MarketYear",
            "ForecastYear",     # int
            "ForecastMonth",    # int
            "Attribute",
            "Unit",
            "Value"
        ]
    )

    rows = df.rows()

    series = {
        "Avg. Farm Price":  [ { "max": float("-inf"), "min": float("inf"), crop_year: None } ] * 12,
        "Area Harvested":   [ { "max": float("-inf"), "min": float("inf"), crop_year: None } ] * 12,
        "Area Planted":     [ { "max": float("-inf"), "min": float("inf"), crop_year: None } ] * 12,
        "Supply, Total":    [ { "max": float("-inf"), "min": float("inf"), crop_year: None } ] * 12,
        "Use, Total":       [ { "max": float("-inf"), "min": float("inf"), crop_year: None } ] * 12,
        "Ending Stocks":    [ { "max": float("-inf"), "min": float("inf"), crop_year: None } ] * 12
    }

    valid_attributes = list(series.keys())

    for row in rows:

        idx     = row[w_rec.forecast_month] - 1
        attrib  = row[w_rec.attribute]
        val     = row[w_rec.value]
        m_year  = row[w_rec.market_year]
        
        if attrib in valid_attributes:

            series_ = series[attrib]

            series_[idx]["max"]     = max(val, series_[idx]["max"])
            series_[idx]["min"]     = min(val, series_[idx]["min"])
            series_[idx][crop_year] = val if m_year == crop_year else series_[idx][crop_year]

    fig = make_subplots(rows = 6, cols = 1)

    i = 1
    x = list(CALENDAR.values())

    for attrib, months in series.items():

        for trace_def in [ 
            ( "max",        "#FF0000" ),
            ( "min",        "#0000FF" ),
            ( crop_year,    "#ca2c92" ) 
        ]:

            measure = trace_def[0]
            color   = trace_def[1]

            fig.add_trace(
                go.Scatter(
                    {
                        "x":        x,
                        "y":        [ month[measure] for month in months ],
                        "marker":   { "color": color },
                        "name":     f"{attrib} {measure}"
                    }
                ),
                row = i,
                col = 1
            )
        
        i += 1

    fig.show()


if __name__ == "__main__":

    symbol      = argv[1]
    crop_year   = argv[2]
    start       = argv[3]
    end         = argv[4]

    report(symbol, crop_year, start, end)