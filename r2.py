from    bisect  import bisect_left
from    json    import loads
from    sys     import argv
from    time    import time
from    typing  import List
from    util    import get_rows, group_by_date, r, spreads

config  = loads(open("./config.json").read())

DB_PATH     = config["db_path"]
START       = config["start"]
END         = config["end"]
MAX_MONTHS  = 12
MAX_DTE     = 180


def report(rows: List):

    groups          = group_by_date(rows, MAX_MONTHS)
    spread_groups   = spreads(groups, 1)
    latest          = spread_groups[-1]
    flat            = [ 
        row 
        for group in spread_groups
        for row in group
    ]
    size_all        = sorted([
        row[r.settle] / row[r.spot]
        for row in flat
    ])

    # group by season (m1, m2)

    by_season = {}

    for row in flat:

        months = row[r.month]

        if months not in by_season:

            by_season[months] = []

        by_season[months].append(row)

    # day report
    
    avg_discount = 0

    for row in groups[-1]:

        avg_discount += row[r.settle] / row[r.spot] - 1

    avg_discount /= len(groups[-1])

    print(
        f"{latest[0][r.date]} {latest[0][r.name]}".ljust(15),
        str(latest[0][r.spot]).ljust(15),
        f"{avg_discount: 0.3f}".ljust(15),
        "\n"
    )

    # spread report

    print(
        "id".ljust(15), 
        "size pct.".ljust(15),
        "size pt.".ljust(15),
        "rank (all)".ljust(15), 
        "rank (season)".ljust(15)
    )

    for spread in latest:

        id          = f"{spread[r.id][0]}/{spread[r.id][1]}"
        size_pct    = spread[r.settle] / spread[r.spot]
        size_pt     = spread[r.settle]
        rank_all    = bisect_left(size_all, size_pct) / len(size_all)
        size_season = sorted([
            row[r.settle] / row[r.spot]
            for row in by_season[spread[r.month]]
        ])
        rank_season = bisect_left(size_season, size_pct) / len(size_season)

        print(
            f"{id: <15}",
            f"{size_pct: <15.3f}",
            f"{size_pt: <15.3f}"
            f"{rank_all: <15.3f}",
            f"{rank_season: <15.3f}",
        )


if __name__ == "__main__":

    start_ts = time()

    # input

    symbol  = argv[1]
    start   = START if len(argv) < 3 else argv[2]
    end     = END   if len(argv) < 4 else argv[3]

    rows = get_rows(symbol, start, end)

    # add plots and show

    report(rows)

    # finished

    print(f"\nfinished:\t{time() - start_ts: 0.1f}")