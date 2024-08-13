import re
import yaml

def process_md_to_yaml(md_file_path, yaml_file_path):
    with open(md_file_path, 'r') as md_file:
        md_content = md_file.read()
        
    # Citations
    pattern1 = r"^\d+\.\s+(([^,]+),\s+((?:\w+\s+)*\w+\.?)\s+(\d{4})\.\s+(.*))$"
    yaml_content = re.sub(pattern1, r"- name: \2_\4\n  citation: >\n    \1", md_content, flags=re.MULTILINE)

    # Footnotes
    pattern2 = r"(?m)^\[\^(\d+)\]:\s*(.+)$"
    yaml_content = re.sub(pattern2, r"footnote_\1: >\n  \2", yaml_content)

    # Figure Captions
    pattern3 = r"(?m)^\*\*Example (\d+[a-z]?)\*\*\s*[.:]?\s+(.+)$"
    yaml_content = re.sub(pattern3, r"figure_\1:\n  main_number:\n  main_caption:\n  figures:\n    - figure:\n        number: '\1'\n        caption: >\n          \2\n        url: 'assets/articles/*******/img/ex_\1.png'\n        alt: 'Test'\n        border: false\n        scale: 1", yaml_content)

    # Print the intermediate YAML content for debugging (optional)
    print(yaml_content)

    # Try to convert to YAML, but handle errors gracefully
    try:
        yaml_data = yaml.safe_load(yaml_content)
    except yaml.parser.ParserError as e:
        print(f"Warning: YAML parsing error encountered: {e}")
        yaml_data = None  # Set yaml_data to None to indicate an error

    # Write to YAML file, even if there was an error
    with open(yaml_file_path, 'w') as yaml_file:
        if yaml_data:
            yaml.dump(yaml_data, yaml_file, default_flow_style=False)
        else:
            yaml_file.write(yaml_content)  # Write the raw content if there was an error

if __name__ == "__main__":
    md_file_path = "captions_citations_footnotes_pre_yaml.md"
    yaml_file_path = "captions_citations_footnotes_processed.yaml"
    process_md_to_yaml(md_file_path, yaml_file_path)
    