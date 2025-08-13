#!/usr/bin/env python3

# Fix the AI assistant section specifically

with open('main_cancer_first.py', 'r') as f:
    lines = f.readlines()

# Find the problematic section and replace it with properly indented code
start_line = None
end_line = None

for i, line in enumerate(lines):
    if "# Add user message to history" in line:
        start_line = i
    if start_line and "try:" in line and "# Create filters" in lines[i+1]:
        end_line = i + 1
        break

if start_line and end_line:
    # Replace the problematic lines with correctly indented code
    replacement = [
        "                        # Add user message to history\n",
        "                        st.session_state.chat_history.append({\n",
        "                            'role': 'user',\n", 
        "                            'content': suggestion\n",
        "                        })\n",
        "                        \n",
        "                        # Get AI response with detailed processing message\n",
        "                        progress_placeholder = st.empty()\n",
        "                        progress_placeholder.info(\"🔍 **AI is researching...** Searching through abstracts and generating insights...\")\n",
        "                        \n",
        "                        try:\n"
    ]
    
    lines = lines[:start_line] + replacement + lines[end_line:]

# Write back
with open('main_cancer_first.py', 'w') as f:
    f.writelines(lines)

print("Fixed AI assistant section!")
