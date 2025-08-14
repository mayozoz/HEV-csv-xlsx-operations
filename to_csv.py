import csv
import os
 
def organize_files_to_csv(src_file, model_a_file, model_b_file, model_c_file, model_d_file, output_file): # , model_d_file
    """
    Organize input files into CSV with specified columns.
    """

    with open(src_file, 'r', encoding='utf-8') as f:
        src_lines = [line.strip() for line in f.readlines()]
 
    with open(model_a_file, 'r', encoding='utf-8') as f:
        model_a_lines = [line.strip() for line in f.readlines()]
    
    with open(model_b_file, 'r', encoding='utf-8') as f:
        model_b_lines = [line.strip() for line in f.readlines()]
    
    with open(model_c_file, 'r', encoding='utf-8') as f:
        model_c_lines = [line.strip() for line in f.readlines()]
    
    with open(model_d_file, 'r', encoding='utf-8') as f:
        model_d_lines = [line.strip() for line in f.readlines()]

    # Verify lengths
    file_lengths = [len(src_lines), len(model_a_lines), len(model_b_lines), 
               len(model_c_lines), len(model_c_lines)]

    if len(set(file_lengths)) > 1:
        print(f"Warning: Files have different lengths: {file_lengths}")
        print("Using the minimum length to avoid index errors.")
    
    min_length = min(file_lengths)

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['ID', '日语原文', 'claude', 'claude得分', 'deepseek-v3', 'deepseek-v3得分', 
                    'doubao-seed-1.6', 'doubao-seed-1.6得分', 'qwen-mt-turbo', 'qwen-mt-turbo得分'] # , '模型D', '模型D得分'
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(min_length):
            row = {
                'ID': i + 1,
                '日语原文': src_lines[i],
                'claude': model_a_lines[i],
                'claude得分': '',  # Empty
                'deepseek-v3': model_b_lines[i],
                'deepseek-v3得分': '',  # Empty
                'doubao-seed-1.6': model_c_lines[i],
                'doubao-seed-1.6得分': '',  # Empty
                'qwen-mt-turbo': model_d_lines[i],
                'qwen-mt-turbo得分': ''   # Empty
            }
            writer.writerow(row)

        print(f"Successfully created {output_file} with {min_length} rows")


if __name__ == "__main__":
    src_file = "/ssd11/other/meiyy02/code_files/jpn-cn-200/src_clean.txt"
    model_a_file = "/ssd11/other/meiyy02/code_files/jpn-cn-200/jpn_Jpan-cn.claude"
    model_b_file = "/ssd11/other/meiyy02/code_files/jpn-cn-200/jpn_Jpan-cn.deepseek-v3"
    model_c_file = "/ssd11/other/meiyy02/code_files/jpn-cn-200/jpn_Jpan-cn.doubao-seed-1.6"
    model_d_file = "/ssd11/other/meiyy02/code_files/jpn-cn-200/jpn_Jpan-cn.qwen-mt-turbo"
    output_file = "/ssd11/other/meiyy02/code_files/jpn-cn-200/jpn_Jpan-cn_200.csv"

    input_files = [src_file, model_a_file, model_b_file, model_c_file, model_d_file]
    missing_files = [f for f in input_files if not os.path.exists(f)]

    if missing_files:
        print(f"Error: The following files are missing: {missing_files}")
        print("Please update the file paths in the script.")
    else:
        organize_files_to_csv(src_file, model_a_file, model_b_file, 
                            model_c_file, model_d_file, output_file)