from    bisect      import bisect_left
from    enum        import IntEnum
from    json        import loads
from    math        import log
from    statistics  import median_low
from    sys         import argv
from    time        import time
from    typing      import List
from    util        import clean, get_groups, r, rs, spreads


config  = loads(open("./config.json").read())

DB_PATH     = config["db_path"]
START       = config["start"]
END         = config["end"]
USE_SPOT    = False
MAX_MONTHS  = 48

class sr(IntEnum):

    id          = 0
    pct_spot    = 1
    impl_rate   = 2
    points      = 3
    rank_all    = 4
    rank_season = 5


def report(groups: List):

    groups          = [ 
        group[:MAX_MONTHS]
        for group in groups
    ]
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
    
    discounts = []

    for group in groups:

        avg_discount = 0

        for row in group:

            avg_discount += row[r.settle] / row[r.spot] - 1

        avg_discount /= len(group)
        discounts.append(avg_discount)

    latest_discount = discounts[-1]
    discounts       = sorted(discounts)
    discount_rank   = bisect_left(discounts, latest_discount) / len(discounts)

    print(
        "date".rjust(12),
        "symbol".rjust(12),
        "spot".rjust(12),
        "avg. disc.".rjust(12),
        "disc. rank".rjust(12)
    )

    print(
        f"{latest[0][r.date]}".rjust(12),
        f"{latest[0][r.name]}".rjust(12),
        f"{latest[0][r.spot]: 0.3f}".rjust(12),
        f"{latest_discount: 0.3f}".rjust(12),
        f"{discount_rank: 0.3f}".rjust(12),
        "\n"
    )

    # spread report

    print(
        "id".rjust(12), 
        "% spot".rjust(14),
        "impl. rate".rjust(14),
        "size ".rjust(14),
        "rank (all)".rjust(14),
        "rank (season)".rjust(14)
    )


    summary_rows = {
        sr.id:          [],
        sr.pct_spot:    [],
        sr.impl_rate:   [],
        sr.points:      [],
        sr.rank_all:    [],
        sr.rank_season: []
    }

    # make columns

    for spread in latest:

        id          = f"{spread[rs.id][0]}/{spread[rs.id][1]}"
        pct_spot    = spread[rs.settle] / spread[rs.spot]
        impl_rate   = log((spread[rs.spot] - spread[rs.settle]) / spread[rs.spot]) / ((spread[rs.dte_back] - spread[rs.dte]) / 365)        
        points      = spread[rs.settle]
        rank_all    = bisect_left(size_all, pct_spot) / len(size_all)
        size_season = sorted(
            [
                spread_row[rs.settle] / spread_row[rs.spot]
                for spread_row in by_season[spread[rs.month]]
            ]
        )
        rank_season = bisect_left(size_season, pct_spot) / len(size_season)

        summary_rows[sr.id].append(id)
        summary_rows[sr.pct_spot].append(pct_spot)
        summary_rows[sr.impl_rate].append(impl_rate)
        summary_rows[sr.points].append(points)
        summary_rows[sr.rank_all].append(rank_all)
        summary_rows[sr.rank_season].append(rank_season)

    # calculate prefixes and print

    def get_pref(arr: List, x: float):

        if      x == min(arr):         return "-"
        elif    x == median_low(arr):  return "."
        elif    x == max(arr):         return "+"
        else:                          return " "

    for i in range(len(summary_rows[sr.id])):

        id          = summary_rows[sr.id][i]
        pct_spot    = summary_rows[sr.pct_spot][i]
        impl_rate   = summary_rows[sr.impl_rate][i]
        points      = summary_rows[sr.points][i]
        rank_all    = summary_rows[sr.rank_all][i]
        rank_season = summary_rows[sr.rank_season][i]

        pct_spot_pref       = get_pref(summary_rows[sr.id], id)
        impl_rate_pref      = get_pref(summary_rows[sr.impl_rate], impl_rate)
        points_pref         = get_pref(summary_rows[sr.points], points)
        rank_all_pref       = get_pref(summary_rows[sr.rank_all], rank_all)
        rank_season_pref    = get_pref(summary_rows[sr.rank_season], rank_season)

        print(
            f"{id: >12}",
            f"{pct_spot: >12.3f} {pct_spot_pref}",
            f"{impl_rate: >12.3f} {impl_rate_pref}",
            f"{points: >12.3f} {points_pref}"
            f"{rank_all: >12.3f} {rank_all_pref}",
            f"{rank_season: >12.3f} {rank_season_pref}",
        )


if __name__ == "__main__":

    start_ts = time()

    symbols = None

    if argv[1] != "all":
    
        symbols = " ".join(argv[1:]).split()
    
    else:

        symbols = config["enabled"]

    for symbol in symbols:
        
        groups = clean(get_groups(symbol, START, END, USE_SPOT))

        report(groups)

        print("\n")