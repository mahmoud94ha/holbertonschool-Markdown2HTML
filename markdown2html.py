#!/usr/bin/python3
"""Markdown to html converter"""
import sys
import os
import re
import hashlib


def convert_to_md5(string):
    return hashlib.md5(string.encode('utf-8')).hexdigest()


def remove_c(string):
    def replace_c(match):
        return match.group().replace("c", "").replace("C", "")
    string = re.sub(r'\(\([^()]*[Cc][^()]*\)\)', replace_c, string)
    string = re.sub(r'(\(\()|(\)\))', '', string)
    return string


if __name__ == "__main__":

    if len(sys.argv) < 3:
        sys.stderr.write("Usage: ./markdown2html.py README.md README.html\n")
        exit(1)

    file = sys.argv[1]
    out = sys.argv[2]
    bold_re = r"\*\*(.+?)\*\*"
    italic_re = r"__(.+?)__"
    md5_re = re.compile(r'\[\[(.+?)\]\]')

    if not os.path.exists(file):
        sys.stderr.write(f"Missing {file}\n")
        exit(1)

    with open(file, "r") as f:
        markdown_string = f.read()

    lines = markdown_string.split("\n")

    converted = []
    ul_open = False
    ol_open = False
    p_open = False
    p_counter = 0

    for line in lines:
        line = line.strip()

        match = md5_re.search(line)
        if match:
            md5_hash = convert_to_md5(md5_re.search(line).group(1))
            line = md5_re.sub(md5_hash, line, count=1)

        modified_line = remove_c(line)
        if modified_line != line:
            line = modified_line

        if line.startswith("#"):
            heading_level = line.count("#")
            heading_text = line.strip("#").strip()

            if ul_open:
                converted.append("</ul>")
                ul_open = False
            if ol_open:
                converted.append("</ol>")
                ol_open = False
            if p_open:
                converted.append("</p>")
                p_open = False
            if "**" in heading_text:
                heading_text = \
                    heading_text = re.sub(bold_re, r"<b>\1</b>", heading_text)
            if "__" in heading_text:
                heading_text = \
                    heading_text = \
                    re.sub(italic_re, r"<em>\1</em>", heading_text)
            converted.append(
                f"<h{heading_level}>{heading_text}</h{heading_level}>"
            )

        elif line.startswith("-"):
            if not ul_open:
                converted.append("<ul>")
                ul_open = True
            if p_open:
                converted.append("</p>")
                p_open = False
            if ol_open:
                converted.append("</ol>")
                ol_open = False
            list_first = line.strip("- ").rstrip("\n")
            if "**" in list_first:
                list_first = \
                    list_first = re.sub(bold_re, r"<b>\1</b>", list_first)
            if "__" in list_first:
                list_first = \
                    list_first = re.sub(italic_re, r"<em>\1</em>", list_first)
            converted.append(f"<li>{list_first}</li>")

        elif line.startswith("* "):
            if not ol_open:
                converted.append("<ol>")
                ol_open = True
            if p_open:
                converted.append("</p>")
                p_open = False
            if ul_open:
                converted.append("</ul>")
                ul_open = False
            list_first = line.strip("* ").rstrip('\n')
            if "**" in list_first:
                list_first = \
                    list_first = re.sub(bold_re, r"<b>\1</b>", list_first)
            if "__" in list_first:
                list_first = \
                    list_first = re.sub(italic_re, r"<em>\1</em>", list_first)
            converted.append(f"<li>{list_first}</li>")

        elif line:
            if ul_open:
                converted.append("</ul>")
                ul_open = False
            if ol_open:
                converted.append("</ol>")
                ol_open = False
            if not p_open:
                converted.append("<p>")
                p_counter += 1
                p_open = True
            if p_counter > 1:
                converted.append("<br/>")
            p_counter += 1
            line = re.sub(bold_re, r"<b>\1</b>", line)
            line = re.sub(italic_re, r"<em>\1</em>", line)
            converted.append(line)

        elif not line:
            if ul_open:
                converted.append("</ul>")
                ul_open = False
            if ol_open:
                converted.append("</ol>")
                ol_open = False
            if p_open:
                converted.append("</p>")
                p_open = False
            p_counter = 0

    if p_open:
        converted.append("</p>")
    if ul_open:
        converted.append("</ul>")
    if ol_open:
        converted.append("</ol>")

    html = "\n".join(converted)
    with open(out, "w") as f:
        f.write(html)

    exit(0)

