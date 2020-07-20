import pandas as pd
import numpy as np
import os


def explode(df, lst_cols, fill_value='', preserve_index=False):
    """
    source：https://stackoverflow.com/questions/12680754/split-explode-pandas-dataframe-string-entry-to-separate-rows
    description: there exist some alias among institution names, such as '鞍山市第四医院/鞍山市肿瘤医院'. For the purpose of
              split them into multiple rows, we use this function...
    """
    # source:
    # make sure `lst_cols` is list-alike
    if (lst_cols is not None
            and len(lst_cols) > 0
            and not isinstance(lst_cols, (list, tuple, np.ndarray, pd.Series))):
        lst_cols = [lst_cols]
    # all columns except `lst_cols`
    idx_cols = df.columns.difference(lst_cols)
    # calculate lengths of lists
    lens = df[lst_cols[0]].str.len()
    # preserve original index values
    idx = np.repeat(df.index.values, lens)
    # create "exploded" DF
    res = (pd.DataFrame({
        col: np.repeat(df[col].values, lens)
        for col in idx_cols},
        index=idx)
           .assign(**{col: np.concatenate(df.loc[lens > 0, col].values)
                      for col in lst_cols}))
    # append those rows that have empty lists
    if (lens == 0).any():
        # at least one list in cells is empty
        res = (res.append(df.loc[lens == 0, idx_cols], sort=False)
               .fillna(fill_value))
    # revert the original index order
    res = res.sort_index()
    # reset index if requested
    if not preserve_index:
        res = res.reset_index(drop=True)
    return res


def transform_into_list(name):
    if '/' not in name:
        return [name]

    return name.split('/')


# get city names
cities = os.listdir('./data')
full_df = pd.DataFrame([], columns=['名称', '地址', '邮编', '省份'])

# combine data
for c in cities:
    c_df = pd.read_excel('./data/{}'.format(c))
    full_df = pd.concat([full_df, c_df[['名称', '地址', '邮编', '省份']]], axis=0)
    print(len(full_df))

# preprocessing
full_df['名称'] = full_df['名称'].apply(lambda x: transform_into_list(x))
full_df = explode(full_df, ['名称'])

# reorder and save into excel file
full_df[['名称', '地址', '邮编', '省份']].to_excel('clinics_all.xlsx')
