from    enum                    import  IntEnum
import  plotly.graph_objects    as      go
from    sys                     import  argv
from    util                    import  get_contracts_by_month, r


# usage: python basis_single_hist.py HO M 2023 10


class ts_rec(IntEnum):

    date        = 0
    dte         = 1
    settle      = 2
    spot        = 3
    basis       = 4
    basis_norm  = 5
    text        = 6


def report(
    symbol:     str,
    month:      str,
    base_year:  int,
    n_years:    int
):

    contracts = get_contracts_by_month(symbol, month)

    years       = list(contracts.keys())
    base_idx    = years.index(base_year) + 1
    years       = years[base_idx - n_years:base_idx]

    contracts = {
        year : contracts[year]
        for year in years
    }

    by_dte = {}

    for _, rows in contracts.items():

        for row in rows:

            dte         = row[r.dte]
            basis_pct   = (row[r.settle] / row[r.spot] - 1) * 100

            if dte not in by_dte:

                by_dte[dte] = { 
                    "max":  float("-inf"),
                    "min":  float("inf"),
                    "base": None
                }

            max_pct = by_dte[dte]["max"]
            min_pct = by_dte[dte]["min"]

            by_dte[dte]["max"] = basis_pct if basis_pct > max_pct else max_pct
            by_dte[dte]["min"] = basis_pct if basis_pct < min_pct else min_pct

            if row[r.year] == base_year:

                by_dte[dte]["base"] = basis_pct

    x_min_max   = sorted(list(by_dte.keys()))
    y_max       = [ by_dte[dte]["max"] for dte in x_min_max ]
    y_min       = [ by_dte[dte]["min"] for dte in x_min_max ]
    x_base      = [ x for x in x_min_max if by_dte[x]["base"] ]
    y_base      = [ by_dte[dte]["base"] for dte in x_base ]

    fig = go.Figure()

    traces = [
        {
            "x":    x_min_max,
            "y":    y_max,
            "line": { "width": 0 },
            "name": "max"
        },
        {
            "x":        x_min_max,
            "y":        y_min,
            "line": { 
                "width": 0,
                "color": "#0000FF"
            },
            "fill": "tonexty",
            "name": "min"
        },
        {
            "x":        x_base,
            "y":        y_base,
            "mode":     "markers",
            "marker":   { "color": "#FF0000" },
            "name":     f"{symbol} {month} {base_year}"
        }
    ]
    
    for trace in traces:

        fig.add_trace(go.Scatter(**trace))

    fig.show()


if __name__ == "__main__":

    symbol      = argv[1]
    month       = argv[2]
    base_year   = int(argv[3])
    n_years     = int(argv[4])

    report(symbol, month, base_year, n_years)