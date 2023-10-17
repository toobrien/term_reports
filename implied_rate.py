import  numpy       as      np
import  pandas      as      pd
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

    contracts   = df.filter(df["date"] == df["date"][-1])["contract_id"]
    contracts   = list(contracts[0:months])
    df          = df.filter(df["contract_id"].is_in(contracts))
    df          = df.to_pandas()

    df_price    = df.pivot_table(index = "date", columns = "contract_id", values = "settle")[contracts]
    df_dte      = df.pivot_table(index = "date", columns = "contract_id", values = "dte")[contracts]
    
    m1_price    = pd.concat([ df_price.iloc[:, 0] ] * (len(contracts) - 1), axis = 1, ignore_index = True)
    dur         = (df_dte.subtract(df_dte.iloc[:, 0], axis = 0).iloc[0].T)[1:] / 365
    df_price    = df_price.iloc[:, 1:]

    x           = df_price.values
    y           = m1_price.values
    t           = dur.values

    df_rate     = np.log(x / y) / t
   
    pass