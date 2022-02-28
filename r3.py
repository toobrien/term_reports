from    json                    import  loads
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    typing                  import  List
from    util                    import  avg_r, by_season, by_year, clean, cor_r, get_groups, \
                                        rs, spot_correlation, spreads, term_avg_by_year


config      = loads(open("./config.json").read())
DB_PATH     = config["db_path"]
START       = config["start"]
END         = config["end"]
USE_SPOT    = False
MA_LEN      = 20


def add_trace(
    fig:        go.Figure,
    rows:       List,
    id:         str,
    ax_x:       int,
    ax_y:       int,
    ax_text:    int,
    fig_row:    int,
    fig_col:    int
):

    x       = [ r[ax_x] for r in rows ]
    y       = [ r[ax_y] for r in rows ]
    text    = [ r[ax_text] for r in rows ]

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
        row = fig_row,
        col = fig_col
    )


def report():

    groups          = clean(get_groups("HO", START, END, USE_SPOT))
    spread_groups   = spreads(groups, 1)
    avgs            = term_avg_by_year(spread_groups, 0, 9)
    season_groups   = by_season(spread_groups)

    nq = season_groups[("N", "Q")]
    nq = by_year(nq)

    fig = make_subplots(
        rows        = 4, 
        cols        = 1,
        subplot_titles = [
            "settle",
            "spot",
            "correlation",
            "avg settle"
        ],
        vertical_spacing = 0.05
    )

    fig.update_layout(height = 1600)

    # spreads (settlement values)
    # underlying
    # correlation

    for _, rows in nq.items(): 
        
        spread_id       = rows[0][rs.id]
        spread_id       = f"{spread_id[0]}/{spread_id[1]}"
        spot_id         = spread_id + " S"
        correlation_id  = spread_id + " C"

        crs = spot_correlation(rows, MA_LEN)

        add_trace(
            fig     = fig, 
            rows    = rows, 
            id      = spread_id, 
            ax_x    = rs.dte, 
            ax_y    = rs.settle, 
            ax_text = rs.date, 
            fig_row = 1, 
            fig_col = 1
        )
        
        add_trace(
            fig     = fig, 
            rows    = rows, 
            id      = spot_id, 
            ax_x    = rs.dte, 
            ax_y    = rs.spot, 
            ax_text = rs.date, 
            fig_row = 2, 
            fig_col = 1
        )
        
        add_trace(
            fig     = fig, 
            rows    = crs, 
            id      = correlation_id, 
            ax_x    = cor_r.dte, 
            ax_y    = cor_r.correlation, 
            ax_text = cor_r.date,
            fig_row = 3, 
            fig_col = 1
        )

    # avg spread by year

    for year, rows in avgs.items():

        add_trace(
            fig     = fig, 
            rows    = rows, 
            id      = str(year), 
            ax_x    = avg_r.day_of_year, 
            ax_y    = avg_r.avg_settle, 
            ax_text = avg_r.date, 
            fig_row = 4, 
            fig_col = 1
        )

    fig.show()


if __name__ == "__main__":

    report()
