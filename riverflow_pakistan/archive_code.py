
def get_max_min_percentiles() -> pd.DataFrame:
    # Creating a function max and min from percentiles values
    file = "/Users/mugisha/Desktop/clone/Drought_Pakistan/riverflow_pakistan/flows/indus_at_tarbela.csv"
    flow_data = pd.read_csv(file, index_col=0, parse_dates=True)
    name_of_river = file.split("/")[-1].split(".")[0]

    # Define data storages: 
    list_of_values = []
    out_put_list = []

    for i in range(1, 366):
        out_put = fit_model(flow_data, i, window=10)
        out_put_list.append(out_put)

    for dataframe in out_put_list:
        # change values into a list
        values =dataframe.iloc[:, 0].values.tolist()
        clean_list = [x for x in values if not math.isnan(x)]
        list_of_values.append(clean_list)
 
    # loop through the percentages and compute dataframes
    dfs = {}
    percentages = [0.01, 0.1, 0.25, 0.75, 0.9, 0.99]
    for perc in percentages:
        df = pd.DataFrame(columns=[f'{perc}_value', f'{perc}_value'])
        for i, lst in enumerate(list_of_values):
            lower_bound = np.percentile(lst, perc*100 - 1) if perc != 0.01 else -np.inf
            upper_bound = np.percentile(lst, perc*100)
            values = [x for x in lst if lower_bound < x <= upper_bound]
            if values:
                df.loc[f'list{i+1}'] = [min(values), max(values)]
        dfs[perc] = df.reset_index(drop=True)

    return dfs

get_max_min_percentiles()[0.01]



# main code: 

def create_percentile_dataframe() -> pd.DataFrame:
    # Creating a function max and min from percentiles values
    file = "/Users/mugisha/Desktop/clone/Drought_Pakistan/riverflow_pakistan/flows/indus_at_tarbela.csv"
    flow_data = pd.read_csv(file, index_col=0, parse_dates=True)
    name_of_river = file.split("/")[-1].split(".")[0]

    # Define data storages: 
    list_of_values = []
    out_put_list = []

    for i in range(1, 366):
        out_put = fit_model(flow_data, i, window=10)
        out_put_list.append(out_put)

    for dataframe in out_put_list:
        # change values into a list
        values =dataframe.iloc[:, 0].values.tolist()
        clean_list = [x for x in values if not math.isnan(x)]
        list_of_values.append(clean_list)

    Plot_dataframe = pd.DataFrame(columns=["min_value", "0.1_value","0.25_value","0.75_value","0.9_value","max_value"])
    for i, lst in enumerate(list_of_values):
        percentages = [0.1, 0.25, 0.75, 0.9]
        min_value = min(lst)
        max_value = max(lst)

        # create a list of values for each percentile and incldue the min and max values which are the min and max values all in a comphrensive list
        percentile_values = [min_value] + [np.percentile(lst, perc*100) for perc in percentages] + [max_value]
        # Plot_dataframe.loc[f'list{i+1}'] = percentile_values
        Plot_dataframe.loc[f'list{i+1}'] = percentile_values
        Plot_dataframe = Plot_dataframe.reset_index(drop=True)



    return Plot_dataframe
create_percentile_dataframe()