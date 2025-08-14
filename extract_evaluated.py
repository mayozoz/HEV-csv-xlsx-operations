import pandas as pd
import sys
import os

'''
- extract from raw xlsx file
- compute best model
- convert to:
    1. new ref (txt) file setting the highest score as the ref
    2 (??). training file with json data in format [src, mt, ref, score]
'''
MODEL_COLUMNS = ['模型A', '模型B', '模型C', '模型D']
SCORE_COLUMS = ['模型A得分', '模型B得分', '模型C得分', '模型D得分']
THRESHOLD = float(0)


def find_left_of_max(df, row):
    """Finds highest scored mt. Otherwise returns None."""

    max_col = None
    max_val = -float('inf')

    for col in SCORE_COLUMS:
        if row[col] > max_val:
            max_va
            max_col = col

    col_idx = df.columns.get_loc(max_col)
    # print(f"over threshold = {}")
    return row[df.columns[col_idx]] if max_val > THRESHOLD else None


def extract_col(infile, outfile):
    """Extract the human annotated scores for a model."""
    col = '1.7-15000'

    df = pd.read_csv(infile)
    with open(outfile, 'w', encoding='utf-8') as f:
        for _, row in df.iterrows():
            # f.write(f"{float(row[col]):.1f}\n")
            f.write(f"{row[col]}\n")

def extract_file(infile, outfile):
    """Processes infile and writes highest scored cells to outfile."""

    df = pd.read_csv(infile)
    # print(df.head())
    highest_scored_lines = []

    for i, row in df.iterrows():
        highest_scored_line = find_left_of_max(df, row)
        if highest_scored_line is None:
            print(f"Error: row {i-1} has an invalid score below the THRESHOLD={THRESHOLD}")
            highest_scored_lines.append("#ERROR#")
        else:
            highest_scored_lines.append(highest_scored_line)
    
    # write to out file
    with open(outfile, 'w+', encoding='utf-8') as f:
        for line in highest_scored_lines:
            f.write(f"{line}\n")


def compute_best_model(infile, outfile):
    """Process infile and determines the model with best output."""
    df = pd.read_csv(infile)
    sums = {model: 0.0 for model in MODEL_COLUMNS}
    counts = {model: 0 for model in MODEL_COLUMNS}
    highs = {model: 0.0 for model in MODEL_COLUMNS}
    lows = {model: 5.0 for model in MODEL_COLUMNS}

    for i, row in df.iterrows():
        is_row_valid = True
        for model, score_col in zip(MODEL_COLUMNS, SCORE_COLUMS):
            try:
                score = float(row[score_col])
                if pd.isna(score): # if NaN
                    is_row_valid = False
                    break
                sums[model] += score
                counts[model] += 1
                if score > highs[model]:
                    highs[model] = score
                if score < lows[model]:
                    lows[model] = score
            except (ValueError, TypeError):
                print(f"ERROR in line {i}.")
                is_row_valid = False
                continue
    
    avg_scores = {model: sums[model]/counts[model] if counts[model] > 0 else 0
                  for model in MODEL_COLUMNS}
    percent_scores = {model: (sums[model] - 200)/800 for model in MODEL_COLUMNS}

    best_model = max(avg_scores.items(), key=lambda x: x[1])
    ranked_models = sorted(
        avg_scores.items(),
        key=lambda x: x[1],
        reverse = True
    )

    output_lines = [
        "Model Performance Ranking (Best to Worst):",
        "----------------------------------------",
        *[f"{i+1}. {model}: Avg Score = {score:.2f}, "
          f"Percent Score = {percent_scores[model]}\n"
          f"\t(Total={sums[model]:.2f}, "
          f"Count={counts[model]}, High={highs[model]}, Low={lows[model]})" 
          for i, (model, score) in enumerate(ranked_models)],
    ]

    with open(outfile, 'w+', encoding='utf-8') as f:
        f.write("\n".join(output_lines))

    return best_model[0]


if __name__ == "__main__":
    infile, outfile = sys.argv[1:]

    if not os.path.exists(infile):
        print(f"Error: file missing.")
    else:
        # extract_file(infile, outfile)
        os.makedirs(os.path.dirname(outfile), exist_ok=True)  # Create parent dirs if needed
        if not os.path.exists(outfile):
            open(outfile, 'w').close()

        # compute_best_model(infile, outfile)
        # extract_ref(infile, outfile)
        extract_col(infile, outfile)