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
* Python

### Installation

1.  **Clone the repository:**
    ```sh
    git clone [https://github.com/desmondwong1215/pulse-check.git](https://github.com/desmondwong1215/pulse-check.git)
    cd pulse-check
    ```

2.  **Install dependencies:**
    ```sh
    npm install
    # or
    yarn install
    ```

3.  **Configure the environment:**
    * Duplicate the example configuration file:
        ```sh
        cp config.example.json config.json
        ```
    * Modify `config.json` to set up the necessary modules and integrations. See the [Configuration](#-configuration) section below for details.

### Running the Application

* **Start the development server:**
    ```sh
    npm start
    ```
* The application will launch, running the modules defined in your configuration.

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

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/desmondwong1215/pulse-check/issues).

To contribute:

1.  **Fork** the project.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  **Commit** your changes (`git commit -m 'Add some AmazingFeature'`).
4.  **Push** to the branch (`git push origin feature/AmazingFeature`).
5.  Open a **Pull Request**.

## 📜 License

This project is distributed under the MIT License. See `LICENSE` for more information.
