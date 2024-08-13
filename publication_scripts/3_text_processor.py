import re

def process_markdown(input_file, output_file):
    with open(input_file, 'r') as f:
        content = f.read()

    # YAML front matter to be added
    front_matter = """---
layout: article
volume: 
title: ""
author: ""
short-name: ""
abstract: >
sections:  
    - header: 
        text: ""
        id: ""
---
"""

    # Pattern replacement to replace example locations with includes statments
    pattern1 = r"(?m)^\*\*Example (\d+[a-z]?)\*\*\s*[.:]?\s+(.+)$"
    replacement1 = r"{% include figure_grid.html columns=1 figure_key='figure_\1' %}"

    # Pattern replacement to replace in-paragraph example indications with anchors. 
    pattern2 = r"\[Example (\d+[a-z]?)]{.underline}"
    replacement2 = r"[Example \1](#ex-\1)"

    # Pattern to find footnotes and replace them with includes statements
    pattern3 = r"\[\^(.*)\]"
    replacement3 = r"{% include footnote.html footnote_number='\1' footnote_text=site.data[page.short-name].footnote_\1 %}"
    
    # Pattern to find and replace sharps, flats, naturals
    sharp = r"ƒ"
    replacement_sharp = "<span style=\"font-family: music;\">&#x266F;</span>" 
    natural = r"∂"
    replacement_natural = "<span style=\"font-family: music;\">&#x266E;</span>" 
    flat = r"ß"
    replacement_flat = "<span style=\"font-family: music;\">&#x266D;</span>" 

    # Pattern to find and replace scale degrees
    s_d_1 = r"\^1"
    replacement_s_d_1 = "<span style=\"font-family: music;\">&#xEF00;</span>"
    s_d_2 = r"\^2"
    replacement_s_d_2 = "<span style=\"font-family: music;\">&#xEF01;</span>"
    s_d_3 = r"\^3"
    replacement_s_d_3 = "<span style=\"font-family: music;\">&#xEF02;</span>"
    s_d_4 = r"\^4"
    replacement_s_d_4 = "<span style=\"font-family: music;\">&#xEF03;</span>"
    s_d_5 = r"\^5"
    replacement_s_d_5 = "<span style=\"font-family: music;\">&#xEF04;</span>"
    s_d_6 = r"\^6"
    replacement_s_d_6 = "<span style=\"font-family: music;\">&#xEF05;</span>"
    s_d_7 = r"\^7"
    replacement_s_d_7 = "<span style=\"font-family: music;\">&#xEF06;</span>"
    s_d_8 = r"\^8"
    replacement_s_d_8 = "<span style=\"font-family: music;\">&#xEF07;</span>"
    s_d_9 = r"\^9"
    replacement_s_d_9 = "<span style=\"font-family: music;\">&#xEF08;</span>"


    #Figured Bass
    figured_bass = r"\^\^(\d+)\^\^"
    figured_bass_replacement = r"<sup>\1</sup>"
    
    #Subscripts
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
    new_content = re.sub(sharp, replacement_sharp, new_content)
    new_content = re.sub(flat, replacement_flat, new_content)
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

if __name__ == "__main__":
    input_file = "mckay.md"
    output_file = "mckay_processed.md"
    process_markdown(input_file, output_file)


