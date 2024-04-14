import finlab

def protec():
    """
    這是一個受保護的函數,包含了您的關鍵代碼
    """
    import finlab
    from finlab import data
    from finlab.backtest import sim
    import pandas as pd
    from datetime import datetime, timedelta
    finlab.login("vAaBvcNeAmbi2OLDvq+9SIu96gfJZy8iuFA58yxhWL8QLKNB1jyjWScd+oJ4Y4Bg#vip_m")

    處置股資訊 = data.get('disposal_information').sort_index()
    處置股資訊 = pd.DataFrame(處置股資訊)

    close = data.get("price:收盤價")
    close = pd.DataFrame(close)

    volume = None
    if data.get('price:成交股數') is not None:
        volume = data.get('price:成交股數') * 1000
    elif data.get('rotc_price:成交股數') is not None:
        volume = data.get('rotc_price:成交股數') * 1000
    volume = pd.DataFrame(volume)

    # 計算5日均量
    volume_5d_avg = volume.rolling(window=5).mean()

    # 篩選5日均量大於5000張的條件
    volume_condition = volume_5d_avg > 3000

    # 設定回測的時間範圍為從當前日期往回10年
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * 10)
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    # 將數據限制在過去10年的範圍內
    close = close.loc[start_date_str:end_date_str]
    volume_5d_avg = volume_5d_avg.loc[start_date_str:end_date_str]

    # 將不是分盤交易的處置雜訊過濾
    處置股資訊 = 處置股資訊[~處置股資訊["分時交易"].isna()].dropna(how='all')

    # 重置索引並重新命名列
    處置股資訊 = 處置股資訊.reset_index()[["stock_id", "date", "處置結束時間"]]
    處置股資訊.columns = ["stock_id", "處置開始時間", "處置結束時間"]

    # 初始位置, 將全部股票的 position 設為 0, 後續產生持有部位使用
    position = close < 0

    # 遍歷處置股資訊
    for i in range(0, 處置股資訊.shape[0]):
        stock_id = 處置股資訊.iloc[i, 0]
        # 排除股票代號等於4碼的標地才納入(以普通股為主，排除特殊金融商品)
        if len(stock_id) == 4:
            start_day = 處置股資訊.iloc[i, 1]
            end_day = 處置股資訊.iloc[i, 2]

            # 檢查該股票在 close 和 volume_5d_avg 中是否都存在
            if stock_id in close.columns and stock_id in volume_5d_avg.columns:
                # 檢查該股票在處置期間的5日均量是否大於3000張
                if (volume_5d_avg.loc[start_day:end_day, stock_id] > 3000).all():
                    # 如果 start_day 不在 close 中,找到最接近的下一個交易日
                    while start_day not in close.index:
                        start_day += pd.Timedelta(days=1)

                    # 獲取該股票在處置開始日的開盤價
                    open_price = close.loc[start_day, stock_id]

                    # 計算需要買入的股數,使其約當100萬
                    shares_to_buy = 1000000 // open_price

                    # 將該股票在處置期間的持倉設為需要買入的股數
                    position.loc[start_day:end_day, stock_id] = shares_to_buy

    # 執行回測
    report = sim(position, trade_at_price="open", fee_ratio=1.425 / 1000 / 5, position_limit=0.2, name='監獄策略')

    pass