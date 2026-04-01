# Use Python 3.9 slim image as base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy model files and data
COPY pred_model_main.py .
COPY CCLE_extracted_503_cell_lines_L1000_common_genes_3747_feature_vector_v1_selected_common_3_platform_v2.txt .
COPY GDSC_988_cell_line_name_main_fix_RRID_v1.txt .
COPY GDSC_CCLE_cross_domain_mode_7_v4.joblib .

# Copy the API wrapper script
COPY app.py .

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["python", "app.py"]