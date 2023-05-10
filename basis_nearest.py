from    enum                    import  IntEnum
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    sys                     import  argv
from    util                    import  get_groups, r


# usage:    
#           python basis_nearest.py CL 90 180 dte abs
#           python basis_nearest.py HO 0 252 date pct
#           python basis_nearest.py RB 0 55 date pct


class ts_rec(IntEnum):

    date        = 0
    dte         = 1
    settle      = 2
    spot        = 3
    basis       = 4
    basis_norm  = 5
    text        = 6


def report(
    symbol:         str,
    min_dte:        int,
    max_dte:        int,
    x_mode:         str,
    y_mode:         str,
):

    series  = {}
    hist    = []

    groups = get_groups(symbol)

    for group in groups:

        for i in range(len(group)):

            row = group[i]

            date    = row[r.date]
            year    = row[r.year]
            month   = row[r.month]
            settle  = row[r.settle]
            dte     = row[r.dte]
            spot    = row[r.spot]

            if dte < min_dte or dte >= max_dte:

                continue

            id  = ( symbol, month, str(year) )
            key = i

            if key not in series:

                series[key] = []

            basis       = spot - settle
            basis_norm  = (spot / settle - 1) * 100
            text        = f"date: {date}<br>dte: {dte}<br>spot: {spot}<br>basis: {basis: 0.4f}<br>{' '.join(id)}"

            if y_mode == "pct":

                text = f"date: {date}<br>dte: {dte}<br>{spot}<br>basis: {basis_norm: 0.1f}%<br>{' '.join(id)}"

                hist.append(basis_norm)
            
            else:

                hist.append(basis)

            rec = ( 
                    date,
                    dte,
                    settle,
                    spot,
                    basis,
                    basis_norm,
                    text
                )
            
            series[key].append(rec)

    # plot results

    fig = make_subplots(rows = 1, cols = 2)
    
    fig.update_layout(title = symbol)

    for key, ts in series.items():

        x = [ rec[ts_rec.dte]   for rec in ts ]
        y = [ rec[ts_rec.basis] for rec in ts ]

        if x_mode == "date":

            x = [ rec[ts_rec.date] for rec in ts]

        if y_mode == "pct":

            y = [ rec[ts_rec.basis_norm] for rec in ts ]

        fig.add_trace(
            go.Scatter(
                {
                    "x": x,
                    "y": y,
                    "text": [ rec[ts_rec.text] for rec in ts ],
                    "name": f"{symbol} {key}"
                }
            ),
            row = 1,
            col = 1
        )

    fig.add_trace(
        go.Histogram(
            { 
                "x": hist,
                "name": "basis %" if y_mode == "pct" else "basis"
            }
        ),
        row = 1,
        col = 2
    )

    fig.show()


if __name__ == "__main__":

    symbol          = argv[1]
    min_dte         = int(argv[2])
    max_dte         = int(argv[3])
    x_mode          = argv[4]       # "date" for x axis == date, any other value for x axis == dte
    y_mode          = argv[5]       # "abs" for points, or "pct" for %

    report(symbol, min_dte, max_dte, x_mode, y_mode)