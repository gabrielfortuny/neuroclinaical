from PIL import Image, ImageDraw
from datetime import datetime
import matplotlib.pyplot as plt
from app.models import Patient
import numpy as np
from collections import defaultdict
from matplotlib.ticker import MaxNLocator
import matplotlib.patches as mpatches
from app.models import Patient, DrugAdministration
from io import BytesIO


def fetch_graph_data(patient_id):
    patient = Patient.query.get(patient_id)
    if not patient:
        return [], []

    # Import psycopg2 for direct database access
    import psycopg2
    import psycopg2.extras

    # Get database connection parameters from the environment
    host = "db"  # Container name from docker-compose
    port = 5432  # Default PostgreSQL port
    user = "admin"
    password = "dpSVtoZUjmyXAXWo6LfLe3NgzZQHPqvt3POhmMPTU2U"
    database = "database"

    # Create direct connection to PostgreSQL
    conn = psycopg2.connect(
        host=host, port=port, user=user, password=password, database=database
    )
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Get drug administrations with drug information - removed the time column
    cursor.execute(
        """
        SELECT
            da.id, 
            d.name AS drug_name, 
            d.drug_class, 
            da.day, 
            da.dosage,
            da.time
        FROM 
            drug_administration da
        WHERE 
            da.patient_id = %s
        ORDER BY 
            da.day ASC
    """,
        (patient_id,),
    )

    # Fetch all results
    drugs = cursor.fetchall()

    # Convert to list of dictionaries for JSON response
    result = []
    for drug in drugs:
        drug_data = {
            "id": drug["id"],
            "name": drug["drug_name"],
            "day": drug["day"],
            "mg_administered": drug["dosage"],
            "time": drug["time"],
        }
        result.append(drug_data)

    # Close the database connection
    cursor.close()
    conn.close()

    data = []
    for seizure in patient.seizures:
        seizure_data = {
            "id": seizure.id,
            "day": seizure.day,
            "seizure_time": (
                seizure.start_time.strftime("%H:%M:%S") if seizure.start_time else None
            ),
            "duration": seizure.duration,  # Already in ISO 8601 format
            "electrodes": [electrode.name for electrode in seizure.electrodes],
        }
        data.append(seizure_data)
    return result, data


def make_plot2(
    patient_id: int,
    screen: int,
    view_seizure_length: int,
    view_soz_heatmap: int,
    view_drug_admin: int,
) -> Image.Image:
    """
    Generate a plot based on the specified screen and optional views.

    Parameters:
    - screen: int, the screen to display (1, 2, or 3)
    - view_seizure_length: int, whether to show seizure length representation (0 or 1)
    - view_soz_heatmap: int, whether to show seizure onset zone heatmap (0 or 1)
    - view_drug_admin: int, whether to show drug administration bars (0 or 1)

    Returns:
    - Image.Image, the generated plot as an image
    """
    current_app.logger.info(f"data one {data1}")
    current_app.logger.info(f"data two {data2}")
    data1, data2 = fetch_graph_data(patient_id)
    
    # TODO: Only do code below this, code above is needed, only replace below
    # Create a blank image
    img = Image.new("RGB", (800, 600), color="white")
    draw = ImageDraw.Draw(img)

    # Data for seizures and drug administration
    seizures = data2
    drugs = data1
    max_m = max(drugs, key=lambda x: int(x["mg_administered"]))
    max_mg = int(max_m["mg_administered"])

    # Calculate the range of days in the data
    seizure_days = [seizure["day"] for seizure in seizures]
    max_day = max(seizure_days) if seizure_days else 1  # Default to 1 if no seizures
    all_days = range(1, max_day + 1)  # Always start from Day 1

    # Set figure size and font sizes for iPhone 16 screen
    plt.rcParams.update({"font.size": 12})
    figsize = (4, 6)  # Adjusted figure size for iPhone 16 screen

    if screen == 1:
        # Group seizures by day
        day_to_seizures = defaultdict(list)
        for seizure in seizures:
            day_to_seizures[seizure["day"]].append(seizure)

        # Create a stacked bar plot
        plt.figure(figsize=figsize)
        bottoms = [0] * len(all_days)  # Initialize bottoms for stacking
        bar_color = "skyblue"  # Set a uniform color for the bars
        edge_color = "black"  # Set the color of the outline

        if view_seizure_length == 0:
            seizure_counts = [len(day_to_seizures[day]) for day in all_days]
            plt.bar(all_days, seizure_counts, color="blue", label="Number of Seizures")
            plt.xlabel("Day", fontsize=14)
            plt.ylabel("Number of Seizures", fontsize=14)
            plt.title("Seizure Count by Day", fontsize=12)
            plt.xticks(all_days, fontsize=12)
            plt.yticks(fontsize=12)
            plt.gca().yaxis.set_major_locator(
                MaxNLocator(integer=True)
            )  # Ensure y-ticks are integers
            plt.tight_layout()
            plt.savefig("plot.png")  # Saves as PNG
            plt.close()

        if view_seizure_length == 1:
            for i, day in enumerate(all_days):
                lengths = [s["duration"] for s in day_to_seizures[day]]
                for j, length in enumerate(lengths):
                    plt.bar(
                        day,
                        length,
                        bottom=bottoms[i],
                        label=f"Seizure {j+1}" if i == 0 else "",
                        color=bar_color,
                        edgecolor=edge_color,
                        linewidth=1.5,
                    )
                    bottoms[i] += length  # Update the bottom for the next seizure

            plt.xlabel("Day", fontsize=14)
            plt.ylabel("Seizure Length (seconds)", fontsize=14)
            plt.title("Seizure Count and Lengths by Day", fontsize=12)
            plt.xticks(all_days, fontsize=12)
            plt.yticks(fontsize=12)
            plt.tight_layout()
            plt.savefig("plot.png")  # Saves as PNG
            plt.close()

    if screen == 2:
        # Group seizures by day
        figsize = (6, 4)
        day_to_seizures = defaultdict(list)
        for seizure in seizures:
            day_to_seizures[seizure["day"]].append(seizure)

        plt.figure(figsize=figsize)

        # Normalize time to a 24-hour timeline for each day
        xticks = []  # X-axis tick positions
        xtick_labels = []  # X-axis tick labels
        label_positions = []  # To store the positions of the labels

        for day in all_days:
            day_seizures = day_to_seizures[day]
            for i, seizure in enumerate(day_seizures):
                seizure_time = datetime.strptime(
                    seizure["seizure_time"], "%H:%M:%S"
                ).time()
                x_value = (
                    (day - 1) * 24
                    + seizure_time.hour
                    + seizure_time.minute / 60
                    + seizure_time.second / 3600
                )
                # Offset bars horizontally if multiple seizures occur at the same time

                # Add seizure time to x-axis ticks and labels
                xticks.append(x_value)
                xtick_labels.append(
                    seizure_time.strftime("%H:%M")
                )  # Only show time, not day
                label_positions.append(x_value)

                plt.bar(
                    x_value,  # X-axis: normalized time across days with offset
                    seizure["duration"],  # Y-axis: duration
                    width=2,  # Width of bars
                    color="blue",  # Same color for all bars
                    align="center",
                    label=(
                        "Seizure Duration"
                        if day == 1 and seizure == day_seizures[0]
                        else ""
                    ),  # Add label only once
                )

        # Adjust x-axis labels to prevent overlap
        adjusted_xticks = []
        adjusted_xtick_labels = []
        for i, (tick, label) in enumerate(zip(xticks, xtick_labels)):
            if (
                abs(xticks[i] - xticks[i - 1]) < max(xticks) / 10
            ):  # Check if labels are too close (conflict)
                xticks[i] += (
                    max(xticks) / 30
                )  # Move the current label to the right by a fixed offset (e.g., 1.0 units)

            # Place the label normally
            adjusted_xticks.append(xticks[i])
            adjusted_xtick_labels.append(label)

        # Set x-axis ticks and labels (only non-overlapping labels)
        plt.xticks(
            adjusted_xticks, adjusted_xtick_labels, rotation=45, ha="right", fontsize=8
        )
        plt.xlabel("Time", fontsize=8)
        plt.ylabel("Seizure Duration (seconds)", fontsize=14)
        if view_drug_admin == 0:
            plt.title("Seizure Durations by Time and Day", fontsize=8)

        plt.grid(axis="y", linestyle="--", alpha=0.7)
        for day in all_days:
            day_start = (day - 1) * 24
            plt.axvline(x=day_start, color="red", linestyle="--", linewidth=1)
            # Add day label at the start of each day
            plt.text(
                day_start,
                plt.ylim()[1] * 0.95,
                f"Day {day}",
                color="red",
                ha="right",
                va="top",
                rotation=90,
                fontsize=8,
            )

        # Add a vertical dashed line to mark the end of the last day
        last_day_end = max_day * 24
        plt.axvline(x=last_day_end, color="green", linestyle="--", linewidth=1)
        plt.text(
            last_day_end,
            plt.ylim()[1] * 0.95,
            "End",
            color="green",
            ha="left",
            va="top",
            rotation=90,
            fontsize=12,
        )

        if view_drug_admin == 1:
            # Plot drug administration on a secondary y-axis
            ax2 = plt.twinx()  # Create a secondary y-axis
            unique_drugs = list(
                set(drug["name"] for drug in drugs)
            )  # Get unique drug names
            color_map = plt.colormaps.get_cmap(
                "tab10"
            )  # Use the recommended method to get a colormap

            # Group drugs by time to handle overlapping annotations
            time_to_drugs = []
            legend_patches = []  # To store legend patches for each drug
            for drug in drugs:
                drug_time = datetime.strptime(drug["time"], "%H:%M:%S").time()
                x_value = (
                    (drug["day"] - 1) * 24
                    + drug_time.hour
                    + drug_time.minute / 60
                    + drug_time.second / 3600
                )
                time_to_drugs.append((x_value, drug))

            # Sort the time_to_drugs dictionary by x_value (time)
            sorted_time_to_drugs = sorted(time_to_drugs, key=lambda x: x[0])

            # Initialize variables for tracking previous values
            prevXval = -float(
                "inf"
            )  # Initialize to negative infinity to ensure the first x_value is always larger
            prevYval = -float(
                "inf"
            )  # Initialize to negative infinity to ensure the first y_value is always larger
            prevPos = 0  # Initialize vertical offset for annotations
            max_drug = 0  # Track the maximum drug dosage for offset calculations
            prevXpos = 0  # Initialize previous x_value for offset calculations
            # Iterate through sorted x_values and drugs_at_time
            for drugs in sorted_time_to_drugs:
                x_value, drug = drugs  # Unpack the tuple

                drug_time = datetime.strptime(drug["time"], "%H:%M:%S").time()
                x_value = (
                    (drug["day"] - 1) * 24
                    + drug_time.hour
                    + drug_time.minute / 60
                    + drug_time.second / 3600
                )
                # Check if labels are too close (conflict)

                drug_index = unique_drugs.index(
                    drug["name"]
                )  # Get index for color mapping

                # Plot the scatter point

                # Update max_drug if the current dosage is higher
                if int(drug["mg_administered"]) > max_drug:
                    max_drug = int(drug["mg_administered"])

                if (abs(int(drug["mg_administered"]) - prevYval) < (max_mg / 10)) and (
                    abs(x_value - prevXval) < max(xticks) / 4
                ):
                    pos = (
                        max_mg / 15
                    ) + prevPos  # Add vertical offset if labels are too close
                    prevPos = pos

                    x_value = prevXpos + max(xticks) / 100
                    prevXpos = x_value
                else:
                    pos = (
                        int(drug["mg_administered"]) + max_mg / 20
                    )  # Default vertical offset
                    prevPos = pos
                    prevXpos = x_value

                prevYval = int(drug["mg_administered"])  # Update previous y_value
                prevXval = (
                    (drug["day"] - 1) * 24
                    + drug_time.hour
                    + drug_time.minute / 60
                    + drug_time.second / 3600
                )  # Update previous x_value

                # Add drug name as annotation with vertical offset
                ax2.scatter(
                    x_value,  # X-axis: normalized time across days
                    int(drug["mg_administered"]),  # Y-axis: drug dosage
                    color=color_map(
                        drug_index / len(unique_drugs)
                    ),  # Assign unique color
                )
                """
                ax2.text(
                    x_value,  # X-axis position
                    pos,  # Y-axis position (offset vertically)
                    drug['name'],  # Drug name
                    color=color_map(drug_index / len(unique_drugs)),  # Use the same color as the point
                    fontsize=10,
                    ha='center'
                )
                """

            ax2.set_ylabel("Drug Dosage (mg)", fontsize=14)
            ax2.set_ylim(0, max_drug + 200)
            plt.title(
                "Seizure Durations and Drug Administration by Time and Day", fontsize=9
            )
            for drug in unique_drugs:

                drug_index = unique_drugs.index(drug)

                legend_patches.append(
                    mpatches.Patch(
                        color=color_map(drug_index / len(unique_drugs)), label=drug
                    )
                )  # Add to legend

                # Add custom legend

            ax2.legend(
                handles=legend_patches,
                title="Drugs",
                loc="upper left",  # Position legend at the upper left
                bbox_to_anchor=(0, 1.35),  # Shift the legend to the left of the graph
                fontsize=6,
                ncol=len(unique_drugs),
            )

        plt.tight_layout()
        plt.savefig("plot.png")  # Saves as PNG
        plt.close()

    if screen == 3:
        # Screen 3: Seizure onset electrodes by seizure
        electrodes = set()
        for seizure in seizures:
            electrodes.update(seizure["electrodes"])
        electrodes = sorted(list(electrodes))

        # Count the number of seizures per electrode
        electrode_counts = defaultdict(int)
        for seizure in seizures:
            for electrode in seizure["electrodes"]:
                electrode_counts[electrode] += 1

        # Prepare data for the bar graph
        electrode_names = list(electrodes)
        seizure_counts = [electrode_counts[electrode] for electrode in electrode_names]

        # Create the bar graph
        plt.figure(figsize=figsize)
        plt.bar(electrode_names, seizure_counts, color="skyblue")
        plt.xlabel("Electrodes", fontsize=14)
        plt.ylabel("Number of Seizures", fontsize=14)
        plt.title("Number of Seizures per Seizure Onset Electrode", fontsize=10)
        plt.xticks(
            rotation=45, ha="right", fontsize=12
        )  # Rotate x-axis labels for better readability
        plt.yticks(fontsize=12)
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.gca().yaxis.set_major_locator(
            MaxNLocator(integer=True)
        )  # Ensure y-ticks are integers
        plt.tight_layout()

        plt.savefig("plot.png")  # Saves as PNG
        plt.close()

    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return Image.open(buf)
