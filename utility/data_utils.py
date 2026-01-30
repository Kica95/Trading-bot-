import pandas as pd


def extract_column_values(input_file, column_name, max_elements=-1):
    """
    Extracts a column from a file and returns the values as a list.

    Parameters:
        input_file (str): Path to the tab-separated input file.
        column_name (str): Name of the column to extract.

    Returns:
        list: A list of values from the specified column.
    """
    try:
        df = pd.read_csv(input_file, sep="\t")
        if column_name not in df.columns:
            print(f"Column '{column_name}' not found in {input_file}.")
            return []
        if max_elements<0:
            return df[column_name].tolist()
        else:
            return df[column_name].tolist()[:max_elements]

    except Exception as e:
        print(f"Error: {e}")
        return []


import pandas as pd

def extract_column_file(input_file, column_name, output_file, nth_line=1):
    """
    Extracts a specific column from a text file, removes the header row,
    and saves every nth line into a new file.

    Parameters:
        input_file (str): The path of the text file to read from.
        column_name (str): The name of the column to extract.
        output_file (str): The path of the text file to save the extracted column.
        nth_line (int): Keep only every nth line after removing header. Default is 1 (keep all).

    Returns:
        None
    """
    try:
        # Read the file with header
        df = pd.read_csv(input_file, sep="\t")

        # Check if the column exists
        if column_name not in df.columns:
            print(f"Error: Column '{column_name}' not found in {input_file}. Available columns: {df.columns.tolist()}")
            return

        # Extract the column (as Series, no header row in output)
        extracted_df = df[[column_name]]

        # Remove the header row ("close") -> that's already handled by pandas header
        # So we only need to ensure we keep the numeric data
        extracted_df = extracted_df.iloc[::nth_line]  # no skip needed, header already excluded

        # Save to new file, without column name
        extracted_df.to_csv(output_file, sep="\t", index=False, header=False)

        print(f"Column '{column_name}' (every {nth_line} line, no header) successfully extracted to {output_file}")

    except Exception as e:
        print(f"Error processing {input_file}: {e}")


def compute_open_close_difference(input_file, output_file):
    """
    Computes the difference between the 'open' and 'close' values from a text file,
    rounds the result to two decimal places, and saves it into a new file.

    Parameters:
        input_file (str): The path of the text file to read from.
        output_file (str): The path of the text file to save the results.

    Returns:
        None
    """
    try:
        # Read the file
        df = pd.read_csv(input_file, sep="\t")

        # Check if the required columns exist
        if "open" not in df.columns or "close" not in df.columns:
            print(f"Error: Columns 'open' or 'close' not found in {input_file}. Available columns: {df.columns.tolist()}")
            return

        # Compute the difference and round to two decimal places
        df["open_close_diff"] = (df["open"] - df["close"]).round(2)

        # Save to new file
        df[["timestamp", "open_close_diff"]].to_csv(output_file, sep="\t", index=False)

        print(f"Computed open-close difference (rounded) and saved to {output_file}")

    except Exception as e:
        print(f"Error processing {input_file}: {e}")


def find_highest_lowest_difference(input_file):
    """
    Finds the highest and lowest differences from a difference file.

    Parameters:
        input_file (str): The path of the text file containing the 'open_close_diff' column.

    Returns:
        dict: A dictionary containing the highest and lowest differences with timestamps.
    """
    try:
        # Read the file
        df = pd.read_csv(input_file, sep="\t")

        # Check if required column exists
        if "open_close_diff" not in df.columns:
            print(
                f"Error: Column 'open_close_diff' not found in {input_file}. Available columns: {df.columns.tolist()}")
            return None

        # Find highest and lowest differences
        max_diff_row = df.loc[df["open_close_diff"].idxmax()]
        min_diff_row = df.loc[df["open_close_diff"].idxmin()]

        # Store results
        result = {
            "highest": {"timestamp": max_diff_row["timestamp"], "value": round(max_diff_row["open_close_diff"], 2)},
            "lowest": {"timestamp": min_diff_row["timestamp"], "value": round(min_diff_row["open_close_diff"], 2)},
        }

        return result

    except Exception as e:
        print(f"Error processing {input_file}: {e}")
        return None


def main1():

    # Extract the 'close' price column from a BTCUSDT historical data file
    extract_column_file("../data/data_2025_02/BTCUSDT_1m_historical_data.txt", "close", "data/BTCUSDT_close_prices.txt")

    # Extract 'volume' from Ethereum data
    extract_column_file("../data/data_2025_02/ETHUSDT_1m_historical_data.txt", "volume", "data/ETHUSDT_volume.txt")



def main2():
    # Compute the open-close difference for BTC data
    compute_open_close_difference("../data/data_2025_02/BTCUSDT_1m_historical_data.txt",
                                  "../data/data_2025_02/BTCUSDT_open_close_diff.txt")

    # Compute for Ethereum data
    compute_open_close_difference("../data/data_2025_02/ETHUSDT_1m_historical_data.txt",
                                  "../data/data_2025_02/ETHUSDT_open_close_diff.txt")

    # Compute for BinanceCoin data
    compute_open_close_difference("../data/data_2025_02/BNBUSDT_1m_historical_data.txt",
                                  "../data/data_2025_02/BNBUSDT_open_close_diff.txt")


def main3():
    # Find the highest and lowest differences from the BTCUSDT difference file
    result = find_highest_lowest_difference("../data/data_2025_02/BTCUSDT_open_close_diff.txt")

    if result:
        print("Highest Difference:", result["highest"])
        print("Lowest Difference:", result["lowest"])



# Using the special variable
# __name__
if __name__=="__main__":
    extract_column_file("../data/main_data/BNBUSDT.txt", "high", "../data/main_data/BNBUSDT_high_1m.txt", 1)