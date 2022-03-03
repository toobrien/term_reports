from    json                    import  loads
from    plotly.subplots         import  make_subplots
from    sys                     import  argv
from    util                    import  add_trace, avg_r, clean,    \
                                        get_groups, spreads, term_avg_by_year


config      = loads(open("./config.json").read())
DB_PATH     = config["db_path"]
START       = config["start"]
END         = config["end"]
USE_SPOT    = False
START_MONTH = 0
END_MONTH   = 12


def report(symbol: str, mode: str):

    groups              = clean(get_groups(symbol, START, END, USE_SPOT))
    spread_groups       = spreads(groups, 1)
    avgs_abs            = term_avg_by_year(spread_groups, 0, 12, mode = "abs")
    avgs_pct            = term_avg_by_year(spread_groups, 0, 12, mode = "pct")

    fig = make_subplots(
        rows            = 1,
        cols            = 1,
        x_title = f"day of year",
        y_title = f"avg. spread",
        vertical_spacing = 0.05
    )
    
    fig.update_layout(title = f"settle {mode}")

    # avg spread by year

    yr = []

    if mode == "abs":

        yr = [ (year, rows) for year, rows in avgs_abs.items() ]
    
    else:
        
        yr = [ (year, rows) for year, rows in avgs_pct.items() ]

    for i in range(len(yr)):

        year, rows = yr[i]

        add_trace(
            fig     = fig, 
            rows    = rows, 
            id      = f"{str(year)}", 
            ax_x    = avg_r.day_of_year, 
            ax_y    = avg_r.avg_settle, 
            ax_text = avg_r.date,
            fig_row = 1,
            fig_col = 1
        )

    fig.show()


if __name__ == "__main__":

    report(argv[1], argv[2])