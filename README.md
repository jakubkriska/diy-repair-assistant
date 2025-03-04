# DIY Repair Assistant

DIY Repair Assistant is an intelligent chatbot application designed to help users diagnose, repair, and maintain household items. By integrating natural language processing, computer vision, and interactive annotation tools, the assistant provides real-time, step-by-step guidance for your repair projects.

## Table of Contents

1.  [Overview](#overview)
2.  [Features](#features)
3.  [Architecture](#architecture)
4.  [Installation](#installation)
    1.  [Prerequisites](#prerequisites)
    2.  [Backend Setup](#backend-setup)
        1.  [Create a Virtual Environment and Install Dependencies](#create-a-virtual-environment-and-install-dependencies)
        2.  [Set Up Environment Variables](#set-up-environment-variables)
    3.  [Frontend Setup](#frontend-setup)
5.  [Usage](#usage)
    1.  [Web Interface](#web-interface)
    2.  [Terminal Mode](#terminal-mode)
6.  [Project Structure](#project-structure)
7.  [Configuration](#configuration)
8.  [Image Upload & Annotation](#image-upload--annotation)
9.  [Customization](#customization)
10. [Future Enhancements](#future-enhancements)
11. [License](#license)

## Overview <a name="overview"></a>

DIY Repair Assistant offers a conversational interface where users can describe their repair issues and upload images for detailed visual analysis. Whether you’re fixing a broken table or repairing a damaged chair, this project guides you through every step of the process.

## Features <a name="features"></a>

-   **Interactive Chat:** Engage with an assistant that guides you through diagnostic questions and repair steps.
-   **Image Analysis:** Upload an image to have the assistant analyze visible damage using a Llama Vision model via the Groq API.
-   **Canvas Annotation:** Annotate uploaded images with drawing tools (rectangle, circle, freehand) and options to undo or clear annotations.
-   **Keyboard Shortcuts:** Send messages by pressing Enter, with Shift+Enter inserting a newline.
-   **Multi-Mode Operation:** Use the web interface for a graphical experience or run in terminal mode for a command-line interaction.
-   **Configurable Workflow:** Customize conversation prompts, response formatting, and diagnostic steps through a YAML configuration file.

## Architecture <a name="architecture"></a>

The project consists of two main components:

-   **Backend (Flask):** Handles chat interactions, image uploads, image analysis, and conversation history. It communicates with the Groq API and applies YAML-based response formatting.
-   **Frontend (React):** Provides a responsive chat interface, text input with keyboard shortcuts, image uploads, and an interactive canvas (using Konva) for image annotation.

## Installation <a name="installation"></a>

### Prerequisites <a name="prerequisites"></a>

-   **Python 3.9+**
-   **Node.js and npm**
-   Required Python packages: Flask, requests, PyYAML, python-dotenv, torch, Pillow, etc.
-   Frontend dependencies: React, axios, react-konva, use-image, etc.

### Backend Setup <a name="backend-setup"></a>

1.  **Clone the Repository:**

    ```bash
    git clone [https://github.com/yourusername/diy-repair-assistant.git](https://github.com/yourusername/diy-repair-assistant.git)
    cd diy-repair-assistant/backend
    ```
2.  **Create a Virtual Environment and Install Dependencies:** <a name="create-a-virtual-environment-and-install-dependencies"></a>

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
3.  **Set Up Environment Variables:** <a name="set-up-environment-variables"></a>
    Create a `.env` file in the backend directory and add:

    ```
    GROQ_API_KEY=your_api_key_here
    GROQ_API_URL=your_api_url_here
    ```
4.  **Ensure the YAML Configuration File Exists:**
    Verify that `config.yaml` is present in the backend folder.

### Frontend Setup <a name="frontend-setup"></a>

1.  **Navigate to the Frontend Directory:**

    ```bash
    cd ../frontend
    ```
2.  **Install Frontend Dependencies:**

    ```bash
    npm install
    ```

## Usage <a name="usage"></a>

### Web Interface <a name="web-interface"></a>

1.  **Start the Backend Server:**
    From the backend folder, run:

    ```bash
    python app.py
    ```
2.  **Start the Frontend Server:**
    From the frontend folder, run:

    ```bash
    npm start
    ```
3.  **Interact with the Assistant:**

    -   Open your browser and navigate to `http://localhost:3000`.
    -   Use the chat box to enter repair-related questions.
    -   Upload images using the paperclip icon.  Annotate the image using the canvas tools (draw, undo, clear) displayed below the image preview.
    -   The assistant will analyze the image and integrate the analysis into the ongoing conversation.

### Terminal Mode <a name="terminal-mode"></a>

1.  **Run the Backend in Terminal Mode:**
    When you run `python app.py`, you’ll be prompted to select a mode.
2.  **Select Terminal Mode:**
    Type `terminal` to interact with the assistant via the command line.
3.  **Follow On-Screen Instructions:**
    Enter your repair queries and follow the step-by-step guidance provided by the assistant.

## Project Structure <a name="project-structure"></a>

diy-repair-assistant/
├── backend/
│   ├── app.py                # Main Flask application
│   ├── lvl.py                # Llama Vision image analysis integration
│   ├── config.yaml           # YAML configuration for prompts and formatting
│   ├── requirements.txt      # Python dependencies
│   └── uploads/              # Directory for storing uploaded images
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.js            # Main React component
│   │   └── App.css           # Styling for the frontend
│   ├── package.json          # Node.js dependencies and scripts
│   └── ...
└── README.md

## Configuration <a name="configuration"></a>

-   `config.yaml`: Customize conversation prompts, diagnostic instructions, and response formatting.
-   `.env`: Store your sensitive environment variables (e.g., `GROQ_API_KEY` and `GROQ_API_URL`).

## Image Upload & Annotation <a name="image-upload--annotation"></a>

-   **Image Analysis:**
    When you upload an image, it is processed by `lvl.py` using the Groq API to generate a detailed description of the visible damage.
-   **Annotation Canvas:**
    The uploaded image is displayed in a responsive canvas that preserves its natural proportions. Annotation tools include:
    -   Undo: Removes the last drawn shape.
    -   Clear: Clears all annotations.
    -   Modal Option (Optional):
        The annotation interface can also be displayed in a modal window that appears during image annotation and closes when finished, keeping the main chat uncluttered.

## Customization <a name="customization"></a>

-   **Styling:** Adjust the CSS in `App.css` to change the layout, colors, and styles of the chat interface and image preview.
-   **Prompts & Responses:** Edit `config.yaml` and the prompt strings in `lvl.py` to tailor the assistant’s tone and level of detail.
-   **Keyboard Shortcuts:**
    Use `Enter` to send messages and `Shift+Enter` to insert newlines.

## Future Enhancements <a name="future-enhancements"></a>

-   **Improved Error Handling:** Enhance error reporting and fallback mechanisms for API or network issues.
-   **User Account Integration:** Add user authentication and save conversation history for later reference.
-   **Advanced Annotation Tools:** Introduce features like color selection, adjustable line thickness, and more sophisticated drawing tools.
-   **Mobile Optimization:** Further improve the user interface for a seamless mobile experience.

## License <a name="license"></a>

This project is licensed under the MIT License. See the LICENSE file for details.