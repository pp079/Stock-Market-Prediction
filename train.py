import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pandas_datareader as web
import datetime as dt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM

#Load Data
companies = ['AAPL', 'AMZN','CSCO', 'GOOGL','META', 'NFLX', 'NVDA', 'QCOM']

for company in companies:
    start = pd.to_datetime(['2012-01-01']).astype(int)[0]//10**9 # convert to unix timestamp.
    end = pd.to_datetime(['2020-01-01']).astype(int)[0]//10**9 # convert to unix timestamp.
    url = 'https://query1.finance.yahoo.com/v7/finance/download/' + company + '?period1=' + str(start) + '&period2=' + str(end) + '&interval=1d&events=history'
    data = pd.read_csv(url)
    # data = web.DataReader(company, 'yahoo', start, end)

    #prepare data
    scaler = MinMaxScaler(feature_range=(0,1))
    scaled_data = scaler.fit_transform(data['Close'].values.reshape(-1,1))
    prediction_days = 60
    x_train = []
    y_train = []
    for x in range(prediction_days, len(scaled_data)):
        x_train.append(scaled_data[x-prediction_days:x, 0])
        y_train.append(scaled_data[x, 0])
    x_train, y_train=np.array(x_train), np.array(y_train)
    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1],1))

    #build the model

    model=Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(x_train.shape[1],1)))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50, return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50))
    model.add(Dropout(0.2))
    model.add(Dense(units=1))#prediction of next close value

    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(x_train,y_train, epochs=25, batch_size=32)

    #test the data

    #load test data
    test_start = pd.to_datetime(['2020-01-01']).astype(int)[0]//10**9 # convert to unix timestamp.
    test_end = pd.to_datetime([dt.datetime.now()]).astype(int)[0]//10**9 # convert to unix timestamp.
    test_url = 'https://query1.finance.yahoo.com/v7/finance/download/' + company + '?period1=' + str(start) + '&period2=' + str(end) + '&interval=1d&events=history'
    test_data = pd.read_csv(test_url)
    actual_prices= test_data['Close'].values
    total_dataset=pd.concat((data['Close'],test_data['Close']),axis=0)

    model_inputs=total_dataset[len(total_dataset)-len(test_data)-prediction_days:].values
    model_inputs = model_inputs.reshape(-1,1)
    model_inputs = scaler.transform(model_inputs)

    #make prediction on data sets
    x_test= []
    for x in range(prediction_days, len(model_inputs)):
        x_test.append(model_inputs[x-prediction_days:x, 0])

    x_test=np.array(x_test)
    tup=(x_test.shape[0],x_test.shape[1],1)
    x_test = np.reshape(x_test, tup)
    predicted_prices=model.predict(x_test)
    predicted_prices=scaler.inverse_transform(predicted_prices)

    #plot the predictions
    plt.plot(actual_prices,color="black", label=f"Actual {company} Price")
    plt.plot(predicted_prices, color="green",label=f"Predicted {company} Price")
    plt.title(f"{company} Share Price")
    plt.xlabel('Time')
    plt.ylabel(f'{company} Share Price')
    plt.legend()
    plt.savefig(f"Images/{company}.jpg")
    plt.clf()