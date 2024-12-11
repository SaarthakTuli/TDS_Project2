# /// script
# requires-python = ">=3.6,<3.10"
# dependencies = [
#   "pandas",
#   "numpy",
#   "scikit-learn",
#   "seaborn",
#   "matplotlib",
#   "umap-learn",
#   "hdbscan",
#   "requests",
#   "python-dotenv",
#   "chardet",
# ]
# ///

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import umap
import hdbscan
import os
import chardet
import io
import requests
import sys
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import mutual_info_classif
from scipy import stats
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API URL for generating narratives via GPT-4
CUSTOM_CHAT_URL = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"


class DataLoader:
    """
    DataLoader class to load data from CSV files with different encodings.
    Automatically detects encoding using chardet and handles reading with proper encodings.
    """
    def __init__(self, file_path):
        """
        Initializes the DataLoader with the file path.
        :param file_path: Path to the CSV file to be loaded.
        """
        self.file_path = file_path
        self.df = self.load_data()

    def load_data(self):
        """
        Loads the CSV file with automatic encoding detection.
        :return: Pandas DataFrame
        """
        encodings_to_try = ['utf-8-sig', 'utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        with open(self.file_path, 'rb') as rawdata:
            result = chardet.detect(rawdata.read(100000))
            detected_encoding = result['encoding']

            if detected_encoding and detected_encoding.lower() not in map(str.lower, encodings_to_try):
                encodings_to_try.insert(0, detected_encoding)

        # Try reading the file with different encodings
        for encoding in encodings_to_try:
            try:
                df = pd.read_csv(self.file_path, encoding=encoding, low_memory=False, on_bad_lines='skip')
                if not df.empty:
                    print(f"Successfully read CSV with {encoding} encoding")
                    return df
            except Exception as e:
                print(f"Failed to read with {encoding}: {e}")
                continue
        raise ValueError(f"Failed to read file with any of the attempted encodings.")


class DataAnalyzer:
    """
    DataAnalyzer class to perform various data analysis tasks such as descriptive statistics, correlation analysis,
    outlier detection, and clustering.
    """
    def __init__(self, df):
        """
        Initializes the DataAnalyzer with the provided DataFrame.
        :param df: Pandas DataFrame containing the data to be analyzed.
        """
        self.df = df

    def descriptive_analysis(self):
        """
        Performs descriptive analysis on numeric columns and calculates statistics like mean, std, min, max.
        :return: Dictionary containing descriptive statistics and skewness, kurtosis.
        """
        numeric_cols = self.df.select_dtypes(include=['int64', 'float64']).columns
        if numeric_cols.empty:
            return "No numeric columns to describe."
        desc_stats = self.df[numeric_cols].describe().to_dict()
        skewness = self.df[numeric_cols].apply(lambda x: stats.skew(x)).to_dict()
        kurtosis = self.df[numeric_cols].apply(lambda x: stats.kurtosis(x)).to_dict()
        return {'description': desc_stats, 'skewness': skewness, 'kurtosis': kurtosis}

    def correlation_analysis(self):
        """
        Computes the correlation matrix and mutual information between numeric columns.
        :return: Dictionary containing correlation matrix and mutual information.
        """
        numeric_cols = self.df.select_dtypes(include=['int64', 'float64']).columns
        if numeric_cols.empty:
            return {'correlation_matrix': {}, 'mutual_information': {}}
        corr_matrix = self.df[numeric_cols].corr()
        mutual_info = {}
        for col in numeric_cols:
            try:
                target = numeric_cols[0] if len(numeric_cols) > 1 else None
                if target and target != col:
                    mi_scores = mutual_info_classif(self.df[[col]], self.df[target])
                    mutual_info[col] = mi_scores[0]
            except:
                pass
        return {'correlation_matrix': corr_matrix.to_dict(), 'mutual_information': mutual_info}

    def outlier_detection(self):
        """
        Detects outliers in the data using z-scores.
        :return: Dictionary containing z-scores and outliers detected.
        """
        numeric_cols = self.df.select_dtypes(include=['int64', 'float64']).columns
        if numeric_cols.empty:
            return "No numeric columns for outlier detection."
        z_scores = {}
        outliers = {}
        for col in numeric_cols:
            z = np.abs(stats.zscore(self.df[col]))
            z_scores[col] = z.tolist()
            outliers[col] = self.df[z > 3][col].tolist()
        return {'z_scores': z_scores, 'outliers': outliers}

    def clustering_analysis(self):
        """
        Performs clustering using HDBSCAN and UMAP for dimensionality reduction.
        :return: Dictionary containing UMAP coordinates and cluster labels.
        """
        numeric_cols = self.df.select_dtypes(include=['int64', 'float64']).columns
        if numeric_cols.empty:
            return "No numeric columns for clustering analysis."

        # Impute missing values before clustering
        imputer = SimpleImputer(strategy='mean')
        self.df[numeric_cols] = imputer.fit_transform(self.df[numeric_cols])

        X = self.df[numeric_cols]
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        umap_reducer = umap.UMAP(n_components=2, random_state=42)
        X_umap = umap_reducer.fit_transform(X_scaled)
        clusterer = hdbscan.HDBSCAN(min_cluster_size=5, gen_min_span_tree=True)
        clusters = clusterer.fit_predict(X_scaled)
        return {'umap_coordinates': X_umap.tolist(), 'cluster_labels': clusters.tolist(), 'n_clusters': len(set(clusters)) - (1 if -1 in clusters else 0)}


class DataVisualizer:
    """
    DataVisualizer class to generate visualizations and narratives based on data analysis.
    """
    def __init__(self, df):
        """
        Initializes the DataVisualizer with the provided DataFrame.
        :param df: Pandas DataFrame containing the data to be visualized.
        """
        self.df = df

    def generate_narrative(self, analysis_results, foldername):
        """
        Generates a narrative story based on the analysis results using OpenAI's GPT-4 model.
        :param analysis_results: Dictionary containing the analysis results.
        :param foldername: Folder to save the README file with the generated narrative.
        :return: The generated narrative or error message.
        """
        try:
            api_token = os.environ['AIPROXY_TOKEN']
            if not api_token:
                raise ValueError("API token not found. Set the AIPROXY_TOKEN environment variable.")

            prompt = f"""Generate a compelling data story based on the following analysis:
Dataset Overview:- Columns: {', '.join(self.df.columns)}
- Number of Rows: {len(self.df)}
- Missing Values: {dict(self.df.isnull().sum())}
Descriptive Statistics:
{analysis_results['descriptive_analysis']}
Key Insights:- Correlation Highlights: {analysis_results['correlation_analysis']}
The data you received, briefly
The analysis you carried out
The insights you discovered
The implications of your findings (i.e. what to do with the insights)
"""
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are a data storyteller. Explain complex data insights in a clear, engaging manner."},
                    {"role": "user", "content": prompt}
                ]
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_token}"
            }

            response = requests.post(CUSTOM_CHAT_URL, json=payload, headers=headers)

            if response.status_code == 200:
                result = response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response content.")
                with open(f"{foldername}/README.md", "w") as file:
                    file.write(result)
                print(f"Generated narrative saved to {foldername}/README.md")
                return result
            else:
                raise Exception(f"Error in generating narrative: {response.status_code}")
        except Exception as e:
            print(f"Error generating narrative: {e}")
            return str(e)

    def visualize_insights(self, analysis_results, foldername):
        """
        Generates visualizations for the analysis results such as correlation matrix and outlier plots.
        :param analysis_results: Dictionary containing analysis results.
        :param foldername: Folder where the plots will be saved.
        :return: Dictionary containing paths to the saved visualization files.
        """
        plt.figure(figsize=(12, 10))
        corr_matrix = pd.DataFrame(analysis_results['correlation_analysis']['correlation_matrix'])
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
        plt.title('Correlation Heatmap', fontsize=16)
        plt.savefig(f"{foldername}/correlation_heatmap.png")
        plt.close()

        plt.figure(figsize=(12, 10))
        for col, outliers in analysis_results['outlier_detection']['outliers'].items():
            sns.boxplot(x=self.df[col])
            plt.title(f'Outlier Detection - {col}', fontsize=16)
            plt.savefig(f"{foldername}/outlier_detection_{col}.png")
            plt.close()

        return {'correlation_heatmap': f"{foldername}/correlation_heatmap.png", 'outlier_plots': f"{foldername}/outlier_detection.png"}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <path_to_csv_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    folder_name = file_path.split('.')[0] + "/"

    # Create the output folder if not exists
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    loader = DataLoader(file_path)
    analyzer = DataAnalyzer(loader.df)
    visualizer = DataVisualizer(loader.df)

    # Perform the analysis
    analysis_results = {
        'descriptive_analysis': analyzer.descriptive_analysis(),
        'correlation_analysis': analyzer.correlation_analysis(),
        'outlier_detection': analyzer.outlier_detection(),
        'clustering_analysis': analyzer.clustering_analysis()
    }

    # Save the analysis and visualizations
    analysis_report = visualizer.generate_narrative(analysis_results, folder_name)
    visualization_files = visualizer.visualize_insights(analysis_results, folder_name)

    print(f"Analysis completed! Reports and visualizations saved in '{folder_name}'")
