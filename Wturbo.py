import finlab
def turbo():
    """
    這是一個受保護的函數
    """
    import finlab
    from finlab import data
    from finlab.backtest import sim
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    import pandas as pd

    # 登入 FinLab API
    finlab.login("vAaBvcNeAmbi2OLDvq+9SIu96gfJZy8iuFA58yxhWL8QLKNB1jyjWScd+oJ4Y4Bg#vip_m")

    # 设置日期
    latest_date = datetime.today().date()
    start_date = latest_date - relativedelta(years=10)

    # 获取数据
    close = data.get('price:收盤價')
    vol = data.get('price:成交股數')
    rev = data.get('monthly_revenue:當月營收')
    rev_yoy_growth = data.get('monthly_revenue:去年同月增減(%)')

    # 使用 Pandas 日期索引来过滤数据
    close = close.loc[start_date:latest_date]
    vol = vol.loc[start_date:latest_date]
    rev = rev.loc[start_date:latest_date]
    rev_yoy_growth = rev_yoy_growth.loc[start_date:latest_date]

    # 数据处理和条件设置部分
    rev_ma = rev.average(2)
    condition1 = rev_ma == rev_ma.rolling(12, min_periods=6).max()
    condition2 = (close == close.rolling(200).max()).sustain(5, 2)
    condition3 = vol.average(5) > 500 * 3000
    conditions = condition1 & condition2 & condition3

    # 符合选股条件的名单中，再选出单月营收年增率前10强，并在营收公告截止日换股。
    position = rev_yoy_growth * conditions
    position = position[position > 0].is_largest(10).reindex(rev.index_str_to_date().index, method='ffill')

    # 执行回测
    results = sim(position=position, stop_loss=0.2, take_profit=0.8, position_limit=0.25, fee_ratio=1.425 / 1000 * 0.3,
                  name="營收股價雙渦輪")

    # 打印结果
    print(results)
    return results


if __name__ == "__main__":
    results = turbo()