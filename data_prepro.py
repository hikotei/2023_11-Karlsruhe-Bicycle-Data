# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =	
# Import libraries
import os
import numpy as np
import pandas as pd
import yfinance as yf
import holidays
from datetime import datetime, timedelta

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =	

def create_features_df(df, holiday_method='simple', lags=None):

    df_out = df.copy()

    # - - - - - - - - - - - - - - - - - - - - - -
    # basic features 
    # - - - - - - - - - - - - - - - - - - - - - -

    # add hour
    df_out["hour"] = df_out['timestamp_CET'].dt.hour
    # add weekday
    df_out["weekday"] = df_out['timestamp_CET'].dt.weekday
    # add month
    df_out["month"] = df_out['timestamp_CET'].dt.month
    # add weeknum
    # df_out["weeknum"] = df_out['timestamp_CET'].dt.isocalendar().week

    # - - - - - - - - - - - - - - - - - - - - - -
    # holidays
    # - - - - - - - - - - - - - - - - - - - - - -

    # get all years in dataframe
    uniq_yrs = df_out['timestamp_CET'].dt.year.unique()
    # print(f"unique years in df: {uniq_yrs}")
    
    # get holidays for germany for all states and combine them into one single dict
    states = ['BB', 'BE', 'BW', 'BY', 'BYP', 'HB', 'HE', 'HH', 'MV', 
              'NI', 'NW', 'RP', 'SH', 'SL', 'SN', 'ST', 'TH']
    
    holidays_de = holidays.CountryHoliday('DE', years=uniq_yrs)
    for state in states:
        holidays_de.update(holidays.CountryHoliday('DE', state=state, years=uniq_yrs))

    # sort holidays
    holidays_de = dict(sorted(holidays_de.items()))
    holidays_de_dates = list(holidays_de.keys())

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    # only one holiday dummy for all holidays
    if holiday_method == 'simple':

        df_out['is_holiday'] = df_out['timestamp_CET'].dt.date.isin(holidays_de_dates).astype(int)

    # create separate dummies for each holiday ...
    if holiday_method == 'separate' :

        # newyears + silvester ist kein feiertag aber die meisten nehmen trotzdem frei
        # create dummy variable for all rows where timestamp_CET is 12.31 or 01.01
        df_out['is_holiday_newyear_d31'] = ((df_out['timestamp_CET'].dt.month == 12) & (df_out['timestamp_CET'].dt.day == 31))
        df_out['is_holiday_newyear_d01'] = ((df_out['timestamp_CET'].dt.month == 1) & (df_out['timestamp_CET'].dt.day == 1))

        # Heilige Drei Könige (01.06)
        threekings_dates = [k for k, v in holidays_de.items() if v == 'Heilige Drei Könige']
        df_out['is_holiday_threekings'] = df_out['timestamp_CET'].dt.date.isin(threekings_dates)

        # Karfreitag (easter - 2d)
        karfreitag_dates = [k for k, v in holidays_de.items() if v == 'Karfreitag']
        df_out['is_holiday_karfreitag'] = df_out['timestamp_CET'].dt.date.isin(karfreitag_dates)

        # Eastermonday (easter + 1d)
        easter_dates = [k for k, v in holidays_de.items() if v == 'Ostermontag']
        df_out['is_holiday_easter'] = df_out['timestamp_CET'].dt.date.isin(easter_dates)

        # Erster Mai / Tag der Arbeit (05.01)
        erstermai_dates = [k for k, v in holidays_de.items() if v == 'Erster Mai']
        df_out['is_holiday_erstermai'] = df_out['timestamp_CET'].dt.date.isin(erstermai_dates)

        # Christi Himmelfahrt (easter + 39d)
        himmelfahrt_dates = [k for k, v in holidays_de.items() if v == 'Christi Himmelfahrt']
        df_out['is_holiday_himmelfahrt'] = df_out['timestamp_CET'].dt.date.isin(himmelfahrt_dates)

        # Pfingstmontag (easter + 50d)
        pfingstmontag_dates = [k for k, v in holidays_de.items() if v == 'Pfingstmontag']
        df_out['is_holiday_pfingstmontag'] = df_out['timestamp_CET'].dt.date.isin(pfingstmontag_dates)

        # Fronleichnam (easter + 60d)
        fronleichnam_dates = [k for k, v in holidays_de.items() if v == 'Fronleichnam']
        df_out['is_holiday_fronleichnam'] = df_out['timestamp_CET'].dt.date.isin(fronleichnam_dates)

        # Maria Himmelfahrt (08.15)
        mariahimmelfahrt_dates = [k for k, v in holidays_de.items() if v == 'Mariä Himmelfahrt']
        df_out['is_holiday_mariahimmelfahrt'] = df_out['timestamp_CET'].dt.date.isin(mariahimmelfahrt_dates)

        # Tag der Deutschen Einheit (10.03)
        einheit_dates = [k for k, v in holidays_de.items() if v == 'Tag der Deutschen Einheit']
        df_out['is_holiday_einheit'] = df_out['timestamp_CET'].dt.date.isin(einheit_dates)

        # Reformationstag (10.31)
        reformationstag_dates = [k for k, v in holidays_de.items() if v == 'Reformationstag']
        df_out['is_holiday_reformationstag'] = df_out['timestamp_CET'].dt.date.isin(reformationstag_dates)

        # Allerheiligen (11.01)
        allerheiligen_dates = [k for k, v in holidays_de.items() if v == 'Allerheiligen']
        df_out['is_holiday_allerheiligen'] = df_out['timestamp_CET'].dt.date.isin(allerheiligen_dates)

        # christmas = list of datetimes from 12.24 to 12.26 
        df_out['is_holiday_xmas_d23'] = ((df_out['timestamp_CET'].dt.month == 12) & (df_out['timestamp_CET'].dt.day == 23))
        df_out['is_holiday_xmas_d24'] = ((df_out['timestamp_CET'].dt.month == 12) & (df_out['timestamp_CET'].dt.day == 24))
        df_out['is_holiday_xmas_d25'] = ((df_out['timestamp_CET'].dt.month == 12) & (df_out['timestamp_CET'].dt.day == 25))
        df_out['is_holiday_xmas_d26'] = ((df_out['timestamp_CET'].dt.month == 12) & (df_out['timestamp_CET'].dt.day == 26))

        # brückentage zwischen weihnachten und neujahr
        # 12.27, 12.28, 12.29, 12.30
        df_out['is_holiday_xmas2newyear'] = ((df_out['timestamp_CET'].dt.month == 12) & (df_out['timestamp_CET'].dt.day.isin([27,28,29,30])))

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # reformat all columns that begin with "is_holiday" to int
        for col in df_out.columns:
            if col.startswith('is_holiday'):
                df_out[col] = df_out[col].astype(int)

    # - - - - - - - - - - - - - - - - - - - - - -
    # lags
    # - - - - - - - - - - - - - - - - - - - - - -

    # only if column 'gesamt' exists
    if 'gesamt' in df_out.columns:
        # add lagged versions of column 'gesamt' based on input lags list of lagged values
        if lags is not None:
            for lag in lags:
                df_out[f"lag_{lag}"] = df_out["gesamt"].shift(lag)

            # take biggest value in lags and remove first rows in df_out to get rid of NaNs
            max_lag = max(lags)
            df_out = df_out[max_lag:]

    # - - - - - - - - - - - - - - - - - - - - - -
    # df_out.drop(columns=["timestamp_CET"], inplace=True)

    return df_out

def create_dummy_df(df, month_method='simple', weekday_method='simple', hour_method='simple', holiday_method='simple'):

    df_out = df.copy()

    if month_method == 'simple':
        
        # https://stackoverflow.com/a/37426982/15816035
        # - - - - - - - - - - - - - - - - - - - - - - -
        # cats = ['a', 'b', 'c']
        # df = pd.DataFrame({'cat': ['a', 'b', 'a']})

        # dummies = pd.get_dummies(df, prefix='', prefix_sep='')
        # dummies = dummies.T.reindex(cats).T.fillna(0)

        cats = ['month_1', 'month_2', 'month_3', 'month_4', 'month_5', 'month_6', 'month_7', 'month_8', 'month_9', 'month_10', 'month_11', 'month_12']

        # binary dummy var for each month
        dummy_month = pd.get_dummies(df_out['timestamp_CET'].dt.month, prefix='month').astype(int)
        dummy_month = dummy_month.T.reindex(cats).T.fillna(0)
        # leave out first month to avoid multicollinearity
        dummy_month = dummy_month.iloc[:, 1:]
        # add values dummy_month to df_temp
        df_out = pd.concat([df_out, dummy_month], axis=1)

    if weekday_method == 'simple':

        cats = ['weekday_0', 'weekday_1', 'weekday_2', 'weekday_3', 'weekday_4', 'weekday_5', 'weekday_6']

        # binary dummy var for each weekday
        dummy_weekday = pd.get_dummies(df_out['timestamp_CET'].dt.weekday, prefix='weekday').astype(int)
        dummy_weekday = dummy_weekday.T.reindex(cats).T.fillna(0)
        # leave out first weekday to avoid multicollinearity
        dummy_weekday = dummy_weekday.iloc[:, 1:]

        df_out = pd.concat([df_out, dummy_weekday], axis=1)

    # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
    # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
    # create hour dummies

    if hour_method == 'simple':

        # binary dummy var for each hour
        dummy_hour = pd.get_dummies(df_out['timestamp_CET'].dt.hour, prefix='hour').astype(int)
        # leave out first hour to avoid multicollinearity
        dummy_hour = dummy_hour.iloc[:, 1:]
        df_out = pd.concat([df_out, dummy_hour], axis=1)

    if hour_method == 'seasonal':

        # separate hourly dummy vars for summer and winter months
        summer_months = [4, 5, 6, 7, 8, 9]
        df_out['is_summer'] = df_out['timestamp_CET'].dt.month.isin(summer_months).astype(int)

        # create dummy variables for each hour in summer months
        for hr in range(1, 24):
            # skip hour 0 in summer to avoid multicollinearity
            df_out[f'hour_{hr}_summer'] = ((df_out['is_summer'] == 1) & (df_out['timestamp_CET'].dt.hour == hr)).astype(int)

        for hr in range(1, 24):
            # skip hour 0 in winter to avoid multicollinearity
            df_out[f'hour_{hr}_winter'] = ((df_out['is_summer'] == 0) & (df_out['timestamp_CET'].dt.hour == hr)).astype(int)

        # drop is_summer
        df_out.drop(columns=['is_summer'], inplace=True)

    if hour_method == 'monthly':

        # separate hourly dummy vars for EVERY month
        month_dict = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May',
                    6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October',
                    11: 'November', 12: 'December'}

        for m_idx in range(1, 13):
            
            m_name = month_dict[m_idx][:3].lower() # short version of month name

            for hr in range(1, 24):
                # skip hour 0 to avoid multicollinearity
                df_out[f'hour_{hr}_{m_name}'] = ((df_out['timestamp_CET'].dt.month == m_idx) & 
                                                 (df_out['timestamp_CET'].dt.hour == hr)).astype(int)

    # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
    # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
    # create holiday dummies

    # get all years in dataframe
    uniq_yrs = df_out['timestamp_CET'].dt.year.unique()

    # get holidays for germany for all states and combine them into one single dict
    states = ['BB', 'BE', 'BW', 'BY', 'BYP', 'HB', 'HE', 'HH', 'MV', 
              'NI', 'NW', 'RP', 'SH', 'SL', 'SN', 'ST', 'TH']
    
    holidays_de = holidays.CountryHoliday('DE', years=uniq_yrs)
    for state in states:
        holidays_de.update(holidays.CountryHoliday('DE', state=state, years=uniq_yrs))

    # sort holidays
    holidays_de = dict(sorted(holidays_de.items()))
    holidays_de_dates = list(holidays_de.keys())

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    # only one holiday dummy for all holidays
    if holiday_method == 'simple':

        df_out['is_holiday'] = df_out['timestamp_CET'].dt.date.isin(holidays_de_dates).astype(int)

    # create separate dummies for each holiday ...
    if holiday_method == 'separate' :

        # newyears + silvester ist kein feiertag aber die meisten nehmen trotzdem frei
        # create dummy variable for all rows where timestamp_CET is 12.31 or 01.01
        df_out['is_holiday_newyear_d31'] = (((df_out['timestamp_CET'].dt.month == 12) & (df_out['timestamp_CET'].dt.day == 31)) | ((df_out['timestamp_CET'].dt.month == 1) & (df_out['timestamp_CET'].dt.day == 1) & (df_out['timestamp_CET'].dt.hour <= 6)))
        df_out['is_holiday_newyear_d01'] = ((df_out['timestamp_CET'].dt.month == 1) & (df_out['timestamp_CET'].dt.day == 1) & (df_out['timestamp_CET'].dt.hour > 6))

        # # List of holiday names
        # holiday_names = [
        #     'Heilige Drei Könige', 'Karfreitag', 'Ostersonntag', 'Ostermontag',
        #     'Erster Mai', 'Christi Himmelfahrt', 'Pfingstmontag', 'Fronleichnam',
        #     'Mariä Himmelfahrt', 'Tag der Deutschen Einheit', 'Reformationstag',
        #     'Allerheiligen'
        # ]

        # # Iterate over holiday names
        # for holiday_name in holiday_names:
        #     # Get corresponding dates for the holiday
        #     holiday_dates = [k for k, v in holidays_de.items() if v == holiday_name]
            
        #     # Create a column for each holiday
        #     column_name = 'is_holiday_' + holiday_name.lower().replace(' ', '')
        #     df_out[column_name] = df_out['timestamp_CET'].dt.date.isin(holiday_dates)

        # Heilige Drei Könige (01.06)
        threekings_dates = [k for k, v in holidays_de.items() if v == 'Heilige Drei Könige']
        df_out['is_holiday_threekings'] = (df_out['timestamp_CET'].dt.date.isin(threekings_dates) & (df_out['timestamp_CET'].dt.hour > 3))

        # Karfreitag (easter - 2d)
        karfreitag_dates = [k for k, v in holidays_de.items() if v == 'Karfreitag']
        df_out['is_holiday_karfreitag'] = (df_out['timestamp_CET'].dt.date.isin(karfreitag_dates) & (df_out['timestamp_CET'].dt.hour > 6))
        # also add the hours till 5am of the following day

        # Eastersunday (easter)
        easter_sun_dates = [k for k, v in holidays_de.items() if v == 'Ostersonntag']
        df_out['is_holiday_easter_sunday'] = df_out['timestamp_CET'].dt.date.isin(easter_sun_dates)

        # Eastermonday (easter + 1d)
        easter_mon_dates = [k for k, v in holidays_de.items() if v == 'Ostermontag']
        df_out['is_holiday_easter_monday'] = (df_out['timestamp_CET'].dt.date.isin(easter_mon_dates) & (df_out['timestamp_CET'].dt.hour > 6))

        # Erster Mai / Tag der Arbeit (05.01)
        erstermai_dates = [k for k, v in holidays_de.items() if v == 'Erster Mai']
        df_out['is_holiday_erstermai'] = (df_out['timestamp_CET'].dt.date.isin(erstermai_dates) & (df_out['timestamp_CET'].dt.hour > 6))

        # Christi Himmelfahrt (easter + 39d)
        himmelfahrt_dates = [k for k, v in holidays_de.items() if v == 'Christi Himmelfahrt']
        df_out['is_holiday_himmelfahrt'] = (df_out['timestamp_CET'].dt.date.isin(himmelfahrt_dates) & (df_out['timestamp_CET'].dt.hour > 6))

        # Pfingstmontag (easter + 50d)
        pfingstmontag_dates = [k for k, v in holidays_de.items() if v == 'Pfingstmontag']
        df_out['is_holiday_pfingstmontag'] = (df_out['timestamp_CET'].dt.date.isin(pfingstmontag_dates) & (df_out['timestamp_CET'].dt.hour > 3))

        # Fronleichnam (easter + 60d)
        fronleichnam_dates = [k for k, v in holidays_de.items() if v == 'Fronleichnam']
        df_out['is_holiday_fronleichnam'] = (df_out['timestamp_CET'].dt.date.isin(fronleichnam_dates) & (df_out['timestamp_CET'].dt.hour > 3))

        # Maria Himmelfahrt (08.15)
        mariahimmelfahrt_dates = [k for k, v in holidays_de.items() if v == 'Mariä Himmelfahrt']
        df_out['is_holiday_mariahimmelfahrt'] = (df_out['timestamp_CET'].dt.date.isin(mariahimmelfahrt_dates) & (df_out['timestamp_CET'].dt.hour > 2))

        # Tag der Deutschen Einheit (10.03)
        einheit_dates = [k for k, v in holidays_de.items() if v == 'Tag der Deutschen Einheit']
        df_out['is_holiday_einheit'] = (df_out['timestamp_CET'].dt.date.isin(einheit_dates) & (df_out['timestamp_CET'].dt.hour > 3))

        # Reformationstag (10.31)
        reformationstag_dates = [k for k, v in holidays_de.items() if v == 'Reformationstag']
        df_out['is_holiday_reformationstag'] = (df_out['timestamp_CET'].dt.date.isin(reformationstag_dates)  & (df_out['timestamp_CET'].dt.hour > 2))

        # Allerheiligen (11.01)
        allerheiligen_dates = [k for k, v in holidays_de.items() if v == 'Allerheiligen']
        df_out['is_holiday_allerheiligen'] = df_out['timestamp_CET'].dt.date.isin(allerheiligen_dates)

        # christmas = list of datetimes from 12.24 to 12.26 
        df_out['is_holiday_xmas_d23'] = ((df_out['timestamp_CET'].dt.month == 12) & (df_out['timestamp_CET'].dt.day == 23) & (df_out['timestamp_CET'].dt.hour > 3))
        df_out['is_holiday_xmas_d24'] = ((df_out['timestamp_CET'].dt.month == 12) & (df_out['timestamp_CET'].dt.day == 24))
        df_out['is_holiday_xmas_d25'] = (((df_out['timestamp_CET'].dt.month == 12) & (df_out['timestamp_CET'].dt.day == 25)) | ((df_out['timestamp_CET'].dt.month == 12) & (df_out['timestamp_CET'].dt.day == 26) & (df_out['timestamp_CET'].dt.hour < 6)))
        df_out['is_holiday_xmas_d26'] = ((df_out['timestamp_CET'].dt.month == 12) & (df_out['timestamp_CET'].dt.day == 26) & (df_out['timestamp_CET'].dt.hour >= 6))

        # brückentage zwischen weihnachten und neujahr
        # 12.27, 12.28, 12.29, 12.30
        df_out['is_holiday_xmas2newyear'] = ((df_out['timestamp_CET'].dt.month == 12) & (df_out['timestamp_CET'].dt.day.isin([27,28,29,30])))

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # reformat all columns that begin with "is_holiday" to int
        for col in df_out.columns:
            if col.startswith('is_holiday'):
                df_out[col] = df_out[col].astype(int)

    return df_out

def fix_quantile_crossing(df):

    df_out = df.copy()
    for index, row in df.iterrows():

        # check if quantiles are in ascending order
        if not all(row.diff().dropna() > 0):
            # print(f'> ERROR: Quantiles are not in ascending order for {index}')
            # print(row)
            # sort columns 
            df_out.loc[index] = row.sort_values().values
            # print(df_ensemble_pred.loc[index])

    return df_out

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =	

# if __name__ == "__main__":
