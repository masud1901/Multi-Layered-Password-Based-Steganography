"""Visualization script for steganography comparison results using Seaborn."""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np


def load_and_process_data():
    """Load and preprocess the comparison results."""
    df = pd.read_csv('comparison_results.csv')
    # Remove duplicate results
    df = df.drop_duplicates(
        subset=['Method', 'Message Size (Bytes)'],
        keep='first'
    )
    
    # Add layer depth security score
    df['Layer_Security'] = df.apply(
        lambda row: calculate_layer_security(
            row['Method'], 
            row['Layers'],
            row['Chi-Square']
        ), 
        axis=1
    )
    
    # Add normalized metrics
    df['PSNR_norm'] = normalize_column(df['PSNR (dB)'])
    df['Time_Efficiency'] = 1 / (df['Encoding Time (s)'] + df['Decoding Time (s)'])
    df['Time_Efficiency_norm'] = normalize_column(df['Time_Efficiency'])
    df['Storage_Efficiency'] = df['Message Size (Bytes)'] / (df['File Size (KB)'] * 1024)
    df['Storage_Efficiency_norm'] = normalize_column(df['Storage_Efficiency'])
    df['Layer_Security_norm'] = normalize_column(df['Layer_Security'])
    
    # Calculate security score from Chi-Square and BER
    df['Security_Score'] = 1 / (df['Chi-Square'] + df['Bit Error Rate'] + 1e-10)
    df['Security_Score_norm'] = normalize_column(df['Security_Score'])
    
    return df


def calculate_layer_security(method, layers, chi_square):
    """Calculate security score based on layer depth and chi-square."""
    if 'Proposed' not in method:
        return 1.0  # Base score for non-layered methods
    
    # Layer depth factor (exponential increase with layers)
    layer_factor = np.exp(layers - 1)
    
    # Chi-square inverse (lower chi-square means better security)
    chi_factor = 1 / (1 + chi_square)
    
    return layer_factor * chi_factor


def normalize_column(series):
    """Normalize column values to 0-1 range."""
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return pd.Series(1, index=series.index)
    return (series - min_val) / (max_val - min_val)


def plot_radar_chart(df):
    """Create radar chart comparing methods for each message size."""
    msg_sizes = df['Message Size (Bytes)'].unique()
    
    for msg_size in msg_sizes:
        data = df[df['Message Size (Bytes)'] == msg_size]
        
        # Metrics for radar chart
        metrics = ['PSNR_norm', 'Time_Efficiency_norm', 
                  'Storage_Efficiency_norm', 'Layer_Security_norm']
        
        # Number of variables
        num_vars = len(metrics)
        
        # Compute angle for each axis
        angles = [n / float(num_vars) * 2 * np.pi for n in range(num_vars)]
        angles += angles[:1]
        
        # Initialize the spider plot
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        # Plot data
        for idx, method in enumerate(data['Method']):
            values = data[data['Method'] == method][metrics].values.flatten().tolist()
            values += values[:1]
            ax.plot(angles, values, linewidth=2, linestyle='solid', label=method)
            ax.fill(angles, values, alpha=0.1)
        
        # Fix axis to go in the right order and start at 12 o'clock
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        
        # Draw axis lines for each angle and label
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(['PSNR', 'Time\nEfficiency', 
                           'Storage\nEfficiency', 'Layer\nSecurity'])
        
        plt.title(f'Method Comparison - {msg_size} bytes', pad=20)
        plt.legend(loc='center left', bbox_to_anchor=(1.2, 0.5))
        plt.tight_layout()
        plt.savefig(f'plots/radar_comparison_{msg_size}bytes.png', 
                   bbox_inches='tight', dpi=300)
        plt.close()


def plot_performance_matrix(df):
    """Create heatmap of normalized performance metrics."""
    metrics = ['PSNR_norm', 'Time_Efficiency_norm', 
              'Storage_Efficiency_norm', 'Layer_Security_norm']
    
    # Calculate mean performance for each method
    performance = df.groupby('Method')[metrics].mean()
    
    # Create heatmap
    plt.figure(figsize=(12, 8))
    sns.heatmap(performance, annot=True, cmap='RdYlGn', center=0.5,
                fmt='.2f', cbar_kws={'label': 'Normalized Score'})
    plt.title('Method Performance Comparison')
    plt.tight_layout()
    plt.savefig('plots/performance_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()


def plot_layer_security_comparison(df):
    """Plot layer security comparison with IEEE paper formatting."""
    # IEEE column width is approximately 3.5 inches
    plt.figure(figsize=(7, 3.5))  # Width spans both columns
    
    # Use colorblind-friendly palette
    colors = sns.color_palette("colorblind", n_colors=len(df['Method'].unique()))
    
    # Create grouped bar plot with enhanced styling
    ax = sns.barplot(
        data=df,
        x='Message Size (Bytes)',
        y='Layer_Security',
        hue='Method',
        palette=colors,
        edgecolor='black',
        linewidth=0.5
    )
    
    # IEEE-style formatting
    plt.title('Security Analysis by Layer Depth', 
              fontsize=9, 
              pad=10, 
              fontweight='bold')
    plt.xlabel('Payload Size (Bytes)', fontsize=8)
    plt.ylabel('Security Score', fontsize=8)
    
    # Rotate x-axis labels
    plt.xticks(rotation=45, ha='right', fontsize=7)
    plt.yticks(fontsize=7)
    
    # Add grid
    ax.yaxis.grid(True, linestyle='--', alpha=0.3)
    ax.set_axisbelow(True)
    
    # Place legend inside the plot
    plt.legend(
        title='Method',
        title_fontsize=7,
        fontsize=6,
        loc='upper right',  # Position in upper right corner
        bbox_to_anchor=(0.98, 0.98),  # Fine-tune position
        borderaxespad=0,
        ncol=1,  # Stack legend entries vertically
        frameon=True,  # Add frame
        fancybox=False,  # Rectangular box
        edgecolor='black',  # Black edge color
        framealpha=0.8,  # Slightly transparent background
        markerscale=0.7  # Make legend markers smaller
    )
    
    # Thin spines
    for spine in ax.spines.values():
        spine.set_linewidth(0.5)
    
    plt.tight_layout()
    plt.savefig(
        'plots/layer_security_comparison.png',
        dpi=600,
        bbox_inches='tight',
        facecolor='white',
        edgecolor='none'
    )
    plt.close()


def plot_security_heatmap(df):
    """Create heatmap for IEEE paper format."""
    # Filter for proposed methods only
    proposed_df = df[df['Method'].str.contains('Proposed')]
    
    # Selected metrics for 2x2 layout
    metrics = {
        'Layer_Security': 'Security Score',
        'File Size (KB)': 'Storage (KB)',
        'PSNR (dB)': 'PSNR (dB)',
        'Chi-Square': 'Statistical Security'
    }
    
    # Professional color schemes for different metrics
    color_maps = {
        'Layer_Security': 'Blues',     # Blue gradient
        'File Size (KB)': 'BuGn',      # Blue-Green gradient
        'PSNR (dB)': 'RdYlBu_r',      # Red-Yellow-Blue
        'Chi-Square': 'PuBu'           # Purple-Blue gradient
    }
    
    # IEEE double column width
    fig, axes = plt.subplots(2, 2, figsize=(7, 7))
    axes = axes.ravel()
    
    for idx, (metric, title) in enumerate(metrics.items()):
        # Create pivot table
        pivot_data = proposed_df.pivot_table(
            values=metric,
            index='Layers',
            columns='Message Size (Bytes)',
            aggfunc='mean'
        )
        
        # Plot heatmap
        cbar_kws = {
            'label': title,
        }
        
        ax = sns.heatmap(
            pivot_data,
            annot=True,
            fmt='.1f',
            cmap=color_maps[metric],
            cbar_kws=cbar_kws,
            ax=axes[idx],
            annot_kws={'size': 6},
            center=None,  # Remove center point to avoid dark colors
            vmin=pivot_data.min().min(),  # Set proper value range
            vmax=pivot_data.max().max()
        )
        
        # Set colorbar label size after creating the heatmap
        ax.collections[0].colorbar.ax.tick_params(labelsize=7)
        ax.collections[0].colorbar.ax.set_ylabel(title, fontsize=7)
        
        axes[idx].set_title(title, fontsize=8, pad=5, fontweight='bold')
        axes[idx].set_xlabel('Payload Size (Bytes)', fontsize=7)
        axes[idx].set_ylabel('Layers', fontsize=7)
        
        # Set tick label sizes
        axes[idx].tick_params(labelsize=6)
        
        # Rotate x-axis labels
        axes[idx].set_xticklabels(
            axes[idx].get_xticklabels(),
            rotation=45,
            ha='right'
        )
    
    plt.suptitle(
        'Multi-Layer Security Analysis',
        fontsize=9,
        y=0.95,
        fontweight='bold'
    )
    
    # Adjust spacing
    plt.tight_layout()
    plt.savefig(
        'plots/security_metrics_heatmap.png',
        dpi=600,
        bbox_inches='tight',
        facecolor='white',
        edgecolor='none'
    )
    plt.close()


def main():
    """Generate all visualization plots."""
    # Create plots directory
    Path('plots').mkdir(exist_ok=True)
    
    # Load and process data
    df = load_and_process_data()
    
    # Generate plots
    plot_radar_chart(df)
    plot_performance_matrix(df)
    plot_layer_security_comparison(df)
    plot_security_heatmap(df)
    
    print("Visualization completed. Plots saved in 'plots' directory.")


if __name__ == "__main__":
    main() 