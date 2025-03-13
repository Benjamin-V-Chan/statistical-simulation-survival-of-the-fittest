import pandas as pd
import matplotlib.pyplot as plt

def plot_overlapping_attributes(csv_filename, attributes):
    """
    Reads the simulation CSV file and plots multiple attributes on the same line chart 
    with normalized values (0 to 1) for better comparison.

    Parameters:
    - csv_filename: The name of the CSV file generated from the simulation.
    - attributes: A list of column names to plot.
    """
    try:
        # Load CSV data
        df = pd.read_csv(csv_filename)

        # Validate attributes
        available_attributes = df.columns.tolist()
        valid_attributes = [attr for attr in attributes if attr in available_attributes]
        invalid_attributes = [attr for attr in attributes if attr not in available_attributes]

        if invalid_attributes:
            print(f"Warning: These attributes were not found and will be skipped: {invalid_attributes}")

        if not valid_attributes:
            print("No valid attributes selected. Available columns:", available_attributes)
            return

        # Normalize the selected attributes using Min-Max Scaling (0 to 1)
        normalized_df = df.copy()
        for attribute in valid_attributes:
            min_val = df[attribute].min()
            max_val = df[attribute].max()
            if max_val != min_val:  # Avoid division by zero
                normalized_df[attribute] = (df[attribute] - min_val) / (max_val - min_val)
            else:
                normalized_df[attribute] = 0  # If all values are the same, set them to 0

        # Create figure
        plt.figure(figsize=(12, 6))

        # Plot each valid attribute as a separate line (normalized)
        for attribute in valid_attributes:
            plt.plot(df["frame"], normalized_df[attribute], label=attribute, linestyle="-", marker="o", alpha=0.8)

        # Labels and title
        plt.xlabel("Frame (Time Step)")
        plt.ylabel("Normalized Value (0 to 1)")
        plt.title("Simulation Statistics Over Time (Normalized for Comparison)")
        plt.legend()
        plt.grid(True)

        # Show the plot
        plt.show()

    except Exception as e:
        print(f"Error reading CSV file: {e}")
        
        
def plot_multiple_attributes(csv_filename, attributes):
    """
    Reads the simulation CSV file and plots multiple attributes over time in separate charts.

    Parameters:
    - csv_filename: The name of the CSV file generated from the simulation.
    - attributes: A list of column names to plot.
    """
    try:
        # Load CSV data
        df = pd.read_csv(csv_filename)

        # Validate attributes
        available_attributes = df.columns.tolist()
        valid_attributes = [attr for attr in attributes if attr in available_attributes]
        invalid_attributes = [attr for attr in attributes if attr not in available_attributes]

        if invalid_attributes:
            print(f"Warning: These attributes were not found and will be skipped: {invalid_attributes}")

        if not valid_attributes:
            print("No valid attributes selected. Available columns:", available_attributes)
            return

        # Plot each valid attribute separately
        for attribute in valid_attributes:
            plt.figure(figsize=(10, 5))
            plt.plot(df["frame"], df[attribute], label=attribute, linestyle="-", marker="o")

            # Labels and title
            plt.xlabel("Frame (Time Step)")
            plt.ylabel(attribute.replace("_", " ").title())  # Make label readable
            plt.title(f"{attribute.replace('_', ' ').title()} Over Time")
            plt.legend()
            plt.grid(True)

            # Show the plot for each attribute
            plt.show()

    except Exception as e:
        print(f"Error reading CSV file: {e}")