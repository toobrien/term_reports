from    bisect  import bisect_left
from    json    import loads
from    sys     import argv
from    time    import time
from    typing  import List
from    util    import clean, get_groups, r, spreads

config  = loads(open("./config.json").read())

DB_PATH     = config["db_path"]
START       = config["start"]
END         = config["end"]
MAX_MONTHS  = 12


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
        "date".ljust(12),
        "symbol".ljust(12),
        "spot".ljust(12),
        "avg. discount".ljust(12),
        "discount rank".ljust(12)
    )

    print(
        f"{latest[0][r.date]}".ljust(12),
        f"{latest[0][r.name]}".ljust(12),
        f"{latest[0][r.spot]: 0.3f}".ljust(12),
        f"{latest_discount: 0.3f}".ljust(12),
        f"{discount_rank: 0.3f}".ljust(12),
        "\n"
    )

    # spread report

    print(
        "id".ljust(12), 
        "size pct.".ljust(12),
        "size pt.".ljust(12),
        "rank (all)".ljust(12), 
        "rank (season)".ljust(12)
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
            f"{id: <12}",
            f"{size_pct: <12.3f}",
            f"{size_pt: <12.3f}"
            f"{rank_all: <12.3f}",
            f"{rank_season: <12.3f}",
        )


if __name__ == "__main__":

    start_ts = time()

    symbols = None

    if argv[1] != "all":
    
        symbols = " ".join(argv[1:]).split()
    
    else:

        symbols = config["enabled"]

    for symbol in symbols:
        
        groups = clean(get_groups(symbol, START, END))

        report(groups)

        print("\n")

    print(f"finished:\t{time() - start_ts: 0.1f}")