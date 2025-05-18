import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import os

# Helper function to parse text file into structured data
def parse_text(file):
    lines = file.read().decode("utf-8").splitlines()
    data = []
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            data.append((key.strip(), value.strip()))
    return data

# Create a PDF with fpdf2 using default Arial font
class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
        self.set_font("DejaVu", "", 12)

    def header(self):
        self.set_fill_color(50, 90, 150)
        self.set_text_color(255)
        self.set_font("DejaVu", "B", 14)
        self.cell(0, 10, "Client Analysis Report", ln=True, align="C", fill=True)
        self.ln(5)

    def chapter_title(self, title):
        self.set_text_color(30, 30, 30)
        self.set_font("DejaVu", "B", 12)
        self.cell(0, 10, title, ln=True, align="L")
        self.ln(2)

    def chapter_body(self, body):
        self.set_text_color(50, 50, 50)
        self.set_font("DejaVu", "", 11)
        self.multi_cell(0, 8, body)
        self.ln()

    def add_graph(self, image_path):
        self.image(image_path, x=10, w=190)
        self.ln(10)

# Generate bar chart from data
def generate_bar_chart(data, image_path):
    keys = [item[0] for item in data]
    values = [float(item[1]) if item[1].replace('.', '', 1).isdigit() else 0 for item in data]

    plt.figure(figsize=(10, 4))
    plt.bar(keys, values, color='skyblue')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(image_path)
    plt.close()

# Streamlit App
st.set_page_config(page_title="Text to PDF SaaS", layout="wide")
st.title("📊 Text File → PDF Client Report Generator")

uploaded_file = st.file_uploader("Upload your Analysis Text File (.txt)", type=["txt"])

if uploaded_file:
    data = parse_text(uploaded_file)
    df = pd.DataFrame(data, columns=["Metric", "Value"])
    st.success("File successfully parsed! Here's the preview:")
    st.dataframe(df)

    if st.button("Generate PDF Report"):
        image_path = "chart.png"
        generate_bar_chart(data, image_path)

        pdf = PDF()
        pdf.add_page()
        pdf.chapter_title("Summary of Analysis")
        for key, val in data:
            pdf.chapter_body(f"{key}: {val}")
        pdf.add_page()
        pdf.chapter_title("Graphical Representation")
        pdf.add_graph(image_path)

        output_path = "client_report.pdf"
        pdf.output(output_path)

        with open(output_path, "rb") as f:
            st.download_button(
                label="📥 Download PDF",
                data=f,
                file_name="client_report.pdf",
                mime="application/pdf"
            )

        os.remove(image_path)
        os.remove(output_path)
