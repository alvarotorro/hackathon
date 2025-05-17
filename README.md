# 🎯 Ticket Matchmaker

**🏆 Winner of the GigPlus Hackathon 2025**

Ticket Matchmaker is an AI-powered system designed to intelligently route customer support tickets to the most suitable ambassadors, enhancing response efficiency and customer satisfaction.

---

## 🚀 Overview

In the realm of customer support, assigning tickets to the right personnel is crucial. Traditional methods often rely on manual processes or simplistic rules, leading to delays and suboptimal customer experiences.

Ticket Matchmaker leverages Large Language Models (LLMs) to analyze ticket content and ambassador profiles, ensuring each ticket is directed to the best-fit ambassador — in real-time and with full explainability.

---

## 🧠 Features

- **Contextual Analysis**: Understands urgency, sentiment, and topic from natural language.
- **Ambassador Profiling**: Matches based on experience, availability, and skillset.
- **Matching Agent**: Returns optimal ambassador with confidence score and explanation.
- **Explainability**: Transparent JSON output for trust and auditability.
- **Scalable by Design**: Modular architecture ready for high-throughput scenarios.

---

## 🛠️ Architecture

- **Ticket Ingestion**
- **LLM-based Ticket Analyzer**
- **Ambassador Profile Manager**
- **Matching Engine (JSON in/out)**
- **API Layer** for external integration (e.g., DFM, Teams bot)

---

## 📦 Installation

```bash
git clone https://github.com/alvarotorro/hackathon.git
cd hackathon
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
