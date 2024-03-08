import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def process_data(raw_data):
    '''
    Args:
        raw_data: data file that I am working with
    Returns:
        cleaned_data: location of file with cleaned data
    
    '''
    # Load the CSV file using pandas
    data = pd.read_csv(raw_data)

    # Get the column names
    column_names = data.columns.tolist()

    # Print the column names
    # for column in column_names:
    #     print(column)

    #extract the time, Cal VsenseBatt (Shimmer Sensor), GazeLeftx, GazeLefty, GazeRightx, GazeRighty, pupilLeft, pupilRight
    time = data['Timestamp']
    cal_vsensebatt = data['Cal VSenseBatt (Shimmer Sensor)']
    x_left = data['GazeLeftx']
    y_left = data['GazeLefty']
    x_right = data['GazeRightx']
    y_right = data['GazeRighty']
    l_pupil = data['PupilLeft']
    r_pupil = data['PupilRight']

    #print the first 5 rows of the data for each
    # print(time.head())
    # print(cal_vsensebatt.head())
    # print(x_left.head())
    # print(y_left.head())
    # print(x_right.head())
    # print(y_right.head())
    # print(l_pupil.head())
    # print(r_pupil.head())

    # Average the x and y coordinates
    x_eye = (x_left + x_right) / 2
    y_eye = (y_left + y_right) / 2

    # Subtract out the first time to make the time start at 0
    time = time - time[0]

    # Take seconds from milliseconds
    time = time / 1000

    #average the pupil sizes
    pupil = (l_pupil + r_pupil) / 2

    #invert the vsensebatt to calculate conductance
    conductance = 1/cal_vsensebatt*1e6

    #create linear model
    #convert time into a row vector
    time = time.values.reshape(-1, 1)  # Independent variable
    y = conductance.values  # Dependent variable
    print(time)
    print(y)
    model = LinearRegression()
    model.fit(time, y)

    # Predict the conductance values
    predicted_conductance = model.predict(time)

    #calculate residuals from the linear interpolation of the conductance
    conductance_residuals = conductance - predicted_conductance
    # print(conductance_residuals)

    #calculate the zscore of the residuals
    conductance_zscore = (conductance_residuals - conductance_residuals.mean())/conductance_residuals.std()

    #create a series that contains a 1 if the zscore is greater than 2 and the one before it is less than 2
    peaks = (conductance_zscore > 3)
    # & (conductance_zscore.shift(-1) < 2)

    #print the number of ones in the series
    print(peaks.sum())

    #create df with the time, conductance, x and y coordinates, and pupil size, and the peaks
    df = pd.DataFrame({'time': time.flatten(), 'conductance': conductance, 'x': x_eye, 'y': y_eye, 'pupil': pupil, 'peaks': peaks})



    #save the df to a new csv file
    df.to_csv('sensors.csv', index=False)