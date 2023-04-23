from    cot.cot_v2_api          import API_ROOT, get_contract, get_index, format, report
from    json                    import dumps
import  plotly.graph_objects    as go
from    polars                  import from_dict
from    cot.raw_recs            import futs_only_raw
from    cot.recs                import disagg_futs_only, futs_only
from    requests                import get
from    sys                     import argv
from    time                    import time


def s0():

    # set "format" to false to keep original headers
    
    # note: in this example, an exchange symbol is used instead of a contract code.
    #       you can add more symbols -> code mappings to the common_symbols file.
    #       use the report's index (see sample 3) to discover the mapping.
           
    # example: put into a polars dataframe

    con = get_contract(report.futs_only, "NQ", format.none)
    df  = from_dict(con)

    print(df)


def s1():

    # set "format" to true for use with cot_v2_api record types
    # example: print eurodollar open interest by date

    eurodollars = "132741" # find using the index
    con         = get_contract(report.futs_only, eurodollars, format.full)

    recs = zip(
                con[futs_only_raw.as_of_date_in_form_yyyy_mm_dd],
                con[futs_only_raw.open_interest_all]
            )

    for rec in recs:

        print(rec[0], rec[1])


def s2():

    # bypass this library and get the raw data (column headers are in-tact)

    report_name     = "futs_only"
    contract_code   = "076691" # platinum; find using the index

    res = get(f"{API_ROOT}/{report_name}/{contract_code}").json()

    print(dumps(res, indent = 4))


def s3():

    # print the "futures only" index

    idx = get_index(report.futs_only)

    print(dumps(idx, indent = 4))


def s4():

    # use the convenience record to print the first 6 months of commercial net position as percentage of total open interest
    # for reports between 2018-01-01 and 2024-01-01

    con = get_contract(
                        report.futs_only, 
                        "ZC", 
                        format.convenience,
                        "2018-01-01",
                        "2024-01-01"
                    )

    dates           = con[futs_only.date]
    comm_net_pct    = con[futs_only.comm_net_pct]
    
    for i in range(24):

        print(dates[i], f"{comm_net_pct[i]:0.1f}")


def s5():

    # plot net positions (as % of total open interest) for the various participants 
    # of the disaggregated futures and options report between 2018-01-01 and 2024-01-01.

    con = get_contract(
                        report.disagg_futs_and_opts,
                        "ZW",
                        format.convenience,
                        "2018-01-01",
                        "2024-01-01"
                    )

    # Note that "opts" records are the same as "futs_only" in both the disaggregated and financial reports.
    # Just use the "futs_only" convenience records to index either report.
    
    fig = go.Figure()
    x   = con[disagg_futs_only.date]
    ys  = [
        ( "producer/merchat/processor/user",    con[disagg_futs_only.prod_merc_net_pct] ),
        ( "managed money",                      con[disagg_futs_only.managed_net_pct] ),
        ( "swap dealers",                       con[disagg_futs_only.swap_net_pct] ),
        ( "other reportable",                   con[disagg_futs_only.other_net_pct] ),
        ( "non reportable",                     con[disagg_futs_only.nonrep_net_pct] )
    ]

    for pair in ys:

        fig.add_trace(
            go.Scatter( 
                {
                    "x": x,
                    "y": pair[1],
                    "name": pair[0]
                }
            )
        )

    fig.show()


if __name__ == "__main__":

    to_run = int(argv[1])

    samples = [
        s0,
        s1,
        s2,
        s3,
        s4,
        s5
    ]
    
    start = time()

    samples[to_run]()

    print(f"elapsed: {time() - start:0.1f}s")