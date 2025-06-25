# ESG Report Generator with Graph, Metrics & Compliance Flags

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from jinja2 import Template
from pathlib import Path

# --- Define function to generate ESG chart ---
def generate_esg_chart(scores, path):
    plt.figure(figsize=(6, 4))
    plt.bar(scores.keys(), scores.values())
    plt.title("ESG Pillar Scores")
    plt.ylabel("Score (0-100)")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

# --- Function to render report in HTML ---
def generate_html_report(company, esg_score, metrics, flags, chart_path, output_html_path):
    template_str = """
    <html>
    <head>
      <style>
        body { font-family: sans-serif; padding: 30px; }
        .score { font-size: 20px; }
        .flag { color: red; font-weight: bold; }
        .compliant { color: green; }
      </style>
    </head>
    <body>
      <h1>📄 ESG Summary Report</h1>
      <p><strong>Company:</strong> {{ company }}</p>
      <p class="score">🌱 ESG Score: {{ esg_score }}</p>

      <h2>📊 Metrics</h2>
      <ul>
        {% for metric in metrics %}
          <li>{{ metric.name }}: {{ metric.value }}</li>
        {% endfor %}
      </ul>

      <h2>🚩 Compliance Flags</h2>
      <ul>
        {% for flag in flags %}
          <li class="flag">{{ flag }}</li>
        {% endfor %}
      </ul>

      <h2>📉 ESG Breakdown</h2>
      <img src="{{ chart_path }}" width="500px">
    </body>
    </html>
    """
    template = Template(template_str)
    html_content = template.render(
        company=company,
        esg_score=esg_score,
        metrics=metrics,
        flags=flags,
        chart_path=Path(chart_path).name
    )
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

# --- Streamlit Integration ---
def generate_esg_report(company, esg_score, e_score, s_score, g_score, compliance_df):
    scores = {
        "Environmental": round(e_score, 1),
        "Social": round(s_score, 1),
        "Governance": round(g_score, 1)
    }

    metrics = [
        {"name": "GHG Emissions", "value": f"{company['GHG Emissions (tCO₂e)']} tCO₂e"},
        {"name": "Renewable Energy %", "value": f"{company['Renewable Energy %']}%"},
        {"name": "Gender Pay Gap", "value": f"{company['Gender Pay Gap %']}%"},
    ]

    flags = compliance_df[compliance_df["Compliance Status"].str.contains("❌|⚠️")]["Recommendation"].tolist()

    chart_path = "esg_scores_chart.png"
    report_path = "esg_report.html"

    generate_esg_chart(scores, chart_path)
    generate_html_report(company["Company"], esg_score, metrics, flags, chart_path, report_path)

    return report_path

