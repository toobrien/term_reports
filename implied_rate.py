import  polars      as      pl
from    sys         import  argv, path
from    time        import  time

path.append("..")

from    data.cat_df import  cat_df


# python CME_HOX2023 12 2023-08-01 2024-01-01


pl.Config.set_tbl_rows(50)
pl.Config.set_tbl_cols(25)


if __name__ == "__main__":

    t0      = time()
    symbol  = argv[1]
    months  = int(argv[2])
    start   = argv[3]
    end     = argv[4]

    df = cat_df(
        "futs", 
        symbol, 
        start, 
        end
    ).sort(
        [ "date", "year", "month" ]
    ).select(
        [
            "contract_id",
            "date",
            "settle",
            "dte"
        ]
    )

    contracts = df.filter(df["date"] == df["date"][-1])["contract_id"][0:months]

    df = df.filter(df["contract_id"].is_in(contracts))
    df = df.pivot(index = "date", columns = "contract_id", values = "settle")

    print(df)

    print(f"elapsed: {time() - t0:0.2f}")

    pass