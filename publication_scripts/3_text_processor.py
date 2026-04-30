import re
import os

def process_markdown(input_file, output_file):
    with open(input_file, 'r') as f:
        content = f.read()

    # YAML front matter to be added
    front_matter = """---
layout: article
volume: 
categories: 
title: ""
author: ""
short-name: ""
abstract: ""
sections:  
    - header: 
        text: > 
          
        id: ""
author-info: ""
permalink: 
---
"""

    # Pattern replacement to replace example locations with include statements
    pattern1 = r"(?m)^\*\*Example (\d+[a-z]?)\*\*\s*[.:]?\s+(.+)$"
    replacement1 = r"{% include figure_grid.html columns=1 figure_key='figure_\1' %}"

    # Pattern replacement to replace in-paragraph example indications with anchors. 
    pattern2 = r"\[Example (\d+[a-z]?)]{.underline}"
    replacement2 = r"[Example \1](#ex-\1)"

    # Pattern to find footnotes and replace them with include statements
    pattern3 = r"\[\^(.*?)\]"
    replacement3 = r"{% assign author_key = page.short-name %}{% assign footnote_text = site.data[author_key].footnote_\1 %}{% include footnote.html footnote_number='\1' footnote_text=footnote_text %}"
    
    # Pattern to find and replace sharps, flats, naturals
    sharp = r"ƒ"
    replacement_sharp = "<span style=\"font-family: music;\">&#x266F;</span>"
    natural = r"∂"
    replacement_natural = "<span style=\"font-family: music;\">&#x266E;</span>"
    flat = r"ß"
    replacement_flat = "<span style=\"font-family: music;\">&#x266D;</span>"

    # Pre-process: accidental inside scale degree notation (\^ƒ4 → ƒ\^4)
    # Must run before accidental and scale degree processing
    accidental_in_sd = r"\\\^([ƒß∂])(\d)"
    def swap_accidental_in_sd(m):
        return m.group(1) + "\\^" + m.group(2)

    # Pre-process: Roman numeral followed by accidental (IIIƒ → ƒIII)
    # Swaps order so accidental displays conventionally before the numeral
    roman_accidental = r"([IVX]+)([ƒß∂])"
    roman_accidental_replacement = r"\2\1"

    # Pattern to find and replace scale degrees
    # Patterns match the full \^N sequence (backslash-caret-digit) from authors
    s_d_1 = r"\\\^1"
    replacement_s_d_1 = "<span style=\"font-family: music;\">&#xEF00;</span>"
    s_d_2 = r"\\\^2"
    replacement_s_d_2 = "<span style=\"font-family: music;\">&#xEF01;</span>"
    s_d_3 = r"\\\^3"
    replacement_s_d_3 = "<span style=\"font-family: music;\">&#xEF02;</span>"
    s_d_4 = r"\\\^4"
    replacement_s_d_4 = "<span style=\"font-family: music;\">&#xEF03;</span>"
    s_d_5 = r"\\\^5"
    replacement_s_d_5 = "<span style=\"font-family: music;\">&#xEF04;</span>"
    s_d_6 = r"\\\^6"
    replacement_s_d_6 = "<span style=\"font-family: music;\">&#xEF05;</span>"
    s_d_7 = r"\\\^7"
    replacement_s_d_7 = "<span style=\"font-family: music;\">&#xEF06;</span>"
    s_d_8 = r"\\\^8"
    replacement_s_d_8 = "<span style=\"font-family: music;\">&#xEF07;</span>"
    s_d_9 = r"\\\^9"
    replacement_s_d_9 = "<span style=\"font-family: music;\">&#xEF08;</span>"


    # Figured Bass
    figured_bass = r"\^\^(\d+)\^\^"
    figured_bass_replacement = r"<sup>\1</sup>"
    
    # Subscripts
    subscript = r"~(\d+)~"
    subscript_replacement = r"<sub>\1</sub>"
    
    # Headings
    section_heading = r"##\s+([^\n(]+)\s*(?:\(([^)]+)\))?\n"
    replacement_heading = lambda m: f"</section>\n\n<section markdown=\"1\">\n<h2 id='{m.group(1).lower().replace(' ', '-')}'>{m.group(1)}</h2>\n" 
    section_subheading = r"###\s+([^\n(]+)\s*(?:\(([^)]+)\))?\n"
    replacement_subheading = lambda m: f"<h3 id='{m.group(1).lower().replace(' ', '-')}'>{m.group(1)}</h3>\n" 

    # Perform the replacements in the correct order
    new_content = re.sub(pattern2, replacement2, content, flags=re.DOTALL)
    new_content = re.sub(pattern1, replacement1, new_content)
    new_content = re.sub(pattern3, replacement3, new_content)
    # Pre-process notation order issues before converting individual symbols
    new_content = re.sub(accidental_in_sd, swap_accidental_in_sd, new_content)
    new_content = re.sub(roman_accidental, roman_accidental_replacement, new_content)
    new_content = re.sub(sharp, replacement_sharp, new_content)
    new_content = re.sub(flat, replacement_flat, new_content)
    new_content = re.sub(natural, replacement_natural, new_content)
    new_content = re.sub(s_d_1, replacement_s_d_1, new_content)
    new_content = re.sub(s_d_2, replacement_s_d_2, new_content)
    new_content = re.sub(s_d_3, replacement_s_d_3, new_content)
    new_content = re.sub(s_d_4, replacement_s_d_4, new_content)
    new_content = re.sub(s_d_5, replacement_s_d_5, new_content)
    new_content = re.sub(s_d_6, replacement_s_d_6, new_content)
    new_content = re.sub(s_d_7, replacement_s_d_7, new_content)
    new_content = re.sub(s_d_8, replacement_s_d_8, new_content)
    new_content = re.sub(s_d_9, replacement_s_d_9, new_content)
    new_content = re.sub(figured_bass, figured_bass_replacement, new_content)
    new_content = re.sub(subscript, subscript_replacement, new_content)
    new_content = re.sub(section_subheading, replacement_subheading, new_content)
    new_content = re.sub(section_heading, replacement_heading, new_content)
   
    # Prepend the YAML front matter to the new content
    new_content = front_matter + new_content

   
    # Write the modified content to the output file
    with open(output_file, 'w') as f:
        f.write(new_content)

def process_all_md_in_directory(input_directory, output_directory):
    """
    Processes all markdown files in the given directory and saves the result as processed markdown files.
    
    Args:
        input_directory: The directory where the markdown files are stored.
        output_directory: The directory where the processed markdown files will be saved.
    """
    # Ensure output directory exists
    os.makedirs(output_directory, exist_ok=True)
    
    # List all files in the input directory
    for filename in os.listdir(input_directory):
        # Process only markdown files
        if filename.endswith('.md'):
            input_file = os.path.join(input_directory, filename)
            
            # Modify the filename to add '_processed' before the extension
            base_filename = os.path.splitext(filename)[0]  # Get the base name without extension
            output_file = f"{base_filename}_processed.md"  # Add '_processed' to the filename
            output_file = os.path.join(output_directory, output_file)  # Save in the output directory
            
            # Call the function to process each markdown file
            process_markdown(input_file, output_file)

if __name__ == "__main__":
    input_directory = './raw_md'  # The directory containing the markdown files in the 'raw_md' subfolder
    output_directory = './processed_md'  # The directory where the processed markdown files will be saved
    
    # Process all markdown files in the raw_md directory and save the processed files in the processed_md directory
    process_all_md_in_directory(input_directory, output_directory)