import re
import os

def extract_and_reformat_footnotes(markdown_text):
    """
    Extracts footnotes from a Markdown document, reformats them, and returns the result.

    Args:
        markdown_text (str): The Markdown text containing footnotes.

    Returns:
        str: The reformatted footnotes.
    """

    footnote_pattern = re.compile(r"\[\^(\d+)\]:\s+(.*?)(?=\n\[\^\d+\]:|\Z)", re.DOTALL)
    footnotes = footnote_pattern.findall(markdown_text)

    reformatted_footnotes = ""
    for number, content in footnotes:
        content = content.strip().replace("\n    ", " ").replace("\n", " ")  # Replace newlines with spaces
        reformatted_footnotes += f"footnote_{number}: >\n  {content}\n" #Remove extra newline

    return reformatted_footnotes.strip()

def process_markdown_files(directory):
    """
    Processes all Markdown files in the given directory.

    Args:
        directory (str): The directory containing Markdown files.
    """

    for filename in os.listdir(directory):
        if filename.endswith(".md"):
            filepath = os.path.join(directory, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                markdown_content = f.read()

            reformatted_output = extract_and_reformat_footnotes(markdown_content)

            output_filename = os.path.splitext(filename)[0] + "_footnotes_formatted.txt"
            output_filepath = os.path.join(directory, output_filename)

            with open(output_filepath, "w", encoding="utf-8") as f:
                f.write(reformatted_output)

            print(f"Footnotes extracted from {filename} and saved to {output_filename}")

# Get the directory of the current script
script_directory = os.path.dirname(os.path.abspath(__file__))

# Process all Markdown files in the script's directory
process_markdown_files(script_directory)