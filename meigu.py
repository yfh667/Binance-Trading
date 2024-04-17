import akshare as ak

stock_us_hist_df = ak.stock_us_hist(symbol='105.MTP', period="daily", start_date="19700101", end_date="22220101", adjust="qfq")
print(stock_us_hist_df)