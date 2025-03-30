import re

# Read input markdown file
with open("input.md", "r", encoding="utf-8") as file:
    content = file.read()

# Extract footnotes
footnote_definitions = {}
footnote_pattern = re.compile(r"\[\^(\d+)\]: (.*)")
content = footnote_pattern.sub(lambda m: footnote_definitions.setdefault(f"footnote_{m.group(1)}", f"  {m.group(2)}") or "", content)

# Replace footnote references
footnote_ref_pattern = re.compile(r"\[\^(\d+)\]")
content = footnote_ref_pattern.sub(
    lambda m: "{% assign author_key = page.short-name %}{% assign footnote_text = site.data[author_key].footnote_"
    + m.group(1)
    + " %}{% include footnote.html footnote_number='"
    + m.group(1)
    + "' footnote_text=footnote_text %}",
    content,
)

# Write output files
with open("output.md", "w", encoding="utf-8") as file:
    file.write(content)

with open("footnotes.yml", "w", encoding="utf-8") as file:
    file.write("\n".join(f"{k}: >\n{v}" for k, v in footnote_definitions.items()))