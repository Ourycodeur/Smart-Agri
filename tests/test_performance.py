import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score


def test_model_performance():

    model = joblib.load(
        "C:\\Users\\El. OURY BALDE\\Desktop\\P12\\api\\models\\best_random_forest.pkl"
    )

    df = pd.read_csv(
        "C:\\Users\\El. OURY BALDE\\Desktop\\P12\\api\\data\\final_dataset.csv"
    )

    X = df.drop(
        columns=[
            "hg/ha_yield",
            "yield_log"
        ]
    )

    y = df["yield_log"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    y_pred = model.predict(X_test)

    r2 = r2_score(
        y_test,
        y_pred
    )

    assert r2 >= 0.70