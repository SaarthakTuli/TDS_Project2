# /// script
# requires-python = ">=3.6,<3.10"
# dependencies = [
#   "pandas",
#   "numpy",
#   "matplotlib",
#   "seaborn",
#   "requests",
#   "umap-learn",
#   "hdbscan",
#   "chardet",
#   "scikit-learn",
#   "scipy",
#   "python-dotenv",
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

load_dotenv()
CUSTOM_CHAT_URL = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"

class DataLoader:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.df = self._read_csv_with_encoding(csv_path)
        self.original_columns = self.df.columns.tolist()
        self.missing_values = self.df.isnull().sum()

    def _read_csv_with_encoding(self, csv_path):
        encodings_to_try = [
            'utf-8-sig',
            'utf-8',
            'latin-1',
            'iso-8859-1',
            'cp1252',
        ]

        with open(csv_path, 'rb') as rawdata:
            result = chardet.detect(rawdata.read(100000))
            detected_encoding = result['encoding']

            if detected_encoding and detected_encoding.lower() not in map(str.lower, encodings_to_try):
                encodings_to_try.insert(0, detected_encoding)

        # reading with different encodings
        for encoding in encodings_to_try:
            try:
                try:
                    df = pd.read_csv(csv_path,
                                     encoding=encoding,
                                     low_memory=False,
                                     on_bad_lines='skip')

                    if not df.empty:
                        print(f"Successfully read CSV with {encoding} encoding")
                        return df

                except Exception as e:
                    print(f"Standard read failed with {encoding}: {e}")

                    with open(csv_path, 'r', encoding=encoding, errors='replace') as f:
                        file_content = f.read()

                    df = pd.read_csv(io.StringIO(file_content),
                                     low_memory=False,
                                     on_bad_lines='skip')

                    if not df.empty:
                        print(f"Successfully read CSV with {encoding} encoding using error replacement")
                        return df

            except Exception as e:
                print(f"Failed to read CSV with {encoding} encoding: {e}")
                continue

        raise ValueError(f"Could not read CSV file with any of the attempted encodings. "
                         f"Please check the file integrity and encoding.")

    def preprocess_data(self):
        # Preprocess missing values
        numeric_columns = self.df.select_dtypes(include=['int64', 'float64']).columns
        categorical_columns = self.df.select_dtypes(include=['object']).columns

        numeric_imputer = SimpleImputer(strategy='median')
        self.df[numeric_columns] = numeric_imputer.fit_transform(self.df[numeric_columns])

        categorical_imputer = SimpleImputer(strategy='most_frequent')
        self.df[categorical_columns] = categorical_imputer.fit_transform(self.df[categorical_columns])

        # Label Encoding for categorical columns
        self.label_encoders = {}
        for col in categorical_columns:
            le = LabelEncoder()
            self.df[f'{col}_encoded'] = le.fit_transform(self.df[col])
            self.label_encoders[col] = le

class DataAnalyzer:
    def __init__(self, df):
        self.df = df

    def descriptive_analysis(self):
        numeric_cols = self.df.select_dtypes(include=['int64', 'float64']).columns
        desc_stats = self.df[numeric_cols].describe().to_dict()

        skewness = self.df[numeric_cols].apply(lambda x: stats.skew(x)).to_dict()
        kurtosis = self.df[numeric_cols].apply(lambda x: stats.kurtosis(x)).to_dict()

        return {
            'description': desc_stats,
            'skewness': skewness,
            'kurtosis': kurtosis
        }

    def correlation_analysis(self):
        numeric_cols = self.df.select_dtypes(include=['int64', 'float64']).columns
        encoded_cols = [col for col in self.df.columns if col.endswith('_encoded')]

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

        return {
            'correlation_matrix': corr_matrix.to_dict(),
            'mutual_information': mutual_info
        }

    def outlier_detection(self):
        numeric_cols = self.df.select_dtypes(include=['int64', 'float64']).columns

        z_scores = {}
        outliers = {}
        for col in numeric_cols:
            z = np.abs(stats.zscore(self.df[col]))
            z_scores[col] = z.tolist()
            outliers[col] = self.df[z > 3][col].tolist()

        return {
            'z_scores': z_scores,
            'outliers': outliers
        }

    def clustering_analysis(self):
        numeric_cols = self.df.select_dtypes(include=['int64', 'float64']).columns
        X = self.df[numeric_cols]

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        umap_reducer = umap.UMAP(n_components=2, random_state=42)
        X_umap = umap_reducer.fit_transform(X_scaled)

        clusterer = hdbscan.HDBSCAN(min_cluster_size=5, gen_min_span_tree=True)
        clusters = clusterer.fit_predict(X_scaled)

        return {
            'umap_coordinates': X_umap.tolist(),
            'cluster_labels': clusters.tolist(),
            'n_clusters': len(set(clusters)) - (1 if -1 in clusters else 0)
        }

class DataVisualizer:
    def __init__(self, df):
        self.df = df

    def generate_narrative(self, analysis_results, foldername):
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
here modify and give me
The data you received, briefly
The analysis you carried out
The insights you discovered
The implications of your findings (i.e. what to do with the insights)
Create a good readme file with proper formatting
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
                with open(foldername + 'README.md','w') as file:
                    file.write(result)
                return result
            else:
                return f"Failed to generate narrative. HTTP Status: {response.status_code}, Response: {response.text}"
        except Exception as e:
            return f"Narrative generation failed: {str(e)}"

    def visualize_insights(self, analysis_results, foldername):
        plt.figure(figsize=(12, 10))
        corr_matrix = pd.DataFrame(analysis_results['correlation_analysis']['correlation_matrix'])

        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))

        sns.heatmap(corr_matrix,
                    mask=mask,
                    annot=True,
                    cmap='coolwarm',
                    center=0,
                    square=True,
                    linewidths=0.5,
                    cbar_kws=None,
                    annot_kws={"fontsize":8})

        plt.title('Correlation Heatmap', fontsize=16, pad=20)
        plt.tight_layout()
        plt.savefig(foldername + 'correlation_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()

        # 2. Outlier Box Plot
        plt.figure(figsize=(15, 8))
        numeric_cols = self.df.select_dtypes(include=['int64', 'float64']).columns
        box_plot = self.df[numeric_cols].boxplot(rot=90)

        plt.title('Outlier Box Plot', fontsize=16, pad=20)
        plt.xlabel('Columns', fontsize=12)
        plt.ylabel('Values', fontsize=12)
        plt.tight_layout()
        plt.savefig(foldername + 'outlier_box_plot.png', dpi=300, bbox_inches='tight')
        plt.close()

        return {
            'correlation_heatmap': 'correlation_heatmap.png',
            'outlier_box_plot': 'outlier_box_plot.png'
        }

def main(csv_path):
    try:
        data_loader = DataLoader(csv_path)
        data_loader.preprocess_data()
        print("Data Loaded Successfully")


        foldername = csv_path.split(".csv")[0] + "/"
        if not os.path.exists(foldername):
            os.makedirs(foldername)


        analyzer = DataAnalyzer(data_loader.df)
        analysis_results = {
            'descriptive_analysis': analyzer.descriptive_analysis(),
            'correlation_analysis': analyzer.correlation_analysis(),
            'outlier_detection': analyzer.outlier_detection(),
            'clustering_analysis': analyzer.clustering_analysis()
        }
        print("Descriptive Statistics Generation Complete")

        visualizer = DataVisualizer(data_loader.df)
        analysis_results['visualization'] = visualizer.visualize_insights(analysis_results, foldername)
        print("Data Visualization Chart Completed")

        analysis_results['narrative'] = visualizer.generate_narrative(analysis_results, foldername)
        print("Narative Generation Completed")

    except Exception as e:
        print(f"Analysis failed: {e}")

if __name__ == "__main__":
    main(sys.argv[1])
