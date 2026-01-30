from Example.Binance.utility import extract_column_values


def load_simulation_data(locations, column_names, keys, max_steps=-1):
    """
    Extracts data from text files and structures it as a list of dictionaries (like JSON).
    - If max_steps > 0: data is truncated or padded with None to exactly max_steps.
    - If max_steps == -1: all available data is used with padding only to the longest list.
    """
    if not isinstance(locations, list):
        locations = [locations]
    if not isinstance(column_names, list):
        column_names = [column_names]
    if not isinstance(keys, list):
        keys = [keys]

    sim = {}
    for index, location in enumerate(locations):
        key = keys[index]
        sim[key] = extract_column_values(location, column_names[index], max_steps)

    # Determine desired output length
    if max_steps > 0:
        final_len = max_steps
    else:
        final_len = max(len(v) for v in sim.values())  # use longest list

    # Pad or truncate each list to final_len
    for key in sim:
        sim[key] = sim[key][:final_len] + [None] * max(0, final_len - len(sim[key]))

    # Build structured list of dicts
    simulation_data = [
        {key: sim[key][i] for key in sim}
        for i in range(final_len)
    ]

    return simulation_data

if __name__ == "__main__":
    print(load_simulation_data(["../data/BNBUSDT_open_close_diff.txt","../data/BTCUSDT_open_close_diff.txt"],
                               ["open_close_diff","open_close_diff"],
                               ["open_close_diff_bnb","open_close_diff_btc"]))