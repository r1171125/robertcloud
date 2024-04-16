def protec():
    """
    這是一個受保護的函數,包含了您的關鍵代碼
    """
    import finlab
    from finlab import data
    from finlab import login
    from finlab.backtest import sim
    import datetime
    import pytz
    import matplotlib.pyplot as plt
    import pandas as pd

    # 定義台灣時區
    tz_taiwan = pytz.timezone('Asia/Taipei')

    # 獲取台灣時區的當前時間
    now = datetime.datetime.now(tz_taiwan)

    # 登入 FinLab API
    finlab.login("vAaBvcNeAmbi2OLDvq+9SIu96gfJZy8iuFA58yxhWL8QLKNB1jyjWScd+oJ4Y4Bg#vip_m")

    處置股資訊 = data.get('disposal_information').sort_index()
    close = data.get("price:收盤價")

    # 將不是分盤交易的處置雜訊過濾
    處置股資訊 = 處置股資訊[~處置股資訊["分時交易"].isna()].dropna(how='all')

    # date 為盤後處置股公告日，作為訊號產生日。
    處置股資訊 = 處置股資訊.reset_index()[["stock_id", "date", "處置結束時間"]]
    處置股資訊.columns = ["stock_id", "處置開始時間", "處置結束時間"]

    # 初始位置，將全部股票的position設為0，後續產生持有部位使用
    position = close < 0

    for i in range(0, 處置股資訊.shape[0]):
        stock_id = 處置股資訊.iloc[i, 0]
        # 排除股票代號等於4碼的標地才納入(以普通股為主，排除特殊金融商品)
        if len(stock_id) == 4 and stock_id in close.columns:
            start_day = 處置股資訊.iloc[i, 1]
            end_day = 處置股資訊.iloc[i, 2]
            # 處置時間期間持有
            position.loc[start_day:end_day, stock_id] = True

    report = sim(position, trade_at_price="open", fee_ratio=1.425 / 1000 / 3, position_limit=0.2, name='處置股監獄')

    return report


if __name__ == "__main__":
    results = protec()
