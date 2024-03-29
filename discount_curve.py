from    util                    import  get_groups, r
from    math                    import  log
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    sys                     import  argv
from    time                    import  time
from    typing                  import  List


# usage: python discount_curve.py CL 2018-01-01 2024-01-01


MAX_DATES   = 1000
MAX_MONTHS  = 12


def add_scatter(
    fig:    go.Figure,
    groups: List
):

    # scatterplot

    latest      = groups[-1][0][r.date]
    cur_opacity = 1.0
    step        = 0.8 / len(groups)
    opacities   = {}

    for group in groups:

        date            =   group[0][r.date]
        opacities[date] =   cur_opacity
        cur_opacity     -=  step  

        g = group[:MAX_MONTHS]

        x = [ 
            row[r.dte]
            for row in g[:-1]
        ]

        y = [ 
            (g[i][r.settle] - g[i + 1][r.settle]) / g[i + 1][r.spot]
            for i in range(len(g) - 1)
        ]

        text = [ 
            f"{g[i][r.month]}{g[i][r.id][-2:]}\n"
            f"{g[i + 1][r.month]}{g[i + 1][r.id][-2:]}\n"
            f"{g[i][r.date]}" 
            for i in range(len(g) - 1)
        ]

        color = [ 
            "#FF0000" if row[r.date] == latest else "#0000FF" 
            for row in g
        ]

        opacity = [ 
            opacities[row[r.date]] 
            for row in g 
        ]

        fig.add_trace(
            go.Scatter(
                {
                    "x": x,
                    "y": y,
                    "text": text,
                    "name": date,
                    "mode": "markers",
                    "marker": {
                        "color": color,
                        "opacity": opacity
                    }
                }
            ),
            row = 1,
            col = 1
        )
    

def add_line(
    fig:        go.Figure, 
    groups:     List
):

    # calculate average discount
    
    x = []
    y = []

    for group in groups:

        avg = 0

        for row in group[:MAX_MONTHS]:

            avg += row[r.discount_rate]

        avg /= min(MAX_MONTHS, len(group))

        x.append(group[0][r.date])
        y.append(avg)

    # add trace

    fig.add_trace(
        go.Scatter(
            {
                "x":    x,
                "y":    y,
                "name": "average discount",
                "mode": "lines"
            }
        ),
        row = 2,
        col = 1
    )


if __name__ == "__main__":

    start_ts = time()

    # input

    symbol  = argv[1]
    start   = None if len(argv) < 3 else argv[2]
    end     = None if len(argv) < 4 else argv[3]

    # get, sort, and and clean data

    groups  = get_groups(symbol, start, end)

    # add plots and show

    fig = make_subplots(
        rows        = 2, 
        cols        = 1,
        row_heights = [ 0.7, 0.3 ] 
    )
    
    add_scatter(fig, groups)
    add_line(fig, groups)

    fig.show()

    # finished

    print(f"start date:\t{start}")
    print(f"end date:\t{end}")
    print(f"finished:\t{time() - start_ts: 0.1f}")
