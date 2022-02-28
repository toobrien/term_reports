from    json                    import  loads
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    typing                  import  List
from    util                    import  by_season, by_year, clean, get_groups, rs, spreads


config  = loads(open("./config.json").read())

DB_PATH     = config["db_path"]
START       = config["start"]
END         = config["end"]
USE_SPOT    = False


def add_spread(
    fig:    go.Figure,
    spread: List,
    ax_x:   int,
    ax_y:   int,
    row:    int,
    col:    int
):

    id      = spread[0][rs.id]
    x       = [ r[ax_x] for r in spread ]
    y       = [ r[ax_y] for r in spread ]
    text    = [ r[rs.date] for r in spread ]

    fig.add_trace(
        go.Scatter(
            {
                "x": x,
                "y": y,
                "text": text,
                "name": f"{id[0]}/{id[1]}",
                "mode": "markers"
            }
        ),
        row = row,
        col = col
    )


def report():

    groups          = clean(get_groups("HO", START, END, USE_SPOT))
    spread_groups   = spreads(groups, 1)
    season_groups   = by_season(spread_groups)

    nq = season_groups[("N", "Q")]
    nq = by_year(nq)

    fig = make_subplots(
        rows        = 2, 
        cols        = 1,
        row_heights = [ 0.5, 0.5 ] 
    )

    for year, rows in nq.items():
    
        # by dte 
        
        add_spread(fig, rows, rs.dte, rs.settle, 1, 1)
        add_spread(fig, rows, rs.dte, rs.spot, 2, 1)

        # by date

        # add_spread(fig, rows, rs.date, rs.settle, 1, 1)

    

    fig.show()


if __name__ == "__main__":

    report()
