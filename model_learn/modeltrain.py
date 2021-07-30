import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split


def load_data():
    data = pd.read_excel('data.ods', sheet_name=2)
    return data


def to_metric(df):
    mph = 0.44704
    yrd = 0.9144
    conversion = {
        'ball_speed': mph,
        'side': yrd,
        'height': yrd,
        'carry': yrd,
        'total': yrd,
    }

    for col, conv in conversion.items():
        if col in df.columns:
            df[col] = df[col]*conv
    return df


if __name__ == '__main__':
    data = load_data()
    data = to_metric(data)

    features = ['ball_speed', 'launch_angle', 'side_angle', 'backspin', 'sidespin']
    targets = ['landing_angle', 'side', 'height', 'carry', 'total']

    X = data[features]
    y = data[targets]
    X_train, X_test, y_train, y_test = train_test_split(X, y)

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)