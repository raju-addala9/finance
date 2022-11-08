def test(str):
    print(str)


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


def get_custom(others, date):
    import pandas as pd
    dg = pd.read_excel('DGS3MO.xls')
    dg = dg.dropna(axis='rows')
    dg['DG_daily_return'] = dg['DG'] / 252
    others.to_excel("delMe.xlsx", index=False)
    others = pd.read_excel('delMe.xlsx')
    results = pd.merge(dg, others[others.columns.tolist()], on="mydate", how='left')
    return results


def capm_modelMap(mapOfStockBeta, market,riskFreeRate):
    risk_free_return = riskFreeRate
    market_return = mapOfStockBeta[market]
    exp_return = {}
    for stock in mapOfStockBeta:
        beta  = mapOfStockBeta[stock]
        expected_return = risk_free_return + beta*(market_return - risk_free_return)
        exp_return[stock] = expected_return
    
    exp_return[market] = mapOfStockBeta[market]
    return exp_return

def capm_model(stocks, market,riskFreeRate, date):
    mapOfStockBeta  = compute_beta(stocks, market, date)
    risk_free_return = riskFreeRate
    market_return = mapOfStockBeta[market]
    exp_return = capm_modelMap(mapOfStockBeta, market, riskFreeRate)
    return exp_return

def compute_beta(stocks, market, date):
    import pandas as pd
    hist  = get_data_for_stocks(stocks, date)
    hist.to_excel("Beta.xlsx", index = False)
    results = pd.read_excel('Beta.xlsx')
    mapOfStockBeta = {}
    #app_beta = data['SPY_daily_return'].cov(data['AAPL_daily_return'])/data['SPY_daily_return'].var()
    for stock in stocks:
        app_beta = results[market + '_daily_return'].cov(results[stock+'_daily_return'])/results[market+'_daily_return'].var()
        mapOfStockBeta[stock] = app_beta
        print(stock + ' ' +  str(app_beta))
    
    mapOfStockBeta[market] = results[market + '_daily_return'].mean()*252 #just put return of market
    return mapOfStockBeta
            