import yaml
import re

def process_bibliography(text):
    # Look for the 'Bibliography' section and extract everything after it
    bibliography_start = re.search(r'\*\*Bibliography\*\*', text)
    if bibliography_start:
        # Extract the text after **Bibliography**
        bibliography_text = text[bibliography_start.end():]
        
        # Now split the bibliography entries by the pattern of two spaces between entries (or adjust as needed)
        entries = re.split(r'\n\s*\n', bibliography_text.strip())

        # Prepare a list for processed entries
        processed_entries = []

        for entry in entries:
            # Look for a pattern where the citation is wrapped in quotes
            match = re.match(r'(.+?)\s*"(.+)"\s*(.*)', entry)
            if match:
                # Split the entry into the name and citation
                name = match.group(1).strip()
                citation = match.group(2).strip()
                additional_info = match.group(3).strip() if match.group(3) else ''
                
                # Prepare the formatted entry
                processed_entries.append({
                    'name': name,
                    'citation': citation,
                    'additional_info': additional_info
                })

        # Return the YAML formatted bibliography
        return yaml.dump(processed_entries, allow_unicode=True)
    
    return "Bibliography section not found."

# Example usage with your text
text = """
Some content before the bibliography section

**Bibliography**
Benjamin, Richard. "A Theory of Musical Meter." *Music Perception* 1 (4): 355--413.
Berry, Wallace. 1987. *Structural Functions in Music*. New York: Dover.
Campbell, Olive Dame, and Cecil James Sharp. 1917. *English Folk Songs from the Southern Appalachians: Comprising 122 Songs and Ballads, and 323 Tunes*. New York: Putnam and Sons.
Child, Francis James. 1882. *English and Scottish Popular Ballads, Part VII*. Edited by Helen Child Sargent and George Lyman Kittredge. Boston: Houghton Mifflin Co.
...
"""

# Process the text and print the YAML output
output = process_bibliography(text)
print(output)