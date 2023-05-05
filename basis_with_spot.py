import  plotly.graph_objects    as      go
from    sys                     import  argv
from    util                    import  get_days_ago, get_groups, get_spot, r


# usage: python basis.py VX 0 252 dte abs


def report(
    symbol:     str,
    term:       int,
    max_days:   int,
    x_mode:     str,
    y_mode:     str
):
    
    series  = {}
    start   = get_days_ago(max_days)
    groups  = get_groups(symbol, start)
    spot    = get_spot(symbol)

    # align dates

    fut_dates   = { group[0][r.date] for group in groups }
    spot_dates  = { row[0] for row in spot }
    dates       = sorted(list(fut_dates.intersection(spot_dates)))

    fut_rows    = [ group[term] for group in groups if group[term][r.date] in dates ]
    spot_rows   = [ row for row in spot if row[0] in dates ]

    for i in range(len(fut_rows)):

        fut_row     = fut_rows[i]
        spot_row    = spot_rows[i]
        date        = fut_row[r.date]
        year        = fut_row[r.year]
        month       = fut_row[r.month]
        settle      = fut_row[r.settle]
        dte         = fut_row[r.dte]
        spot        = spot_row[1]
        basis       = spot - settle
        basis_pct   = (basis / spot) * 100
        id          = ( symbol, month, year )

        if id not in series:

            series[id] = []

        if y_mode == "abs":
        
            y       = basis
            y_txt   = f"{basis:0.4f}"
            
        
        elif y_mode == "pct":

            y       = basis_pct
            y_txt   = f"{basis_pct:0.1f}%"

        
        if x_mode == "date":

            x       = date
            x_txt   = f"date: {date}"

        elif x_mode == "dte":

            x       = dte
            x_txt   = f"dte: {dte}"


        fut_text = f"{x_txt}<br>settle: {settle:0.4f}<br>spot: {spot}<br>basis: {y_txt}"

        series[id].append(( x, y, fut_text ))

    # plot results

    fig = go.Figure()

    for id, ts in series.items():

        x       = [ rec[0] for rec in ts ]
        y       = [ rec[1] for rec in ts ]
        text    = [ rec[2] for rec in ts ]

        fig.add_trace(
            go.Scatter(
                {
                    "x":    x,
                    "y":    y,
                    "text": text,
                    "name": f"{id[0]} {id[1]} {id[2]}"
                }
            )
        )

    fig.show()
        


if __name__ == "__main__":

    symbol      = argv[1]
    term        = int(argv[2])
    max_days    = int(argv[3])
    x_mode      = argv[4]
    y_mode      = argv[5]

    report(symbol, term, max_days, x_mode, y_mode)