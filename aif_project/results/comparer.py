import re

def parse_file(filename):
    """
    Parses the input file and returns a dictionary with seed as the key
    and a tuple of total steps and completed missions as the value.
    """
    seed_data = {}
    with open(filename, 'r') as file:
        for line in file:
            match = re.match(r"Seed (\d+): Total Steps = (\d+), Completed Missions = (\d+)", line)
            if match:
                seed = int(match.group(1))
                total_steps = int(match.group(2))
                completed_missions = int(match.group(3))
                seed_data[seed] = (total_steps, completed_missions)
    return seed_data

def compare_files(file1, file2, output_file):
    """
    Compares two files, calculates means, and saves the differences to an output file with aligned columns.
    """
    data1 = parse_file(file1)
    data2 = parse_file(file2)

    headers = [
        "Seed", "OurBot Total Steps", "BabyAI Total Steps", "Difference Steps",
        "OurBot Missions", "BabyAI Missions", "Difference Missions"
    ]
    column_widths = [6, 20, 20, 20, 17, 17, 20]

    def format_row(values):
        return " ".join(f"{value:>{width}}" for value, width in zip(values, column_widths))

    all_seeds = sorted(set(data1.keys()).union(data2.keys()))

    # Collecting statistics for mean calculation
    total_steps1, total_steps2, total_diff_steps = 0, 0, 0
    total_missions1, total_missions2, total_diff_missions = 0, 0, 0
    count = len(all_seeds)

    with open(output_file, 'w') as out_file:
        # Write header
        out_file.write(format_row(headers) + "\n")
        out_file.write("-" * sum(column_widths) + "\n")

        for seed in all_seeds:
            steps1, missions1 = data1.get(seed, (0, 0))
            steps2, missions2 = data2.get(seed, (0, 0))
            diff_steps = steps2 - steps1
            diff_missions = missions2 - missions1

            # Update totals for mean calculation
            total_steps1 += steps1
            total_steps2 += steps2
            total_diff_steps += diff_steps
            total_missions1 += missions1
            total_missions2 += missions2
            total_diff_missions += diff_missions

            row = [
                seed, steps1, steps2, diff_steps,
                missions1, missions2, diff_missions
            ]
            out_file.write(format_row(row) + "\n")

        # Calculate means
        mean_steps1 = total_steps1 / count
        mean_steps2 = total_steps2 / count
        mean_diff_steps = total_diff_steps / count
        mean_missions1 = total_missions1 / count
        mean_missions2 = total_missions2 / count
        mean_diff_missions = total_diff_missions / count

        # Write means to file
        out_file.write("-" * sum(column_widths) + "\n")
        means_row = [
            "Mean", f"{mean_steps1:.2f}", f"{mean_steps2:.2f}", f"{mean_diff_steps:.2f}",
            f"{mean_missions1:.2f}", f"{mean_missions2:.2f}", f"{mean_diff_missions:.2f}"
        ]
        out_file.write(format_row(means_row) + "\n")

# Example usage:
file1 = "OurBot_results_summary.txt"  # Replace with the path to your first file
file2 = "BabyAI_results_summary.txt"  # Replace with the path to your second file
output_file = "comparison_results_with_means.txt"

compare_files(file1, file2, output_file)
print(f"Comparison results with means saved to {output_file}")
