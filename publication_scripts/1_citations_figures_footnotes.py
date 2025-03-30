import re
import os

def extract_and_combine(markdown_file, output_file):
    """
    Extracts footnotes, citations, and figure captions from a Markdown file
    and combines them into a single output document.

    Args:
        markdown_file: The path to the Markdown file.
        output_file: The path to the output file where the combined content will be saved.
    """

    with open(markdown_file, 'r', encoding='utf-8') as f:
        markdown_text = f.read()

    # Extract footnotes (allowing multi-line footnotes)
    footnote_pattern = r'(?m)^\[\^(\d+)\]:\s*(.+(?:\n\s+.+)*)'
    footnotes = re.findall(footnote_pattern, markdown_text)
    footnotes = [f"[^{num}]: {text.strip()}" for num, text in footnotes]

    # Extract citations
    citation_pattern = r"(?m)^## Works Cited\n([\s\S]*)$"
    match = re.search(citation_pattern, markdown_text)
    if match:
        citations_section = match.group(1)
        citation_pattern = r"(?m)^\d+\.\s+.*$"
        citations = re.findall(citation_pattern, citations_section)
    else:
        citations = []

    # Extract figure captions
    figure_caption_pattern = r"^\*\*Example (\d+[a-z]?)\*\*\s+([\s\S]+?)(?=\n\s*\n|$)"
    figure_captions = re.findall(figure_caption_pattern, markdown_text, re.MULTILINE)
    figure_captions = [f"**Example {num}**: {caption}" for num, caption in figure_captions]

    # Debug: Print what was captured
    print("DEBUG: Figure Captions Found:", figure_captions)

    # Combine the extracted elements into a single string (excluding the main text)
    combined_content = ""
    if footnotes:
        combined_content += "## Footnotes\n\n" + '\n'.join(footnotes) + "\n\n"
    if figure_captions:
        combined_content += "## Figure Captions\n\n" + '\n'.join(figure_captions) + "\n\n"
    if citations:
        combined_content += "## Works Cited\n\n" + '\n'.join(citations)

    # Save the combined content to the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(combined_content)

    print(f"Footnotes, citations, and figure captions extracted and combined for {markdown_file}!")


def process_all_markdown_files(input_directory, output_directory):
    """
    Process all markdown files in the given directory and save combined results.
    
    Args:
        input_directory: The directory where the markdown files are stored.
        output_directory: The directory where the output files will be saved.
    """
    # List all files in the input directory
    for filename in os.listdir(input_directory):
        # Process only markdown files
        if filename.endswith('.md'):
            markdown_file = os.path.join(input_directory, filename)
            
            # Modify the filename to add '_stepone' before the extension
            base_filename = os.path.splitext(filename)[0]  # Get the base name without extension
            output_filename = f"{base_filename}_stepone.md"  # Add '_stepone' to the filename
            output_file = os.path.join(output_directory, output_filename)
            
            # Call the extraction function for each markdown file
            extract_and_combine(markdown_file, output_file)


# Example usage
input_directory = './raw_md'  # The directory containing the markdown files (subfolder 'raw_md')
output_directory = './step_one'  # The directory where you want to save the combined files

# Ensure the output directory exists
os.makedirs(output_directory, exist_ok=True)

# Process all markdown files in the input directory
process_all_markdown_files(input_directory, output_directory)