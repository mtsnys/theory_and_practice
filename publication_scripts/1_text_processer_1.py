import re

def extract_and_combine(markdown_file, output_file):
    """
    Extracts footnotes, citations, and figure captions from a Markdown file
    and combines them into a single output document.

    Args:
        markdown_file: The path to the Markdown file.
        output_file: The path to the output file where the combined content will be saved.
    """

    with open(markdown_file, 'r') as f:
        markdown_text = f.read()

    # Extract footnotes
    footnotes = re.findall(r'\[\^.+?\]:.+', markdown_text)

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
    figure_caption_pattern = r"(?m)^\*\*Example \d+[a-z]?\*\*\s*[.:]?\s+.*$"
    figure_captions = re.findall(figure_caption_pattern, markdown_text)

    # Combine the extracted elements into a single string (excluding the main text)
    combined_content = ""
    if footnotes:
        combined_content += "## Footnotes\n\n" + '\n'.join(footnotes) + "\n\n"
    if figure_captions:
        combined_content += "## Figure Captions\n\n" + '\n'.join(figure_captions) + "\n\n"
    if citations:
        combined_content += "## Works Cited\n\n" + '\n'.join(citations)

    # Save the combined content to the output file
    with open(output_file, 'w') as f:
        f.write(combined_content)

    print("Footnotes, citations, and figure captions extracted and combined successfully!")

# Example usage
markdown_file = 'mckay.md'  # Author's markdown file here.
output_file = 'captions_citations_footnotes_pre_yaml.md'  # Replace with your desired output file name

extract_and_combine(markdown_file, output_file)


