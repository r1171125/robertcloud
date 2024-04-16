def etf_00733():
    """
    這是一個受保護的函數,包含了您的關鍵代碼
    """
    import finlab
    import numpy as np
    import pandas as pd
    from finlab import data
    import talib
    from finlab import login

    # 登入 FinLab API
    finlab.login("vAaBvcNeAmbi2OLDvq+9SIu96gfJZy8iuFA58yxhWL8QLKNB1jyjWScd+oJ4Y4Bg#vip_m")
    # 獲取調整後的收盤價和基準指數
    adj_close = data.get('etl:adj_close')
    benchmark = data.get('benchmark_return:發行量加權股價報酬指數') \
        .squeeze() \
        .reindex(adj_close.index, method='ffill')  # 向前填充缺失值，確保時間對齊

    # 設定計算Beta和CAGR所需的天數
    days = 20

    # 使用TALib計算Beta值
    beta = adj_close.apply(lambda s: talib.BETA(s.ffill(), benchmark, timeperiod=days))

    # 計算複合年增長率 (CAGR)
    cagr = (np.exp(np.log(adj_close.pct_change().add(1)).rolling(days).sum())).add(-1)
    cagr_benchmark = (np.exp(np.log(benchmark.pct_change().add(1)).rolling(days).sum())).add(-1)

    # 計算Alpha值
    alpha = cagr - beta * cagr_benchmark

    from finlab import backtest

    # 獲取市值和成交股數，計算公眾流通量係數
    market_cap = data.get('etl:market_value')
    vol = data.get('price:成交股數')
    vol_m = vol.resample('M').sum()  # 按月匯總成交股數
    close = data.get('price:收盤價')

    # 篩選出市值排名前50的非大盤股
    large_cap = market_cap.is_largest(50)
    weight = market_cap

    # 根據Alpha、Beta和其他財務指標篩選股票
    position = alpha[
                   (~large_cap) &  # 排除大盤股
                   (beta > 0) &  # 篩選Beta值大於0的股票
                   (data.get('fundamental_features:經常稅後淨利') > 0) &  # 篩選淨利潤為正的股票
                   (close.notna().cumsum() > 250) &  # 篩選上市超過一年的股票
                   (vol_m.average(12).rank(axis=1, pct=True) > 0.3) &  # 成交量在過去一年中位於前30%
                   ((vol_m.average(3) > 10000_000) | (vol_m.average(3) * close / weight > 0.06))
                   ].is_largest(50) * weight  # 最終選取市值加權最大的50檔股票

    # 執行回測
    r1 = backtest.sim(position,
                      resample='Q',  # 按季度調整持倉
                      resample_offset='7D',  # 調倉日為每季度第7個工作日
                      position_limit=0.2,  # 單一股票持倉上限為20%
                      upload=False)

    from scipy.stats import ttest_ind

    # 计算超額報酬
    excess_return = (r1.creturn.pct_change() - benchmark.pct_change() + 1).resample('M').prod() - 1
    # 2017年之前的超額報酬
    e1 = excess_return.loc[:'2017']
    # 2019年之后的超額報酬
    e2 = excess_return.loc['2019':]

    # Perform two-sample t-test
    t_stat, p_value = ttest_ind(e1.values, e2.values)
    p_value

    # 選擇 00733 中，權重最大的五檔標的進行投資
    new_position = position.is_largest(3) * weight

    results = backtest.sim(new_position, resample='Q')

    return results


if __name__ == "__main__":
    results = etf_00733()
