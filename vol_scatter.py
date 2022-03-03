from    json                    import  loads
from    plotly.subplots         import  make_subplots
from    sys                     import  argv
from    util                    import  add_trace, by_season, by_year,  \
                                        clean, get_groups, rs, spreads
from    typing                  import  List


config      = loads(open("./config.json").read())
DB_PATH     = config["db_path"]
START       = config["start"]
END         = config["end"]
USE_SPOT    = False
WIDTH       = 1     # width of calendars
N_COLS      = 2     # columns in output figure


# spread_id like "CLJK" or "ZSUZ"

def report(spread_ids: List):

    n = len(spread_ids)
    
    fig = make_subplots(
        rows            = 1 + n // N_COLS,
        cols            = 1 if n < N_COLS else N_COLS,
        subplot_titles  = [
            spread
            for spread in spread_ids
        ],
        x_title = "size (%)",
        y_title = "change (%)"
    )

    symbol_data = {}

    for i in range(n):

        base_symbol         = spread_ids[i][0:-2]

        if base_symbol not in symbol_data:

            groups                      = clean(get_groups(base_symbol, START, END, USE_SPOT))
            spread_groups               = spreads(groups, WIDTH)
            season_groups               = by_season(spread_groups)
            symbol_data[base_symbol]    = season_groups
    
        spread_id       = spread_ids[i]
        m1              = spread_id[-2:-1]
        m2              = spread_id[-1:]
        id              = (m1, m2)
        season_groups   = symbol_data[base_symbol]
        selected        = season_groups[id]
        selected        = by_year(selected)

        for id, rows in selected.items():

            # 0:    date
            # 1:    % (spread vs spot)
            # 2:    1 day change in %

            pcts = [ 
                row[rs.settle] / row[rs.spot] * 100
                for row in rows
            ]

            pcts_chg = [ 
                pcts[j] - pcts[j - 1] 
                for j in range(1, len(pcts)) 
            ]

            pct_vs_chg = [
                (rows[j][rs.date], pcts[j], pcts_chg[j])
                for j in range(1, len(pcts_chg))
            ]

            add_trace(
                fig     = fig, 
                rows    = pct_vs_chg,
                id      = f"{base_symbol} {id[0]}",
                ax_x    = 1, 
                ax_y    = 2, 
                ax_text = 0, 
                fig_row = 1 + i // N_COLS, 
                fig_col = 1 + i % N_COLS
            )

    fig.show()


if __name__ == "__main__":

    report(argv[1:])