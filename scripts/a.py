# -*- coding: utf-8 -*-
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Image
import os
e
# Create output directory if it doesn't exist
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# Create a PDF file for the first logo variant
pdf_path_final = os.path.join(output_dir, "ThermoCore_Final_Logo_Variant1.pdf")

# Initialize canvas
c = canvas.Canvas(pdf_path_final, pagesize=A4)
width, height = A4

# Note: You'll need to add your logo image file to the project
# image_path = "path/to/your/logo.png"
# c.drawImage(image_path, 70, height/2 - 150, width=450, preserveAspectRatio=True, mask='auto')

# Add header text
c.setFont("Helvetica-Bold", 22)
c.drawString(160, height - 100, "ThermoCore Logo — Variant 1")

# Add footer note
c.setFont("Helvetica", 12)
c.drawString(180, 50, "(c) 2025 ThermoCore Heating Systems - Brand Identity Design")

# Save the final PDF
c.save()

print(f"PDF created at: {pdf_path_final}")