# Pulse Check ✔️

An intelligent employee engagement and development platform, powered by AI to support PSA's multi-generational workforce.



## 📝 Overview

Pulse Check is an advanced AI-driven system designed specifically for PSA to foster a dynamic and supportive work environment. It moves beyond traditional reviews by engaging employees through daily check-ins and check-outs. These interactions use personalized, microlearning-focused questions to gather continuous feedback.

Over time, Pulse Check analyzes this data to provide deep insights, generate performance summaries, and support employee growth, well-being, and career development. By leveraging these data-driven insights, Pulse Check helps build a more engaged, inclusive, and future-ready workforce aligned with PSA’s core values.

## ✨ Features

* **Daily Check-ins & Microlearning:** Generates personalized questions during daily employee check-ins and check-outs, focusing on continuous feedback and microlearning.
* **Long-Term Employee Analysis:** Gathers sufficient information over time to analyze employee progress and provide insights that support the platform's main purpose.
* **Personalised Career Pathways:** Recommends tailored career tracks, internal mobility options, and upskilling or reskilling plans based on individual aspirations, strengths, and identified skill gaps.
* **AI-Powered Conversational Support:** Provides continuous, confidential support for employee engagement, mental well-being, and professional development through an intelligent conversational interface.
* **Predictive Leadership Analytics:** Utilizes behavioral, performance, and engagement data to identify and predict future leadership potential within the organization.
* **Inclusive Workforce Development:** Fosters an inclusive culture with targeted mentorship programs, enhanced digital accessibility, and a robust feedback and recognition system that celebrates PSA’s values.


## 🚀 Getting Started

Follow these instructions to get a local copy of the platform up and running for development and testing.

### Prerequisites

* Node.js (v14 or later)
* npm / yarn
* Python 3.8+ and pip

### Installation & Setup

1.  **Clone the repository:**
    ```sh
    git clone [https://github.com/desmondwong1215/pulse-check.git](https://github.com/desmondwong1215/pulse-check.git)
    cd pulse-check
    ```

2.  **Backend Setup:**
    ```sh
    # Navigate to the backend directory
    cd backend

    # Create and activate a virtual environment
    # On Windows:
    python -m venv venv
    .\venv\Scripts\activate
    
    # On macOS/Linux:
    # python3 -m venv venv
    # source venv/bin/activate

    # Install Python dependencies
    pip install -r requirements.txt
    ```
    *Note: A `requirements.txt` file is present in the `backend` directory.*

4.  **Frontend Setup:**
    ```sh
    # Navigate back to the root directory from /backend, then navigate to frontend directory
    cd ..
    cd frontend
    
    # Install npm packages
    npm install
    # or
    yarn install
    ```

### Running the Application

This application requires both the backend and frontend servers to be running simultaneously in separate terminals.

1.  **Run the Backend Server:**
    * In your first terminal, navigate to the `backend` directory.
    * Make sure your virtual environment is activated.
    * Start the Python server:
    ```sh
    python app.py
    ```
    * The backend should now be running on its configured port (e.g., http://localhost:5000).

2.  **Run the Frontend Server:**
    * Open a **new terminal**.
    * Navigate to the project's `frontend` directory.
    * Start the React development server:
    ```sh
    npm run dev
    ```
    * The application frontend will launch in your browser, typically at http://localhost:5173.



## ⚙️ Configuration

You can enable and configure the platform's core modules by editing the \`config.json\` file. Here is an example structure:

```json
{
  "tenantId": "PSA-Global",
  "modules": [
    {
      "name": "CareerPathways",
      "enabled": true,
      "options": {
        "syncFrequency": "24h"
      }
    },
    {
      "name": "ConversationalAI",
      "enabled": true,
      "provider": "PulseCheckAI"
    },
    {
      "name": "LeadershipAnalytics",
      "enabled": true,
      "dataSources": ["performance", "engagement"]
    },
    {
      "name": "InclusiveDevelopment",
      "enabled": true
    }
  ]
}
```

## 🛠️ Tech Stack

* **Frontend:** React, JSX
* **Backend:** Python
