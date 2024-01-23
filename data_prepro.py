# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =	
# Import libraries
import os
import numpy as np
import pandas as pd
import yfinance as yf
import holidays
from datetime import datetime, timedelta

school_holiday_bw_url = 'https://raw.githubusercontent.com/hikotei/2023_11-Karlsruhe-Bicycle-Data/main/data/schulferien_BW_2012_2024.csv'

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =	

def create_features_df(df, holiday_method='simple', lags=None, school_holidays_bw=False):

    df_out = df.copy()

    # - - - - - - - - - - - - - - - - - - - - - -
    # basic features 
    # - - - - - - - - - - - - - - - - - - - - - -

    # add weekday
    df_out["weekday"] = df_out['timestamp_CET'].dt.weekday
    # add month
    df_out["month"] = df_out['timestamp_CET'].dt.month
    # add weeknum
    df_out["weeknum"] = df_out['timestamp_CET'].dt.isocalendar().week

    # - - - - - - - - - - - - - - - - - - - - - -
    # holidays
    # - - - - - - - - - - - - - - - - - - - - - -

    # get all years in dataframe
    uniq_yrs = df_out['timestamp_CET'].dt.year.unique()
    # print(f"unique years in df: {uniq_yrs}")
    
    # get holidays for germany for all states and combine them into one single dict
    # states = ['BB', 'BE', 'BW', 'BY', 'BYP', 'HB', 'HE', 'HH', 'MV', 
    #           'NI', 'NW', 'RP', 'SH', 'SL', 'SN', 'ST', 'TH']
    states = ['BW']
    
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

    # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
    # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
    # create school holiday dummies

    if school_holidays_bw:

        # get school holidays from github
        df_school_hol_bw = pd.read_csv(school_holiday_bw_url)
        df_school_hol_bw['start'] = pd.to_datetime(df_school_hol_bw['start'])
        df_school_hol_bw['end'] = pd.to_datetime(df_school_hol_bw['end'])
        df_school_hol_bw['stateCode'] = df_school_hol_bw['stateCode'].astype('string')
        df_school_hol_bw['name'] = df_school_hol_bw['name'].astype('string')

        if holiday_method == 'simple':

            # set is_school_holiday = 1 for all rows where timestamp_CET is any school holiday
            # first create list of all dates that are school holidays

            school_hol_bw_list = []
            for _, row in df_school_hol_bw.iterrows():
                date_range = pd.date_range(start=row['start'], end=row['end'])
                school_hol_bw_list.extend(date_range)
                
            df_out['is_holiday_school'] = df_out['timestamp_CET'].isin(school_hol_bw_list).astype(int)

        if holiday_method == 'separate':

            # for each unique school holiday, 
            # create a separate "is_holiday_school ... " column
            # that = 1 if timestamp_CET is that holiday, else 0

            # first create a list of dates for each unique school holiday
            unique_school_holidays = df_school_hol_bw['name'].unique()
            # create dict with keys = unique school holidays
            unique_school_holidays_dict = {elem : [] for elem in unique_school_holidays}
            
            for _, row in df_school_hol_bw.iterrows():
                date_range = pd.date_range(start=row['start'], end=row['end'])
                unique_school_holidays_dict[row['name']].extend(date_range)

            # create a new column for each unique school holiday
            for holiday in unique_school_holidays:
                holiday_str = holiday.lower().replace(' ', '_')
                df_out[f'is_holiday_school_{holiday_str}'] = df_out['timestamp_CET'].isin(unique_school_holidays_dict[holiday]).astype(int)

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

def create_dummy_df(df, month_method='simple', weekday_method='simple', hour_method='simple', holiday_method='simple', school_holidays_bw=False):

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
    # create holiday dummies

    # get all years in dataframe
    uniq_yrs = df_out['timestamp_CET'].dt.year.unique()

    # # get holidays for germany for all states and combine them into one single dict
    # states = ['BB', 'BE', 'BW', 'BY', 'BYP', 'HB', 'HE', 'HH', 'MV', 
    #           'NI', 'NW', 'RP', 'SH', 'SL', 'SN', 'ST', 'TH']
    states = ['BW']

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

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # create separate dummies for each holiday ...
    if holiday_method == 'separate' :

        # newyears + silvester ist kein feiertag aber die meisten nehmen trotzdem frei
        # create dummy variable for all rows where timestamp_CET is 12.31 or 01.01
        df_out['is_holiday_newyear_d31'] = (((df_out['timestamp_CET'].dt.month == 12) & (df_out['timestamp_CET'].dt.day == 31)) | ((df_out['timestamp_CET'].dt.month == 1) & (df_out['timestamp_CET'].dt.day == 1)))
        df_out['is_holiday_newyear_d01'] = ((df_out['timestamp_CET'].dt.month == 1) & (df_out['timestamp_CET'].dt.day == 1))

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
        df_out['is_holiday_threekings'] = (df_out['timestamp_CET'].dt.date.isin(threekings_dates))

        # Karfreitag (easter - 2d)
        karfreitag_dates = [k for k, v in holidays_de.items() if v == 'Karfreitag']
        df_out['is_holiday_karfreitag'] = (df_out['timestamp_CET'].dt.date.isin(karfreitag_dates))
        # also add the hours till 5am of the following day

        # Eastersunday (easter)
        easter_sun_dates = [k for k, v in holidays_de.items() if v == 'Ostersonntag']
        df_out['is_holiday_easter_sunday'] = df_out['timestamp_CET'].dt.date.isin(easter_sun_dates)

        # Eastermonday (easter + 1d)
        easter_mon_dates = [k for k, v in holidays_de.items() if v == 'Ostermontag']
        df_out['is_holiday_easter_monday'] = (df_out['timestamp_CET'].dt.date.isin(easter_mon_dates))

        # Erster Mai / Tag der Arbeit (05.01)
        erstermai_dates = [k for k, v in holidays_de.items() if v == 'Erster Mai']
        df_out['is_holiday_erstermai'] = (df_out['timestamp_CET'].dt.date.isin(erstermai_dates))

        # Christi Himmelfahrt (easter + 39d)
        himmelfahrt_dates = [k for k, v in holidays_de.items() if v == 'Christi Himmelfahrt']
        df_out['is_holiday_himmelfahrt'] = (df_out['timestamp_CET'].dt.date.isin(himmelfahrt_dates))

        # Pfingstmontag (easter + 50d)
        pfingstmontag_dates = [k for k, v in holidays_de.items() if v == 'Pfingstmontag']
        df_out['is_holiday_pfingstmontag'] = (df_out['timestamp_CET'].dt.date.isin(pfingstmontag_dates))

        # Fronleichnam (easter + 60d)
        fronleichnam_dates = [k for k, v in holidays_de.items() if v == 'Fronleichnam']
        df_out['is_holiday_fronleichnam'] = (df_out['timestamp_CET'].dt.date.isin(fronleichnam_dates))

        # Maria Himmelfahrt (08.15)
        mariahimmelfahrt_dates = [k for k, v in holidays_de.items() if v == 'Mariä Himmelfahrt']
        df_out['is_holiday_mariahimmelfahrt'] = (df_out['timestamp_CET'].dt.date.isin(mariahimmelfahrt_dates))

        # Tag der Deutschen Einheit (10.03)
        einheit_dates = [k for k, v in holidays_de.items() if v == 'Tag der Deutschen Einheit']
        df_out['is_holiday_einheit'] = (df_out['timestamp_CET'].dt.date.isin(einheit_dates))

        # Reformationstag (10.31)
        reformationstag_dates = [k for k, v in holidays_de.items() if v == 'Reformationstag']
        df_out['is_holiday_reformationstag'] = (df_out['timestamp_CET'].dt.date.isin(reformationstag_dates))

        # Allerheiligen (11.01)
        allerheiligen_dates = [k for k, v in holidays_de.items() if v == 'Allerheiligen']
        df_out['is_holiday_allerheiligen'] = df_out['timestamp_CET'].dt.date.isin(allerheiligen_dates)

        # christmas = list of datetimes from 12.24 to 12.26 
        df_out['is_holiday_xmas_d23'] = ((df_out['timestamp_CET'].dt.month == 12) & (df_out['timestamp_CET'].dt.day == 23))
        df_out['is_holiday_xmas_d24'] = ((df_out['timestamp_CET'].dt.month == 12) & (df_out['timestamp_CET'].dt.day == 24))
        df_out['is_holiday_xmas_d25'] = (((df_out['timestamp_CET'].dt.month == 12) & (df_out['timestamp_CET'].dt.day == 25)) | ((df_out['timestamp_CET'].dt.month == 12) & (df_out['timestamp_CET'].dt.day == 26)))
        df_out['is_holiday_xmas_d26'] = ((df_out['timestamp_CET'].dt.month == 12) & (df_out['timestamp_CET'].dt.day == 26))

        # brückentage zwischen weihnachten und neujahr (12.27, 12.28, 12.29, 12.30)
        df_out['is_holiday_xmas2newyear'] = ((df_out['timestamp_CET'].dt.month == 12) & (df_out['timestamp_CET'].dt.day.isin([27,28,29,30])))

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # reformat all columns that begin with "is_holiday" to int
        for col in df_out.columns:
            if col.startswith('is_holiday'):
                df_out[col] = df_out[col].astype(int)

    # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
    # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
    # create school holiday dummies

    if school_holidays_bw:

        # get school holidays from github
        df_school_hol_bw = pd.read_csv(school_holiday_bw_url)
        df_school_hol_bw['start'] = pd.to_datetime(df_school_hol_bw['start'])
        df_school_hol_bw['end'] = pd.to_datetime(df_school_hol_bw['end'])
        df_school_hol_bw['stateCode'] = df_school_hol_bw['stateCode'].astype('string')
        df_school_hol_bw['name'] = df_school_hol_bw['name'].astype('string')

        if holiday_method == 'simple':

            # set is_school_holiday = 1 for all rows where timestamp_CET is any school holiday
            # first create list of all dates that are school holidays

            school_hol_bw_list = []
            for _, row in df_school_hol_bw.iterrows():
                date_range = pd.date_range(start=row['start'], end=row['end'])
                school_hol_bw_list.extend(date_range)
                
            df_out['is_holiday_school'] = df_out['timestamp_CET'].isin(school_hol_bw_list).astype(int)

        if holiday_method == 'separate':

            # for each unique school holiday, 
            # create a separate "is_holiday_school ... " column
            # that = 1 if timestamp_CET is that holiday, else 0

            # first create a list of dates for each unique school holiday
            unique_school_holidays = df_school_hol_bw['name'].unique()
            # create dict with keys = unique school holidays
            unique_school_holidays_dict = {elem : [] for elem in unique_school_holidays}
            
            for _, row in df_school_hol_bw.iterrows():
                date_range = pd.date_range(start=row['start'], end=row['end'])
                unique_school_holidays_dict[row['name']].extend(date_range)

            # create a new column for each unique school holiday
            for holiday in unique_school_holidays:

                # print(holiday.lower())
                # skip winter, easter and pfingst holidays
                # if 'weihnacht' in holiday.lower() or 'oster' in holiday.lower() or 'pfingst' in holiday.lower():
                #     print(f">> skipping {holiday.lower()}")
                #     continue

                holiday_str = holiday.lower().replace(' ', '_')
                df_out[f'is_holiday_school_{holiday_str}'] = df_out['timestamp_CET'].isin(unique_school_holidays_dict[holiday]).astype(int)
    
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
