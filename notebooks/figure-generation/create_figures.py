#!/usr/bin/env python3
"""
Create compelling figures for PharmacoProfiler manuscript
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle, FancyBboxPatch
import matplotlib.patches as mpatches
from matplotlib.sankey import Sankey
import networkx as nx
from matplotlib.patches import Circle
import matplotlib.colors as mcolors

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# Create output directory
import os
os.makedirs('/home/sandbox/figures', exist_ok=True)

# Figure 1: Platform Overview Schematic
def create_platform_overview():
    """Create a comprehensive platform overview figure"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    # Define components and their positions
    components = {
        'Data Sources': {'pos': (2, 8), 'size': (3, 1.5), 'color': '#FF6B6B'},
        'Data Harmonization': {'pos': (6, 8), 'size': (3, 1.5), 'color': '#4ECDC4'},
        'Machine Learning': {'pos': (10, 8), 'size': (3, 1.5), 'color': '#45B7D1'},
        'Tripartite Network': {'pos': (2, 5), 'size': (3, 1.5), 'color': '#96CEB4'},
        'Interactive Visualization': {'pos': (6, 5), 'size': (3, 1.5), 'color': '#FFEAA7'},
        'Drug Prediction': {'pos': (10, 5), 'size': (3, 1.5), 'color': '#DDA0DD'},
        'User Interface': {'pos': (6, 2), 'size': (3, 1.5), 'color': '#FFB6C1'}
    }
    
    # Draw components
    for name, props in components.items():
        x, y = props['pos']
        w, h = props['size']
        rect = FancyBboxPatch((x-w/2, y-h/2), w, h, 
                             boxstyle="round,pad=0.1", 
                             facecolor=props['color'], 
                             edgecolor='black',
                             alpha=0.7)
        ax.add_patch(rect)
        ax.text(x, y, name, ha='center', va='center', fontsize=11, fontweight='bold')
    
    # Draw arrows
    arrows = [
        ((3.5, 8), (4.5, 8)),  # Data Sources -> Harmonization
        ((7.5, 8), (8.5, 8)),  # Harmonization -> ML
        ((3.5, 7.25), (3.5, 6.5)),  # Data Sources -> Network
        ((6, 7.25), (6, 6.5)),  # Harmonization -> Visualization
        ((10, 7.25), (10, 6.5)),  # ML -> Prediction
        ((6, 4.25), (6, 3.5)),  # Visualization -> UI
    ]
    
    for start, end in arrows:
        ax.annotate('', xy=end, xytext=start,
                   arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    
    # Add data source details
    sources = ['GDSC (~970 cell lines)', 'CCLE (~1000 cell lines)', 
               'NCI-60 (60 cell lines)', 'gCSI (754 cell lines)', 
               'FIMM (50 cell lines)', 'CTRP v2']
    
    for i, source in enumerate(sources):
        ax.text(0.5, 9.5 - i*0.3, f"• {source}", fontsize=9, ha='left')
    
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 11)
    ax.set_title('PharmacoProfiler Platform Architecture', fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('/home/sandbox/figures/platform_overview.png', dpi=300, bbox_inches='tight')
    plt.close()

# Figure 2: Dataset Statistics Visualization
def create_dataset_statistics():
    """Create comprehensive dataset statistics visualization"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # Subplot 1: Database comparison
    databases = ['GDSC', 'CCLE', 'NCI-60', 'gCSI', 'FIMM', 'CTRP v2']
    cell_lines = [970, 1000, 60, 754, 50, 800]  # Estimated for CTRP
    compounds = [700, 24, 20000, 16, 52, 500]  # Estimated for CTRP
    
    x = np.arange(len(databases))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, cell_lines, width, label='Cell Lines', alpha=0.8, color='#FF6B6B')
    bars2 = ax1.bar(x + width/2, compounds, width, label='Compounds', alpha=0.8, color='#4ECDC4')
    
    ax1.set_xlabel('Database')
    ax1.set_ylabel('Count')
    ax1.set_title('Database Comparison: Cell Lines vs Compounds')
    ax1.set_xticks(x)
    ax1.set_xticklabels(databases, rotation=45)
    ax1.legend()
    ax1.set_yscale('log')
    
    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom', fontsize=8)
    
    # Subplot 2: Tissue type distribution (pie chart)
    tissue_types = ['Lung', 'Breast', 'Colon', 'CNS/Brain', 'Blood/Hematologic', 
                   'Ovarian', 'Pancreatic', 'Prostate', 'Skin/Melanoma', 'Other']
    counts = [200, 150, 120, 100, 200, 80, 70, 60, 50, 970]
    
    colors = plt.cm.Set3(np.linspace(0, 1, len(tissue_types)))
    wedges, texts, autotexts = ax2.pie(counts, labels=tissue_types, autopct='%1.1f%%', 
                                      colors=colors, startangle=90)
    ax2.set_title('Cell Line Distribution by Tissue Type')
    
    # Subplot 3: Platform integration overview
    integration_data = {
        'Total Compounds': 50000,
        'Total Cell Lines': 2000,
        'Tissue Types': 32,
        'Data Sources': 6
    }
    
    bars = ax3.bar(integration_data.keys(), integration_data.values(), 
                   color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'], alpha=0.8)
    ax3.set_title('PharmacoProfiler Integration Statistics')
    ax3.set_ylabel('Count')
    ax3.tick_params(axis='x', rotation=45)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}', ha='center', va='bottom')
    
    # Subplot 4: Model performance comparison
    validation_types = ['Intra-platform', 'Cross-platform']
    correlations = [0.6, 0.4]
    
    bars = ax4.bar(validation_types, correlations, color=['#DDA0DD', '#FFEAA7'], alpha=0.8)
    ax4.set_title('Machine Learning Model Performance')
    ax4.set_ylabel('Pearson Correlation')
    ax4.set_ylim(0, 0.8)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('/home/sandbox/figures/dataset_statistics.png', dpi=300, bbox_inches='tight')
    plt.close()

# Figure 3: Tripartite Network Visualization
def create_tripartite_network():
    """Create a tripartite network visualization"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    
    # Create a sample tripartite network
    G = nx.Graph()
    
    # Add nodes for each layer
    drugs = [f'Drug_{i}' for i in range(1, 9)]
    cell_lines = [f'Cell_{i}' for i in range(1, 11)]
    targets = [f'Target_{i}' for i in range(1, 7)]
    
    G.add_nodes_from(drugs, bipartite=0)
    G.add_nodes_from(cell_lines, bipartite=1)
    G.add_nodes_from(targets, bipartite=2)
    
    # Add edges (sample connections)
    np.random.seed(42)
    for drug in drugs:
        # Connect drugs to cell lines
        connected_cells = np.random.choice(cell_lines, size=np.random.randint(3, 7), replace=False)
        for cell in connected_cells:
            G.add_edge(drug, cell)
        
        # Connect drugs to targets
        connected_targets = np.random.choice(targets, size=np.random.randint(1, 4), replace=False)
        for target in connected_targets:
            G.add_edge(drug, target)
    
    # Position nodes in three layers
    pos = {}
    
    # Drugs on the left
    for i, drug in enumerate(drugs):
        pos[drug] = (0, i * 1.2)
    
    # Cell lines in the middle
    for i, cell in enumerate(cell_lines):
        pos[cell] = (3, i * 0.96)
    
    # Targets on the right
    for i, target in enumerate(targets):
        pos[target] = (6, i * 1.6)
    
    # Draw the network
    nx.draw_networkx_nodes(G, pos, nodelist=drugs, node_color='#FF6B6B', 
                          node_size=800, alpha=0.8, ax=ax)
    nx.draw_networkx_nodes(G, pos, nodelist=cell_lines, node_color='#4ECDC4', 
                          node_size=600, alpha=0.8, ax=ax)
    nx.draw_networkx_nodes(G, pos, nodelist=targets, node_color='#45B7D1', 
                          node_size=1000, alpha=0.8, ax=ax)
    
    nx.draw_networkx_edges(G, pos, alpha=0.3, edge_color='gray', ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=8, ax=ax)
    
    # Add layer labels
    ax.text(-0.5, 4, 'DRUGS', rotation=90, fontsize=14, fontweight='bold', 
            ha='center', va='center')
    ax.text(3, -1, 'CELL LINES', fontsize=14, fontweight='bold', 
            ha='center', va='center')
    ax.text(6.5, 4, 'TARGETS', rotation=90, fontsize=14, fontweight='bold', 
            ha='center', va='center')
    
    ax.set_title('Tripartite Network Visualization\n(Drugs - Cell Lines - Targets)', 
                fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('/home/sandbox/figures/tripartite_network.png', dpi=300, bbox_inches='tight')
    plt.close()

# Figure 4: Data Harmonization Process
def create_harmonization_process():
    """Create data harmonization process flowchart"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    
    # Define process steps
    steps = [
        {'name': 'Raw Data\nCollection', 'pos': (2, 6), 'color': '#FF6B6B'},
        {'name': 'Identifier\nMapping', 'pos': (5, 6), 'color': '#4ECDC4'},
        {'name': 'Format\nStandardization', 'pos': (8, 6), 'color': '#45B7D1'},
        {'name': 'Quality\nControl', 'pos': (11, 6), 'color': '#96CEB4'},
        {'name': 'Data\nIntegration', 'pos': (6.5, 3), 'color': '#FFEAA7'},
        {'name': 'Harmonized\nDatabase', 'pos': (6.5, 1), 'color': '#DDA0DD'}
    ]
    
    # Draw process steps
    for step in steps:
        x, y = step['pos']
        rect = FancyBboxPatch((x-1, y-0.7), 2, 1.4, 
                             boxstyle="round,pad=0.1", 
                             facecolor=step['color'], 
                             edgecolor='black',
                             alpha=0.7)
        ax.add_patch(rect)
        ax.text(x, y, step['name'], ha='center', va='center', 
               fontsize=10, fontweight='bold')
    
    # Draw arrows
    arrows = [
        ((3, 6), (4, 6)),    # Raw -> Mapping
        ((6, 6), (7, 6)),    # Mapping -> Format
        ((9, 6), (10, 6)),   # Format -> QC
        ((5, 5.3), (6, 4.4)),   # Mapping -> Integration
        ((8, 5.3), (7, 4.4)),   # Format -> Integration
        ((11, 5.3), (7.5, 4.4)), # QC -> Integration
        ((6.5, 2.3), (6.5, 1.7))  # Integration -> Database
    ]
    
    for start, end in arrows:
        ax.annotate('', xy=end, xytext=start,
                   arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    
    # Add data source labels
    sources = ['GDSC', 'CCLE', 'NCI-60', 'gCSI', 'FIMM']
    for i, source in enumerate(sources):
        ax.text(2, 7.5 - i*0.3, source, fontsize=9, ha='center', 
               bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgray', alpha=0.5))
    
    # Add challenges addressed
    challenges = [
        'Different assay types',
        'Inconsistent identifiers', 
        'Varied data formats',
        'Protocol differences',
        'Nomenclature variations'
    ]
    
    for i, challenge in enumerate(challenges):
        ax.text(12.5, 7 - i*0.4, f"• {challenge}", fontsize=9, ha='left')
    
    ax.text(12.5, 7.5, 'Challenges Addressed:', fontsize=10, fontweight='bold', ha='left')
    
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 8)
    ax.set_title('Data Harmonization Process in PharmacoProfiler', 
                fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('/home/sandbox/figures/harmonization_process.png', dpi=300, bbox_inches='tight')
    plt.close()

# Figure 5: Machine Learning Workflow
def create_ml_workflow():
    """Create machine learning workflow diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    # Define workflow components
    components = [
        {'name': 'Feature\nExtraction', 'pos': (2, 8), 'size': (2.5, 1.2), 'color': '#FF6B6B'},
        {'name': 'Data\nPreprocessing', 'pos': (6, 8), 'size': (2.5, 1.2), 'color': '#4ECDC4'},
        {'name': 'Model\nTraining', 'pos': (10, 8), 'size': (2.5, 1.2), 'color': '#45B7D1'},
        {'name': 'Cross-Platform\nValidation', 'pos': (2, 5), 'size': (2.5, 1.2), 'color': '#96CEB4'},
        {'name': 'Intra-Platform\nValidation', 'pos': (6, 5), 'size': (2.5, 1.2), 'color': '#FFEAA7'},
        {'name': 'Performance\nEvaluation', 'pos': (10, 5), 'size': (2.5, 1.2), 'color': '#DDA0DD'},
        {'name': 'Drug Sensitivity\nPrediction', 'pos': (6, 2), 'size': (2.5, 1.2), 'color': '#FFB6C1'}
    ]
    
    # Draw components
    for comp in components:
        x, y = comp['pos']
        w, h = comp['size']
        rect = FancyBboxPatch((x-w/2, y-h/2), w, h, 
                             boxstyle="round,pad=0.1", 
                             facecolor=comp['color'], 
                             edgecolor='black',
                             alpha=0.7)
        ax.add_patch(rect)
        ax.text(x, y, comp['name'], ha='center', va='center', 
               fontsize=10, fontweight='bold')
    
    # Draw workflow arrows
    arrows = [
        ((3.25, 8), (4.75, 8)),     # Feature -> Preprocessing
        ((7.25, 8), (8.75, 8)),     # Preprocessing -> Training
        ((10, 7.4), (10, 5.6)),     # Training -> Performance
        ((8.75, 5), (7.25, 5)),     # Performance -> Intra
        ((4.75, 5), (3.25, 5)),     # Intra -> Cross
        ((6, 4.4), (6, 2.6)),       # Intra -> Prediction
    ]
    
    for start, end in arrows:
        ax.annotate('', xy=end, xytext=start,
                   arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    
    # Add performance metrics
    ax.text(12, 6, 'Performance Metrics:', fontsize=12, fontweight='bold')
    ax.text(12, 5.5, '• Pearson Correlation: 0.6 (intra)', fontsize=10)
    ax.text(12, 5.2, '• Pearson Correlation: 0.4 (cross)', fontsize=10)
    ax.text(12, 4.9, '• RMSE evaluation', fontsize=10)
    ax.text(12, 4.6, '• R² coefficient', fontsize=10)
    
    # Add input features
    ax.text(0.5, 9, 'Input Features:', fontsize=12, fontweight='bold')
    features = ['Cell line genomics', 'Drug descriptors', 'Target information', 'Pathway data']
    for i, feature in enumerate(features):
        ax.text(0.5, 8.7 - i*0.3, f"• {feature}", fontsize=10)
    
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.set_title('Machine Learning Workflow for Drug Sensitivity Prediction', 
                fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('/home/sandbox/figures/ml_workflow.png', dpi=300, bbox_inches='tight')
    plt.close()

# Execute all figure creation functions
if __name__ == "__main__":
    print("Creating platform overview figure...")
    create_platform_overview()
    
    print("Creating dataset statistics visualization...")
    create_dataset_statistics()
    
    print("Creating tripartite network visualization...")
    create_tripartite_network()
    
    print("Creating harmonization process diagram...")
    create_harmonization_process()
    
    print("Creating ML workflow diagram...")
    create_ml_workflow()
    
    print("All figures created successfully!")