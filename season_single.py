from    json                    import  loads
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    sys                     import  argv
from    util                    import  get_groups, r

config      = loads(open("./config.json").read())
START       = config["start"]
END         = config["end"]

# symbol like "HO" or "CL"

def report(symbol: str):

    year_ranges         = {}
    month_settlements   = {
        "F": [],
        "G": [],
        "H": [],
        "J": [],
        "K": [],
        "M": [],
        "N": [],
        "Q": [],
        "U": [],
        "V": [],
        "X": [],
        "Z": []
    }
    month_changes       = {
        "F": {},
        "G": {},
        "H": {},
        "J": {},
        "K": {},
        "M": {},
        "N": {},
        "Q": {},
        "U": {},
        "V": {},
        "X": {},
        "Z": {}
    } 

    LO_IDX      = 0
    HI_IDX      = 1
    DTE_IDX     = 0
    YEAR_IDX    = 0
    SETTLE_IDX  = 1

    groups = get_groups(symbol, START, END, False)

    for group in groups:

        for row in group:

            year    = row[r.year]
            month   = row[r.month]
            settle  = row[r.settle]
            dte     = row[r.dte]

            # set yearly price range

            if year not in year_ranges:

                year_ranges[year] = [ float("inf"), float("-inf") ]

            year_range = year_ranges[year]

            year_range[LO_IDX] = year_range[LO_IDX] if year_range[LO_IDX] < settle else settle
            year_range[HI_IDX] = year_range[HI_IDX] if year_range[HI_IDX] > settle else settle

            # set monthly settlements
            
            month_settlements[month].append((year, settle))

            # group settlements by month, year

            if dte <= 31:

                by_month = month_changes[month]

                if year not in by_month:

                    by_month[year] = []

                by_month_year = by_month[year]

                by_month_year.append((dte, settle))

    # normalize monthly settlements

    for month, settlements in month_settlements.items():

        for i in range(len(settlements)):

            settlement      = settlements[i]
            year            = settlement[YEAR_IDX]
            year_range      = year_ranges[year]
            settlements[i]  = (settlement[SETTLE_IDX] - year_range[LO_IDX]) / (year_range[HI_IDX] - (year_range[LO_IDX]))

    # calculate % change by month, year

    for month, settlements_by_year in month_changes.items():

        changes = []

        for year, settlements in settlements_by_year.items():

            settlements = sorted(settlements, key = lambda e: e[DTE_IDX])

            changes.append(settlements[0][SETTLE_IDX] / settlements[-1][SETTLE_IDX] - 1)

        month_changes[month] = changes

    pass

    # plot results

    fig = make_subplots(
        rows                = 2, 
        cols                = 1,
        subplot_titles      = [
            "price",
            "change",
        ],
        vertical_spacing    = 0.05
    )

    fig.update_layout(height = 1000)
    
    # settlements traces

    for month, settlements in month_settlements.items():

        fig.add_trace(
            go.Box(
                y = settlements,
                x = [ month for i in range(len(settlements)) ],
                name = month,
                boxpoints = False,
                marker_color = "blue"

            ),
            row = 1,
            col = 1
        )

    # monthly changes traces

    for month, changes in month_changes.items():

        fig.add_trace(
            go.Box(
                y = changes,
                x = [ month for i in range(len(settlements)) ],
                name = month,
                boxpoints = False,
                marker_color = "red"

            ),
            row = 2,
            col = 1
        )

    fig.show()


if __name__ == "__main__":

    report(argv[1])
