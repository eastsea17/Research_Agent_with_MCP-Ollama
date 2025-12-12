"""
HTML Report Generator
Converts markdown reports to styled HTML files.
"""
import os
import re
from datetime import datetime


def markdown_to_html(markdown_content: str, title: str = "Research Report") -> str:
    """
    Convert markdown to styled HTML.
    Handles basic markdown: headers, bold, italic, lists, tables, code blocks.
    """
    html_lines = []
    
    # Process line by line
    lines = markdown_content.split('\n')
    in_code_block = False
    in_table = False
    in_list = False
    
    for line in lines:
        # Code blocks
        if line.startswith('```'):
            if in_code_block:
                html_lines.append('</pre></code>')
                in_code_block = False
            else:
                lang = line[3:].strip() or 'text'
                html_lines.append(f'<code><pre class="code-block language-{lang}">')
                in_code_block = True
            continue
        
        if in_code_block:
            html_lines.append(escape_html(line))
            continue
        
        # Headers
        if line.startswith('# '):
            html_lines.append(f'<h1>{process_inline(line[2:])}</h1>')
            continue
        if line.startswith('## '):
            html_lines.append(f'<h2>{process_inline(line[3:])}</h2>')
            continue
        if line.startswith('### '):
            html_lines.append(f'<h3>{process_inline(line[4:])}</h3>')
            continue
        if line.startswith('#### '):
            html_lines.append(f'<h4>{process_inline(line[5:])}</h4>')
            continue
        if line.startswith('##### '):
            html_lines.append(f'<h5>{process_inline(line[6:])}</h5>')
            continue
        
        # Horizontal rule
        if line.strip() == '---':
            html_lines.append('<hr>')
            continue
        
        # Tables
        if '|' in line and line.strip().startswith('|'):
            if not in_table:
                html_lines.append('<table class="report-table">')
                in_table = True
            
            # Skip separator row
            if re.match(r'^\|[-:\s|]+\|$', line.strip()):
                continue
            
            cells = [c.strip() for c in line.strip().split('|')[1:-1]]
            row_tag = 'th' if not any('---' in c for c in cells) and html_lines[-1] == '<table class="report-table">' else 'td'
            row_html = '<tr>' + ''.join(f'<{row_tag}>{process_inline(c)}</{row_tag}>' for c in cells) + '</tr>'
            html_lines.append(row_html)
            continue
        elif in_table:
            html_lines.append('</table>')
            in_table = False
        
        # Lists
        if line.strip().startswith('- ') or line.strip().startswith('• '):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            content = line.strip()[2:]
            html_lines.append(f'<li>{process_inline(content)}</li>')
            continue
        elif in_list and line.strip() == '':
            html_lines.append('</ul>')
            in_list = False
        
        # Blockquotes
        if line.startswith('> '):
            html_lines.append(f'<blockquote>{process_inline(line[2:])}</blockquote>')
            continue
        
        # Regular paragraph
        if line.strip():
            html_lines.append(f'<p>{process_inline(line)}</p>')
        else:
            html_lines.append('')
    
    # Close any open tags
    if in_table:
        html_lines.append('</table>')
    if in_list:
        html_lines.append('</ul>')
    
    body_content = '\n'.join(html_lines)
    
    # Wrap in full HTML document with styling
    html_template = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape_html(title)}</title>
    <style>
        :root {{
            --primary-color: #2563eb;
            --secondary-color: #64748b;
            --bg-color: #f8fafc;
            --card-bg: #ffffff;
            --text-color: #1e293b;
            --border-color: #e2e8f0;
        }}
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.7;
            color: var(--text-color);
            background-color: var(--bg-color);
            padding: 2rem;
            max-width: 900px;
            margin: 0 auto;
        }}
        
        h1 {{
            color: var(--primary-color);
            border-bottom: 3px solid var(--primary-color);
            padding-bottom: 0.5rem;
            margin: 2rem 0 1rem;
        }}
        
        h2 {{
            color: var(--text-color);
            border-left: 4px solid var(--primary-color);
            padding-left: 1rem;
            margin: 2rem 0 1rem;
        }}
        
        h3, h4, h5 {{
            color: var(--secondary-color);
            margin: 1.5rem 0 0.75rem;
        }}
        
        p {{
            margin: 0.75rem 0;
        }}
        
        hr {{
            border: none;
            border-top: 2px solid var(--border-color);
            margin: 2rem 0;
        }}
        
        .report-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
            background: var(--card-bg);
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        .report-table th, .report-table td {{
            padding: 0.75rem 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}
        
        .report-table th {{
            background: var(--primary-color);
            color: white;
            font-weight: 600;
        }}
        
        .report-table tr:hover {{
            background: #f1f5f9;
        }}
        
        blockquote {{
            border-left: 4px solid var(--secondary-color);
            padding: 1rem 1.5rem;
            margin: 1rem 0;
            background: #f1f5f9;
            border-radius: 0 8px 8px 0;
        }}
        
        code {{
            background: #e2e8f0;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-family: 'SF Mono', Monaco, monospace;
            font-size: 0.9em;
        }}
        
        pre.code-block {{
            background: #1e293b;
            color: #e2e8f0;
            padding: 1.5rem;
            border-radius: 8px;
            overflow-x: auto;
            margin: 1rem 0;
        }}
        
        ul {{
            margin: 1rem 0;
            padding-left: 2rem;
        }}
        
        li {{
            margin: 0.5rem 0;
        }}
        
        strong {{
            color: var(--primary-color);
        }}
        
        .status-accepted {{
            color: #16a34a;
            font-weight: bold;
        }}
        
        .status-refined {{
            color: #ca8a04;
            font-weight: bold;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 1rem;
            }}
        }}
    </style>
</head>
<body>
{body_content}
<footer style="margin-top: 3rem; padding-top: 1rem; border-top: 1px solid var(--border-color); text-align: center; color: var(--secondary-color);">
    Generated by Deep Research Agent | {datetime.now().strftime('%Y-%m-%d %H:%M')}
</footer>
</body>
</html>"""
    
    return html_template


def escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;'))


def process_inline(text: str) -> str:
    """Process inline markdown: bold, italic, code, links."""
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # Inline code
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    # Status badges
    text = text.replace('`accepted`', '<span class="status-accepted">✓ accepted</span>')
    text = text.replace('`refined_best_effort`', '<span class="status-refined">◐ refined (best effort)</span>')
    
    return text


def convert_md_to_html(md_filepath: str) -> str:
    """
    Convert a markdown file to HTML and save alongside it.
    Returns the path to the generated HTML file.
    """
    if not os.path.exists(md_filepath):
        print(f"Warning: Markdown file not found: {md_filepath}")
        return None
    
    # Read markdown content
    with open(md_filepath, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Extract title from first H1 or filename
    title_match = re.search(r'^# (.+)$', md_content, re.MULTILINE)
    title = title_match.group(1) if title_match else os.path.basename(md_filepath)
    
    # Convert to HTML
    html_content = markdown_to_html(md_content, title)
    
    # Save HTML file
    html_filepath = md_filepath.replace('.md', '.html')
    with open(html_filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML report generated: {html_filepath}")
    return html_filepath
