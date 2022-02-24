from    bisect  import bisect_left
from    json    import loads
from    math    import log
from    sys     import argv
from    time    import time
from    typing  import List
from    util    import clean, get_groups, r, rs, spreads

config  = loads(open("./config.json").read())

DB_PATH     = config["db_path"]
START       = config["start"]
END         = config["end"]
MAX_MONTHS  = 48


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
        "avg. discount".rjust(12),
        "discount rank".rjust(12)
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
        "% spot".rjust(12),
        "impl. rate".rjust(12),
        "size ".rjust(12),
        "rank (all)".rjust(12), 
        "rank (season)".rjust(12)
    )

    for spread in latest:

        id          = f"{spread[rs.id][0]}/{spread[rs.id][1]}"
        pct_spot    = spread[rs.settle] / spread[rs.spot]
        impl_rate   = log((spread[rs.spot] - spread[rs.settle]) / spread[rs.spot]) / ((spread[rs.dte_back] - spread[rs.dte]) / 365)
        point       = spread[rs.settle]
        rank_all    = bisect_left(size_all, pct_spot) / len(size_all)
        size_season = sorted(
            [
                spread_row[rs.settle] / spread_row[rs.spot]
                for spread_row in by_season[spread[rs.month]]
            ]
        )
        rank_season = bisect_left(size_season, pct_spot) / len(size_season)

        print(
            f"{id: >12}",
            f"{pct_spot: >12.3f}",
            f"{impl_rate: >12.3f}",
            f"{point: >12.3f}"
            f"{rank_all: >12.3f}",
            f"{rank_season: >12.3f}",
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