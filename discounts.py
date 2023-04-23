from    util                    import  get_groups, r
from    math                    import  e
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    statistics              import  median
from    sys                     import  argv
from    time                    import  time
from    typing                  import  List
from    util                    import  add_trace


# usage: python discounts.py CL 90 2018-01-01 2024-01-01


def theo_fut_curve(groups: List):

    latest      = groups[0]
    max_dte     = latest[-1][r.dte]
    latest_spot = latest[0][r.spot]
    med_disc    = median(
        sorted(
            [
                row[r.discount_rate]
                for row in latest
            ]
        )
    )

    curve = [ 
        (
            i,
            latest_spot * e ** (med_disc * i / 365),
            med_disc
        )
        for i in range(1, max_dte + 1)
    ]

    return curve


def fut_curve(groups: List):

    latest = groups[0]

    curve = [
        (
            row[r.dte],
            row[r.settle],
            row[r.id]
        )
        for row in latest
    ]

    return curve


def todays_discounts(groups: List):

    return [
        (
            row[r.dte], 
            row[r.discount_rate],
            row[r.id]
        )
        for row in groups[0]
    ]


def all_history_disc(groups: List):

    max_dte     = groups[0][-1][r.dte]
    dte_to_disc = {
        i : []
        for i in range(max_dte + 1)
    }

    for group in groups:

        for row in group:

            dte = row[r.dte]

            if dte <= max_dte:

                dte_to_disc[dte].append(row[r.discount_rate])

    traces = [
        go.Box(
            y               = discounts,
            x               = [ dte for i in range(len(discounts)) ],
            name            = dte,
            boxpoints       = False,
            marker_color    = "blue"
        )
        for dte, discounts in dte_to_disc.items()
    ]

    return traces


def recent_discounts(groups: list, days: int):

    latest      = groups[0]
    contracts   = {
        row[r.id] : []
        for row in latest
    }
    dtes        = {
        row[r.id] : row[r.dte]
        for row in latest
    }

    for i in range(days + 1):

        group = groups[i]

        for row in group:

            if row[r.id] in contracts:

                contracts[row[r.id]].append(row[r.discount_rate])

    traces = [
        go.Box(
            y               = discounts,
            x               = [ dtes[contract] for i in range(days + 1) ],
            name            = contract,
            boxpoints       = False,
            marker_color    = "red"
        )
        for contract, discounts in contracts.items()
    ]

    return traces


if __name__ == "__main__":

    start_ts = time()

    # input

    symbol  = argv[1]
    days    = int(argv[2])
    start   = None if len(argv) < 4 else argv[3]
    end     = None if len(argv) < 5 else argv[4]

    # get, sort, and and clean data

    groups = [
        group for group in
        reversed(get_groups(symbol, start, end))
    ]

    # create figure

    fig = make_subplots(
        rows        = 3, 
        cols        = 1,
        row_heights = [ 0.33, 0.33, 0.34 ] 
    )

    # add fut / theo curves to subplot 1

    t0 = fut_curve(groups)
    t1 = theo_fut_curve(groups)

    add_trace(
        fig     = fig,
        rows    = t0,
        id      = "fut_curve",
        ax_x    = 0,
        ax_y    = 1,
        ax_text = 2,
        fig_row = 1,
        fig_col = 1
    )

    add_trace(
        fig     = fig,
        rows    = t1,
        id      = "theo_curve",
        ax_x    = 0,
        ax_y    = 1,
        ax_text = 2,
        fig_row = 1,
        fig_col = 1,
        mode    = "lines"
    )

    # add all-history boxplots and today's discounts to subplot 2

    t3 = todays_discounts(groups)
    
    t4 = all_history_disc(groups)

    add_trace(
        fig     = fig,
        rows    = t3,
        id      = "todays_discounts_mid",
        ax_x    = 0,
        ax_y    = 1,
        ax_text = 2,
        fig_row = 2,
        fig_col = 1
    )

    for trace in t4:

        fig.add_trace(
            trace,
            row = 2,
            col = 1
        )

    # add recent discounts and today's discounts to subplot 3

    t5 = recent_discounts(groups, days)

    add_trace(
        fig      = fig,
        rows     = t3,
        id       = "todays_discounts_bottom",
        ax_x     = 0,
        ax_y     = 1,
        ax_text  = 2,
        fig_row  = 3,
        fig_col  = 1,
        color    = "blue"
    )    

    for trace in t5:

        fig.add_trace(
            trace,
            row = 3,
            col = 1
        )

    # finished

    fig.show()

    print(f"finished:\t{time() - start_ts: 0.1f}")
