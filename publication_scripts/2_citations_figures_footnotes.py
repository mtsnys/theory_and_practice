import re
import yaml
import os

def process_md_to_yaml(md_file_path, yaml_file_path):
    """
    Processes a markdown file and converts the citations, footnotes, and figure captions into YAML format.
    """
    with open(md_file_path, 'r') as md_file:
        md_content = md_file.read()
        
    # Citations
    pattern1 = r"^\d+\.\s+(([^,]+),\s+((?:\w+\s+)*\w+\.?)\s+(\d{4})\.\s+(.*))$"
    md_content = re.sub(pattern1, r"- name: \2_\4\n  citation: >\n    \1", md_content, flags=re.MULTILINE)

    # Footnotes
    pattern2 = r"(?m)^\[\^(\d+)\]:\s*(.+)$"
    md_content = re.sub(pattern2, r"footnote_\1: >\n  \2", md_content)

    # Figure Captions
    pattern3 = r"(?m)^\*\*Example (\d+[a-z]?)\*\*\s*[.:]?\s+(.+)$"
    md_content = re.sub(pattern3, r"figure_\1:\n  main_number: \n  main_caption:    \n  figures:\n    - figure:\n        number: '\1'\n        caption: >\n          \2\n        url: 'assets/articles/*******/img/ex_\1.png'\n        alt: 'Test'\n        border: false\n        scale: 1", md_content)

    # Print the intermediate content for debugging (optional)
    print(md_content)

    # Write to YAML file without re-parsing
    with open(yaml_file_path, 'w') as yaml_file:
        yaml_file.write(md_content)


def process_all_md_in_directory(input_directory, output_directory):
    """
    Processes all markdown files in the given directory and saves the result as YAML files in the output directory.
    
    Args:
        input_directory: The directory where the markdown files are stored.
        output_directory: The directory where the processed YAML files will be saved.
    """
    # Ensure output directory exists
    os.makedirs(output_directory, exist_ok=True)
    
    # List all files in the input directory
    for filename in os.listdir(input_directory):
        # Process only markdown files
        if filename.endswith('.md'):
            md_file_path = os.path.join(input_directory, filename)
            
            # Modify the filename to add '_stepone' before the extension
            base_filename = os.path.splitext(filename)[0]  # Get the base name without extension
            yaml_file_path = f"{base_filename}_stepone.yaml"  # Add '_stepone' to the filename
            yaml_file_path = os.path.join(output_directory, yaml_file_path)  # Save in the output directory
            
            # Call the function to process each markdown file
            process_md_to_yaml(md_file_path, yaml_file_path)


if __name__ == "__main__":
    input_directory = './step_one'  # The directory containing the markdown files in the 'step_one' subfolder
    output_directory = './step_two'  # The directory where the processed YAML files will be saved
    
    # Process all markdown files in the step_one directory and save the YAML files in the step_two directory
    process_all_md_in_directory(input_directory, output_directory)