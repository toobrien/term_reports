from    json                    import  loads
from    plotly.subplots         import  make_subplots
from    util                    import  add_trace, avg_r, by_season, by_year, clean,        \
                                        cor_r, get_groups, rs, spot_correlation, spreads
from    sys                     import argv

config      = loads(open("./config.json").read())
DB_PATH     = config["db_path"]
START       = config["start"]
END         = config["end"]
USE_SPOT    = False
MA_LEN      = 20


# argv[1] like "HONQ" or "CLMN"
# argv[2] == "abs" or "pct"

SYMBOL = argv[1][:-2]
MODE   = argv[2]
MONTHS = (argv[1][-2:-1], argv[1][-1:])
WIDTH  = 1

def report():

    settle_ax           = rs.settle if MODE == "abs" else rs.settle_pct
    groups              = clean(get_groups(SYMBOL, START, END, USE_SPOT))
    spread_groups       = spreads(groups, WIDTH)
    season_groups       = by_season(spread_groups)

    selected = season_groups[MONTHS]
    selected = by_year(selected)

    fig = make_subplots(
        rows        = 3, 
        cols        = 1,
        subplot_titles = [
            f"settle {MODE}",
            "spot",
            "correlation"
        ],
        vertical_spacing = 0.05
    )

    fig.update_layout(height = 1500)

    # spreads (settlement values)
    # underlying
    # correlation

    for _, rows in selected.items(): 
        
        spread_id       = rows[0][rs.id]
        spread_id       = f"{spread_id[0]}/{spread_id[1]}"
        spread_id_mode  = f"{spread_id} {MODE}"
        spot_id         = spread_id + " spot"
        correlation_id  = spread_id + " cor."

        crs = spot_correlation(rows, MA_LEN)

        add_trace(
            fig     = fig, 
            rows    = rows, 
            id      = spread_id_mode,
            ax_x    = rs.dte, 
            ax_y    = settle_ax, 
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

    fig.show()


if __name__ == "__main__":

    report()
