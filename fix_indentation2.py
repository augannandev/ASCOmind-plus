#!/usr/bin/env python3

# Script to fix remaining indentation issues in main_cancer_first.py

import re

# Read the file
with open('main_cancer_first.py', 'r') as f:
    lines = f.readlines()

# Fix specific problematic lines around 2025-2040
fixes = {
    2027: "                        # Add user message to history\n",
    2028: "                        st.session_state.chat_history.append({\n",
    2029: "                            'role': 'user',\n",
    2030: "                            'content': suggestion\n",
    2031: "                        })\n",
    2032: "                        \n",
    2033: "                        # Get AI response with detailed processing message\n",
    2034: "                        progress_placeholder = st.empty()\n",
    2035: "                        progress_placeholder.info(\"🔍 **AI is researching...** Searching through abstracts and generating insights...\")\n",
}

# Apply fixes
for line_num, new_content in fixes.items():
    if line_num - 1 < len(lines):
        lines[line_num - 1] = new_content

# Also fix the end of the suggested questions section (around line 2073)
# Find lines with the problematic indentation
for i, line in enumerate(lines):
    if i > 2070 and i < 2080:
        if line.strip() == "st.rerun()":
            lines[i] = "                            st.rerun()\n"
        elif line.strip().startswith("else:"):
            lines[i] = "                    else:\n"
        elif "AI Assistant not available" in line:
            lines[i] = "                        st.error(\"❌ AI Assistant not available. Please check your configuration.\")\n"

# Write back the file
with open('main_cancer_first.py', 'w') as f:
    f.writelines(lines)

print("Fixed remaining indentation issues!")
