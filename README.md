# finance-climat

## Project Overview

This application is an interactive dashboard designed to connect climate analysis with financial portfolio management. It helps users understand how climate-related indicators impact investment decisions and portfolio risk.
The dashboard integrates key climate metrics and transforms them into financial signals that can support decision-making.

## Objectives

The main objectives of this project are:

Analyze climate risks within a financial portfolio
Measure carbon intensity and transition exposure
Evaluate alignment with sustainable (green) activities
Provide decision-support tools for portfolio optimization

## Main Indicators

Physical Risk
Measures exposure to climate hazards such as floods or extreme weather.
Lower values indicate a safer portfolio.

WACI (Weighted Average Carbon Intensity)
Measures how carbon-intensive the portfolio is.
Lower values indicate better environmental performance.

GAR (Green Asset Ratio)
Measures the proportion of assets aligned with green activities.
Higher values indicate a more sustainable portfolio.

ITR (Implied Temperature Rise)
Estimates the temperature trajectory of the portfolio.
Lower values indicate better alignment with climate goals.

## How to Use the Application

Upload a portfolio
In the sidebar, upload a CSV or Excel file containing your portfolio data.
Navigate through modules
Use the sidebar to access different pages:
Executive Summary
Physical Risk
WACI
GAR module
ITR
Analyze results
Each page provides visualizations and KPIs to interpret the portfolio.

## Required Portfolio Format

The dataset must include at least the following columns:

Company name
NACE Code
Portfolio Weight (%)
EU Taxonomy alignment
Taxonomy Eligibility

Optional:

itr (for temperature analysis)

Data Processing

The application automatically:

Cleans column names
Converts numeric values (%, commas, etc.)
Normalizes portfolio weights
Excludes financial sector (NACE Code starting with "K") for GAR calculation

GAR Optimization

The GAR module includes an optimization feature:

Objective: maximize green alignment
Constraints:
total weights = 1
max weight per asset

The optimization uses the SLSQP method.

## Known Issues

ITR Refresh Bug
The ITR page may display errors or "N/A".
This is a known issue related to Streamlit refresh behavior.

Solution:
Refresh the page (F5)
Or re-upload the portfolio

GAR = 0 Issue
If GAR is equal to 0, possible causes are:

alignment values are missing or zero
incorrect data formatting
missing required columns

Session State Issue
The portfolio is stored in memory. In some cases, switching pages may require a refresh.

## Conclusion:

This dashboard demonstrates how climate indicators can be used as financial signals to improve portfolio analysis and support strategic investment decisions.
