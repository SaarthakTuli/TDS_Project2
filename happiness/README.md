# README: Understanding the Quality of Life Across Countries

## Overview of the Dataset

In this analysis, we explore a comprehensive dataset that evaluates quality of life indicators among various countries from the years 2005 to 2023. The dataset focuses on several key variables associated with well-being, including:

- **Country Name**: The name of the country.
- **Year**: The year of data collection.
- **Life Ladder**: A subjective measure of well-being on a scale of 0 to 10.
- **Log GDP per capita**: The logarithm of GDP per capita, adjusted for purchasing power parity.
- **Social Support**: The perceived support that individuals feel they have from their social networks.
- **Healthy Life Expectancy at Birth**: The average number of years a newborn is expected to live in good health.
- **Freedom to Make Life Choices**: The degree of personal freedom individuals feel in making life choices.
- **Generosity**: A measure reflecting the extent of charitable giving.
- **Perceptions of Corruption**: The public’s perception of corruption within their governance systems.
- **Positive Affect / Negative Affect**: Measurements of emotional well-being.

The dataset consists of 2,363 rows, with no missing values, allowing for a thorough analysis of the relationships between various aspects of quality of life.

## Analysis Conducted

We performed a detailed statistical analysis, which included:

- **Descriptive Statistics**: We calculated mean, standard deviation, minimum and maximum values for key indicators.
- **Correlation Analysis**: We explored the relationships between different variables, identifying which factors are significantly related to overall well-being, as represented by the Life Ladder score.
- **Kurtosis and Skewness** Checks: We assessed the distribution of data for normality, noting the skewness and kurtosis values to understand data behavior.
- **Mutual Information Analysis**: We evaluated how different features contribute to understanding the Life Ladder and other variables.

## Key Insights Discovered

1. **Strong Relationships**: There are significant positive correlations between the Life Ladder and several factors:
   - **Log GDP per Capita (0.77)**: The higher a country's GDP per capita, the better individuals report their quality of life.
   - **Social Support (0.72)**: People who feel supported by their social circles tend to rate their well-being higher.
   - **Healthy Life Expectancy (0.71)**: Longer life expectancy correlates with higher happiness levels.
   - **Freedom to Make Life Choices (0.54)**: Greater personal freedom is linked to higher reported life satisfaction.
   - **Perceptions of Corruption (-0.42)**: Countries perceived as more corrupt tend to have lower happiness ratings.

2. **Generosity and Affect**: Generosity moderately correlates with life satisfaction, while positive emotions positively relate to the Life Ladder, while negative emotions show a negative correlation.

3. **Varying Access to Resources**: Countries exhibiting higher life dissatisfaction may struggle with issues of governance and resource distribution, evident through correlated perceptions of corruption and socio-economic metrics.

## Implications of Findings

These insights can direct policymakers and researchers interested in enhancing the quality of life. Here are some suggested actions based on the findings:

- **Economic Policies**: Develop strategies to improve GDP per capita, particularly in lesser economically developed regions.
- **Social Programs**: Invest in social support initiatives, fostering community networks that bolster emotional stability and well-being.
- **Health Initiatives**: Promote health and wellness programs that seek to increase life expectancy and improve the general health status of populations.
- **Governance Reforms**: Address corruption thoroughly, improving transparency and trust in institutions to create an environment conducive to happiness and well-being.
- **Cultural Campaigns**: Encourage cultural shifts that focus on community involvement, generosity, and altruism to build stronger communal ties.

## Conclusion

This analysis provides a meaningful understanding of the interplay between various quality of life indicators, highlighting the importance of economic, social, and governance-related aspects in enhancing human well-being across the globe. By implementing the suggested interventions, countries can work towards improving the happiness and life satisfaction of their citizens.