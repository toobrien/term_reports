from    json                    import  loads
from    plotly.subplots         import  make_subplots
import  plotly.graph_objects    as      go
import  polars                  as      pl
from    sys                     import  argv


# usage: python wasde.py ZR 2018-01-1 2024-01-01


WASDE_PATH      = loads(open("./config.json", "r").read())["wasde_path"]
SUBPLOT_HEIGHT  = 300
SYM_MAP         = {
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


def report(
    symbol:     str,
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

    market_years    = df.unique("MarketYear").select("MarketYear").rows()
    attributes      = [ 
        ( "Avg. Farm Price",    1 ),
        ( "Area Harvested",     2 ),
        ( "Area Planted",       3 ),
        ( "Supply, Total",      4 ),
        ( "Use, Total",         5 ),
        ( "Ending Stocks",      6 )
    ]

    fig = make_subplots(
        rows                = 6, 
        cols                = 1,
        shared_xaxes        = True,
        subplot_titles      = tuple( attribute[0] for attribute in attributes ),
        vertical_spacing    = 0.03
    )
    
    fig.update_layout(
        height      = 6 * SUBPLOT_HEIGHT,
        title_text  = symbol
    )

    for market_year in market_years:

        my_series = df.filter(pl.col("MarketYear") == market_year)
        
        for attribute, row in attributes:

            attrib_series = my_series.filter(pl.col("Attribute") == attribute)

            fig.add_trace(
                go.Scatter(
                    {
                        "x":    attrib_series["ReleaseDate"],
                        "y":    attrib_series["Value"],
                        "name": f"{attribute} {market_year[0]}",
                        "text": [ market_year[0] for i in range(len(attrib_series)) ]
                    }
                ),
                row = row,
                col = 1
            )

            pass

    fig.show()


if __name__ == "__main__":

    symbol      = argv[1]
    start       = argv[2]
    end         = argv[3]

    report(symbol, start, end)