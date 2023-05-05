from    enum                    import  IntEnum
import  plotly.graph_objects    as      go
from    sys                     import  argv
from    util                    import  get_groups, r


# usage:    
#           python basis.py CL 12 180 dte abs
#           python basis.py HO 12 252 date pct


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
    num_contracts:  int,
    max_dte:        int,
    x_mode:         str,
    y_mode:         str,
):

    series = {}

    groups = get_groups(symbol)

    for group in groups:

        for row in group:

            date    = row[r.date]
            year    = row[r.year]
            month   = row[r.month]
            settle  = row[r.settle]
            dte     = row[r.dte]
            spot    = row[r.spot]

            if dte >= max_dte:

                continue

            id = ( symbol, month, year )

            if id not in series:

                series[id] = []

            basis       = spot - settle
            basis_norm  = basis / spot * 100
            text        = f"date: {date}<br>dte: {dte}<br>spot: {spot}<br>basis: {basis: 0.4f}"

            if y_mode == "pct":

                text = f"date: {date}<br>dte: {dte}<br>{spot}<br>basis: {basis_norm: 0.1f}%"

            rec = ( 
                    date,
                    dte,
                    settle,
                    spot,
                    basis,
                    basis_norm,
                    text
                )
            
            series[id].append(rec)

    # plot results

    fig = go.Figure()

    selected = list(series.items())[-num_contracts:]

    for id, ts in selected:

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
                    "name": f"{id[0]} {id[1]} {id[2]}"
                }
            )
        )

    fig.show()


if __name__ == "__main__":

    symbol          = argv[1]
    num_contracts   = int(argv[2])
    max_dte         = int(argv[3])
    x_mode          = argv[4]       # "date" for x axis == date, any other value for x axis == dte
    y_mode          = argv[5]       # "abs" for points, or "pct" for %

    report(symbol, num_contracts, max_dte, x_mode, y_mode)