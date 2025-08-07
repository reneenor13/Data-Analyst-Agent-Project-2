import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import base64
import io
from PIL import Image
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend

class VisualizationEngine:
    def __init__(self):
        # Set style for better looking plots
        plt.style.use('dark_background')
        sns.set_palette("husl")
        
    def create_plot(self, data, question):
        """Create visualizations based on question requirements"""
        try:
            question_lower = question.lower()
            
            if "scatterplot" in question_lower or "scatter" in question_lower:
                return self._create_scatterplot(data, question)
            elif "bar" in question_lower or "histogram" in question_lower:
                return self._create_bar_chart(data, question)
            elif "line" in question_lower or "time series" in question_lower:
                return self._create_line_chart(data, question)
            elif "pie" in question_lower:
                return self._create_pie_chart(data, question)
            else:
                # Default to scatterplot for correlation analysis
                return self._create_scatterplot(data, question)
                
        except Exception as e:
            raise Exception(f"Visualization creation failed: {str(e)}")
    
    def _create_scatterplot(self, data, question):
        """Create a scatterplot with optional regression line"""
        try:
            # Determine columns for plotting
            numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
            
            if len(numeric_cols) < 2:
                raise ValueError("Need at least 2 numeric columns for scatterplot")
            
            # Use first two numeric columns or try to identify from question
            x_col = numeric_cols[0]
            y_col = numeric_cols[1]
            
            # Try to identify columns from question
            if "rank" in question.lower() and "peak" in question.lower():
                for col in data.columns:
                    if "rank" in col.lower():
                        x_col = col
                    elif "peak" in col.lower():
                        y_col = col
            
            # Create the plot
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Scatter plot
            scatter = ax.scatter(data[x_col], data[y_col], 
                               alpha=0.7, s=50, c='cyan', edgecolors='white')
            
            # Add regression line if requested
            if "regression" in question.lower() or "line" in question.lower():
                z = np.polyfit(data[x_col], data[y_col], 1)
                p = np.poly1d(z)
                ax.plot(data[x_col], p(data[x_col]), 
                       "r--", linewidth=2, alpha=0.8, label='Regression Line')
                ax.legend()
            
            # Styling
            ax.set_xlabel(x_col, fontsize=12, color='white')
            ax.set_ylabel(y_col, fontsize=12, color='white')
            ax.set_title(f'{y_col} vs {x_col}', fontsize=14, color='white', pad=20)
            ax.grid(True, alpha=0.3)
            ax.set_facecolor('#1a1a2e')
            fig.patch.set_facecolor('#0f0f23')
            
            # Convert to base64
            return self._fig_to_base64(fig)
            
        except Exception as e:
            raise Exception(f"Scatterplot creation failed: {str(e)}")
    
    def _create_bar_chart(self, data, question):
        """Create a bar chart"""
        try:
            # Find categorical and numeric columns
            cat_cols = data.select_dtypes(include=['object']).columns.tolist()
            num_cols = data.select_dtypes(include=[np.number]).columns.tolist()
            
            if not cat_cols or not num_cols:
                raise ValueError("Need categorical and numeric columns for bar chart")
            
            x_col = cat_cols[0]
            y_col = num_cols[0]
            
            # Create grouped data if needed
            if len(data) > 20:  # Group if too many categories
                grouped = data.groupby(x_col)[y_col].mean().sort_values(ascending=False).head(15)
                x_data = grouped.index
                y_data = grouped.values
            else:
                x_data = data[x_col]
                y_data = data[y_col]
            
            # Create the plot
            fig, ax = plt.subplots(figsize=(12, 8))
            bars = ax.bar(range(len(x_data)), y_data, 
                         color='lightblue', alpha=0.8, edgecolor='white')
            
            # Styling
            ax.set_xlabel(x_col, fontsize=12, color='white')
            ax.set_ylabel(y_col, fontsize=12, color='white')
            ax.set_title(f'{y_col} by {x_col}', fontsize=14, color='white', pad=20)
            ax.set_xticks(range(len(x_data)))
            ax.set_xticklabels(x_data, rotation=45, ha='right')
            ax.grid(True, alpha=0.3, axis='y')
            ax.set_facecolor('#1a1a2e')
            fig.patch.set_facecolor('#0f0f23')
            
            plt.tight_layout()
            return self._fig_to_base64(fig)
            
        except Exception as e:
            raise Exception(f"Bar chart creation failed: {str(e)}")
    
    def _create_line_chart(self, data, question):
        """Create a line chart"""
        try:
            # Find date/time and numeric columns
            date_cols = data.select_dtypes(include=['datetime64']).columns.tolist()
            num_cols = data.select_dtypes(include=[np.number]).columns.tolist()
            
            if not date_cols and not num_cols:
                # Use index as x-axis if no date column
                x_col = data.index
                y_col = num_cols[0] if num_cols else data.columns[0]
            else:
                x_col = date_cols[0] if date_cols else data.columns[0]
                y_col = num_cols[0] if num_cols else data.columns[1]
            
            # Create the plot
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.plot(data[x_col] if x_col in data.columns else data.index, 
                   data[y_col], linewidth=2, color='cyan', marker='o', markersize=4)
            
            # Styling
            ax.set_xlabel(x_col if isinstance(x_col, str) else 'Index', 
                         fontsize=12, color='white')
            ax.set_ylabel(y_col, fontsize=12, color='white')
            ax.set_title(f'{y_col} Over Time', fontsize=14, color='white', pad=20)
            ax.grid(True, alpha=0.3)
            ax.set_facecolor('#1a1a2e')
            fig.patch.set_facecolor('#0f0f23')
            
            plt.tight_layout()
            return self._fig_to_base64(fig)
            
        except Exception as e:
            raise Exception(f"Line chart creation failed: {str(e)}")
    
    def _create_pie_chart(self, data, question):
        """Create a pie chart"""
        try:
            # Find categorical column for pie chart
            cat_cols = data.select_dtypes(include=['object']).columns.tolist()
            
            if not cat_cols:
                raise ValueError("Need categorical column for pie chart")
            
            col = cat_cols[0]
            
            # Get value counts
            counts = data[col].value_counts().head(10)  # Top 10 categories
            
            # Create the plot
            fig, ax = plt.subplots(figsize=(10, 10))
            colors = plt.cm.Set3(np.linspace(0, 1, len(counts)))
            
            wedges, texts, autotexts = ax.pie(counts.values, labels=counts.index, 
                                            autopct='%1.1f%%', colors=colors,
                                            textprops={'color': 'white'})
            
            # Styling
            ax.set_title(f'Distribution of {col}', fontsize=14, color='white', pad=20)
            fig.patch.set_facecolor('#0f0f23')
            
            plt.tight_layout()
            return self._fig_to_base64(fig)
            
        except Exception as e:
            raise Exception(f"Pie chart creation failed: {str(e)}")
    
    def _fig_to_base64(self, fig, format='png'):
        """Convert matplotlib figure to base64 string"""
        try:
            # Save to BytesIO
            img_buffer = io.BytesIO()
            fig.savefig(img_buffer, format=format, bbox_inches='tight', 
                       dpi=150, facecolor='#0f0f23', edgecolor='none')
            img_buffer.seek(0)
            
            # Check size and compress if necessary
            img_data = img_buffer.getvalue()
            if len(img_data) > 100000:  # 100KB limit
                # Reduce quality/size
                img_buffer.seek(0)
                img = Image.open(img_buffer)
                
                # Resize if too large
                if max(img.size) > 800:
                    ratio = 800 / max(img.size)
                    new_size = tuple(int(dim * ratio) for dim in img.size)
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # Save with compression
                compressed_buffer = io.BytesIO()
                img.save(compressed_buffer, format='PNG', optimize=True, quality=85)
                img_data = compressed_buffer.getvalue()
            
            plt.close(fig)  # Clean up memory
            
            # Encode to base64
            img_base64 = base64.b64encode(img_data).decode('utf-8')
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            plt.close(fig)  # Ensure cleanup
            raise Exception(f"Base64 conversion failed: {str(e)}")
    
    def create_plotly_chart(self, data, chart_type='scatter'):
        """Create interactive Plotly charts (alternative method)"""
        try:
            if chart_type == 'scatter':
                fig = px.scatter(data, x=data.columns[0], y=data.columns[1],
                               title=f"{data.columns[1]} vs {data.columns[0]}")
            elif chart_type == 'bar':
                fig = px.bar(data, x=data.columns[0], y=data.columns[1])
            elif chart_type == 'line':
                fig = px.line(data, x=data.columns[0], y=data.columns[1])
            
            # Update layout for dark theme
            fig.update_layout(
                plot_bgcolor='#1a1a2e',
                paper_bgcolor='#0f0f23',
                font_color='white'
            )
            
            # Convert to base64
            img_bytes = fig.to_image(format="png", width=1000, height=600)
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            raise Exception(f"Plotly chart creation failed: {str(e)}")
