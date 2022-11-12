def test(str):
    print(str)


# stock =stock ticker
# date = max, 1y..etc
# Return dataframe with daily return
def get_data(stock, date):
    import pandas as pd
    import yfinance as yf  # Import yahoo finance module
    spy = yf.Ticker(stock)
    spy_hist = spy.history(period=date)
    # print(spy_hist.tail())
    # print(spy_hist.head())
    df = pd.DataFrame(spy_hist)
    df['mydate'] = df.index
    df['mydate'] = df['mydate'].dt.date
    df = df[['mydate', 'Close']]
    # df.loc['2016-11-01'].head()
    df = df.rename(columns={'Close': stock})
    df.sort_values(by=['mydate'], inplace=True, ascending=True)
    df[stock + '_daily_return'] = (df[stock].pct_change(1)) * 100
    df.sort_values(by=['mydate'], inplace=True, ascending=False)
    return df


# stock = array of stock tickers
# date = max, 1y..etc
# Return dataframe with daily return for all stock tickers
def get_data_for_stocks(stocks, date):
    import pandas as pd
    results = []
    merge = False
    for stock in stocks:
        print('working on ' + stock)
        current = get_data(stock, date)

        if merge:
            results = pd.merge(results, current[["mydate", stock, stock + '_daily_return']], on="mydate", how='left')
        else:
            merge = True
            results = current

    return results

# Not generic
def get_custom(others, date):
    import pandas as pd
    dg = pd.read_excel('DGS3MO.xls')
    dg = dg.dropna(axis='rows')
    dg['DG_daily_return'] = dg['DG'] / 252
    others.to_excel("delMe.xlsx", index=False)
    others = pd.read_excel('delMe.xlsx')
    results = pd.merge(dg, others[others.columns.tolist()], on="mydate", how='left')
    return results


# Input = Map of stock and Beta
# Returns expected return 
# expected return = risk_free_return + beta*(market_return - risk_free_return)
def capm_modelMap(mapOfStockBeta, market,riskFreeRate):
    risk_free_return = riskFreeRate
    market_return = mapOfStockBeta[market].annual_return
    exp_return = {}
    for stock in mapOfStockBeta:
        if stock != market:
            beta  = mapOfStockBeta[stock].beta
            expected_return = risk_free_return + beta*(market_return - risk_free_return)
            mapOfStockBeta[stock].exp_return = expected_return
    
    mapOfStockBeta[market].exp_return = mapOfStockBeta[market].annual_return
    return mapOfStockBeta


# stock = array of stock tickers
# date = max, 1y..etc
# Return Map with stock: expected return
# expected return = risk_free_return + beta*(market_return - risk_free_return)
def capm_model(stocks, market,riskFreeRate, date):
    mapOfStockBeta  = compute_beta(stocks, market, date)
    risk_free_return = riskFreeRate
    market_return = mapOfStockBeta[market].annual_return
    exp_return = capm_modelMap(mapOfStockBeta, market, riskFreeRate)
    return exp_return

# stock = array of stock tickers
# date = max, 1y..etc
# return map of stock and beta
def compute_beta(stocks, market, date):
    import pandas as pd
    from stock import Stock
    hist  = get_data_for_stocks(stocks, date)
    hist.to_excel("Beta.xlsx", index = False)
    results = pd.read_excel('Beta.xlsx')
    mapOfStockBeta = {}
    #app_beta = data['SPY_daily_return'].cov(data['AAPL_daily_return'])/data['SPY_daily_return'].var()
    for stock1 in stocks:
        myStock = Stock(stock1)
        app_beta = results[market + '_daily_return'].cov(results[stock1+'_daily_return'])/results[market+'_daily_return'].var()
        myStock.beta = app_beta
        myStock.cov = results[market + '_daily_return'].cov(results[stock1+'_daily_return'])
        myStock.corr = results[market + '_daily_return'].corr(results[stock1+'_daily_return'])
        myStock.annual_return = results[stock1+'_daily_return'].mean()*252
        myStock.std = results[stock1+'_daily_return'].std()
        myStock.var = results[stock1+'_daily_return'].var()
        if stock1 == 'SPY':
            myStock.systematic = myStock.var
            myStock.idiosyncratic  = 0
            myStock.beta = 1
        else:
            myStock.systematic = (myStock.beta*myStock.beta)*results[market+'_daily_return'].var()
            myStock.idiosyncratic  = myStock.var - myStock.systematic
        
        mapOfStockBeta[stock1] = myStock
        print(stock1 + ' ' +  str(app_beta))
    return mapOfStockBeta
           
def get_as_dataframe(stocks):
    import pandas as pd
    p  = pd.DataFrame([vars(stocks[s]) for s in stocks])
    return p