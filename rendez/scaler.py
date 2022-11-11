"""
used to scale and de-scale inputs to the optimzier
"""
from sklearn.preprocessing import StandardScaler
import pandas as pd


class Scaler:
    def __init__(self):
        self.scaler = StandardScaler()
        self.mult = 1e4

    def scale(self, df, objs: dict):
        self.cols = list(objs.keys())
        self.obj_scale = {key + "_SCALED": val for key, val in objs.items()}
        self.scaled_cols = list(self.obj_scale.keys())
        df = self.standard_scale(df)
        df[self.scaled_cols] = df[self.scaled_cols].fillna(0)
        df = self.fit_to_int(df)
        return df, self.obj_scale

    def standard_scale(self, df):
        df[self.scaled_cols] = self.scaler.fit_transform(pd.DataFrame(df[self.cols]))
        return df

    def fit_to_int(self, df):
        df[self.scaled_cols] = df[self.scaled_cols] * self.mult
        df[self.scaled_cols] = df[self.scaled_cols].round(0).astype(int)
        return df
