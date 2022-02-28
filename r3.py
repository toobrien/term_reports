from    json                    import  loads
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    statistics              import  correlation, StatisticsError
from    typing                  import  List
from    util                    import  by_season, by_year, clean, get_groups, rs, spreads


config      = loads(open("./config.json").read())
DB_PATH     = config["db_path"]
START       = config["start"]
END         = config["end"]
USE_SPOT    = False
MA_LEN      = 20


def add_trace(
    fig:    go.Figure,
    rows:   List,
    id:     str,
    ax_x:   int,
    ax_y:   int,
    row:    int,
    col:    int
):

    x       = [ r[ax_x] for r in rows ]
    y       = [ r[ax_y] for r in rows ]
    text    = [ r[rs.date] for r in rows ]

    fig.add_trace(
        go.Scattergl(
            {
                "x": x,
                "y": y,
                "text": text,
                "name": id,
                "mode": "markers"
            }
        ),
        row = row,
        col = col
    )


def spot_correlation(rows: List, length: int):

    diff_spot   = [ None ]
    diff_settle = [ None ]

    for i in range(1, len(rows)):

        x = rows[i][rs.spot] - rows[i - 1][rs.spot]
        y = rows[i][rs.settle] - rows[i - 1][rs.settle]

        diff_spot.append(x)
        diff_settle.append(y)

    res = [ 
        [ row[rs.dte], None ]
        for row in rows 
    ]

    for i in range(length + 1, len(rows)):

        try:

            res[i][1] = correlation(
                diff_spot[i - length:i],
                diff_settle[i - length:i]
            )

        except StatisticsError:

            res[i][1] = None

    return res


def report():

    groups          = clean(get_groups("HO", START, END, USE_SPOT))
    spread_groups   = spreads(groups, 1)
    season_groups   = by_season(spread_groups)

    nq = season_groups[("N", "Q")]
    nq = by_year(nq)

    fig = make_subplots(
        rows        = 3, 
        cols        = 1,
        row_heights = [ 0.34, 0.33, 0.33 ]
    )

    for _, rows in nq.items():
    
        # by dte 
        
        spread_id       = rows[0][rs.id]
        spread_id       = f"{spread_id[0]}/{spread_id[1]}"
        spot_id         = spread_id + " S"
        correlation_id  = spread_id + " C"

        crs = spot_correlation(rows, MA_LEN)

        add_trace(fig, rows, spread_id, rs.dte, rs.settle, 1, 1)
        add_trace(fig, rows, spot_id, rs.dte, rs.spot, 2, 1)
        add_trace(fig, crs, correlation_id, 0, 1, 3, 1)

        # by date

        # add_spread(fig, rows, rs.date, rs.settle, 1, 1)

    

    fig.show()


if __name__ == "__main__":

    report()
