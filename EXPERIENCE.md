# Vibe Coding Experience Documentation

## Tool Selection Justification
For this project, I selected **Cursor** as my primary development environment and **Streamlit (Python)** as the framework. I chose Cursor because it is an "AI-native" editor based on VS Code. Unlike using ChatGPT in a separate browser window, Cursor allows me to generate and edit code directly within the file using shortcuts like `Ctrl+I`, which significantly reduces context switching.

I opted for Python and Streamlit for the "Weather Dashboard" project because Streamlit is ideal for data-driven applications. It allows for the creation of interactive web interfaces purely with Python, eliminating the need to write complex HTML or CSS. This combination felt perfect for "Vibe Coding," where the goal is to achieve a functional result rapidly.

## Development Process
I utilized Cursor's "Composer" feature to generate the initial codebase. I started with a single "Mega Prompt" that detailed all required features, such as the Open-Meteo API integration, city search, and forecast charts. The command `Ctrl+I` was the most effective tool, allowing me to highlight code and ask for specific changes in natural language.

The development process took approximately **3 major iterations** to get fully working code:
1.  **Generation:** The initial prompt created the skeleton and UI structure.
2.  **Refinement:** I asked the AI to fix specific data display issues (Humidity).
3.  **Restoration:** I had to ask the AI to rewrite the file when it accidentally deleted the import statements.

## Challenges and Solutions
I encountered a few interesting challenges during the process:

1.  **The "Blank Screen" Issue:** At first, when I ran the app, the browser showed a blank page. I realized that while the AI wrote the code, it didn't automatically save the file to the disk. The solution was simply pressing `Ctrl+S` to trigger Streamlit's hot-reload feature.
2.  **The "Humidity N/A" Bug:** The application initially displayed "N/A" for humidity. I highlighted the code and prompted the AI: *"The Humidity is showing as 'N/A', please fix it."* The AI correctly identified that the API response logic needed to match the current hour with the hourly data array and fixed the indexing.
3.  **Code Deletion Accident:** While fixing the humidity bug, the AI accidentally deleted the top part of the `app.py` file (the library imports). This caused the app to crash. I overcame this by instructing the AI to *"Rewrite the entire file correctly, ensuring all imports like streamlit and requests are included at the top."* This restored the functionality.

## Reflection
I was surprised by how much the "Vibe Coding" approach shifted my role from a "Coder" to a "Product Manager." Instead of worrying about syntax errors or memorizing API endpoints, I focused on defining features and reviewing the output. The speed of prototyping was incredible; I built a functional dashboard in minutes, which would usually take hours.

I will definitely use tools like Cursor for future projects, especially for prototyping and building internal tools. However, the experience taught me that one cannot blindly trust the AI. The "missing imports" incident showed that a developer must still understand the code structure to spot and fix AI mistakes. This technology will likely lower the barrier to entry for software development but will require developers to become better at debugging and system design.