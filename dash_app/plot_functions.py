import plotly.express as px
import pandas as pd
import pymysql
import yfinance as yf
from flask import session, request
import numpy as np
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
from plotnine import *
import geopandas as gpd

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io
import base64
import seaborn as sns



def get_score(df):
    # 假设从数据源加载数据
     # 例如，获取数据的自定义函数

    # 检查和转换每个评分列。如果缺少某列，则为其添加默认值
    for column in ['Total_Score', 'E_Score', 'S_Score', 'G_Score']:
        if column not in df.columns:
            print(f"Warning: '{column}' column is missing. Setting default value to 0.")
            df[column] = 0  # 设置默认值
        else:
            # 转换为数值类型
            df[column] = pd.to_numeric(df[column], errors='coerce')

    # 提取每个分数列
    total_score = df['Total_Score']
    e_score = df['E_Score']
    s_score = df['S_Score']
    g_score = df['G_Score']

    return total_score, e_score, s_score, g_score
# ESG 等级判定函数
def determine_esg_level(df):
    total_score, _, _, _ = get_score(df)
    # 如果 total_score 是一个 Series，确保只提取单一值
    if isinstance(total_score, pd.Series):
        total_score = total_score.iloc[0]  # 提取第一个数值
    elif isinstance(total_score, (list, np.ndarray)):
        total_score = total_score[0]  # 如果是列表或数组，也提取第一个数值

    if total_score >= 85.72:
        return "AAA"
    elif total_score >= 71.44:
        return "AA"
    elif total_score >= 57.15:
        return "A"
    elif total_score >= 42.87:
        return "BBB"
    elif total_score >= 28.68:
        return "BB"
    elif total_score >= 14.30:
        return "B"
    else:
        return "CCC"


# 仪表盘
def create_gauge(df):
    total_score, _, _, _ = get_score(df)
    # 如果 total_score 是一个 Series，确保只提取单一值
    if isinstance(total_score, pd.Series):
        total_score = total_score.iloc[0]  # 提取第一个数值
    elif isinstance(total_score, (list, np.ndarray)):
        total_score = total_score[0]  # 如果是列表或数组，也提取第一个数值

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=total_score,
        title={'text': "ESG Score", 'font': {'size': 20}},  # 调整标题字体大小
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "black"},
            'bar': {'color': "darkgreen", 'thickness': 0.2},  # 调整指针的粗细
            'bgcolor': "white",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 40], 'color': "white"},
                {'range': [40, 60], 'color': "lightgreen"},
                {'range': [60, 80], 'color': "limegreen"},
                {'range': [80, 100], 'color': "green"},
            ],
        },
        domain={'x': [0.1, 0.9], 'y': [0, 0.75]}  # 缩小仪表的显示范围
    ))

    fig_gauge.update_layout(
        margin=dict(t=0, b=0, l=0, r=0),dragmode=False,hovermode=False  # 去除外边距
    )

    return fig_gauge

# 获取股票数据

# 创建e_score环状图
def create_doughnut_chart(df):
    _, e_score, _, _ = get_score(df)
    e_score = float(e_score.iloc[0].round(2))  # Convert to float with two decimal places
    remain_e_score = round(33.53 - e_score, 2)

    fig_doughnut_chart_e = go.Figure()

    # Create the doughnut chart
    fig_doughnut_chart_e.add_trace(go.Pie(
        labels=["E Score", ""],  # Labels
        values=[e_score, remain_e_score],  # Score and remaining score
        hole=0.5,  # Adjusted hole size for a fuller chart
        marker=dict(colors=["#228B22", "#DCDCDC"]),  # Set color for score part
        showlegend=False,  # Disable legend
        textinfo="none",  # Hide default text, use custom text instead
        hoverinfo="label+value",  # Display label and score on hover
        rotation=210
    ))

    # Add "E Score" label at the center
    fig_doughnut_chart_e.update_layout(
        annotations=[
            dict(
                text="E Score",
                x=0.5, y=0.5,
                font=dict(size=30, color="black"),
                showarrow=False
            ),
            # Place the score at the bottom center of the chart
            dict(
                text=str(e_score),  # Display the score value
                x=0.5, y=0.25,  # Adjust y to control vertical position
                font=dict(size=28, color="black"),
                showarrow=False
            )
        ],
        margin=dict(t=5, b=5, l=5, r=5)  # Reduce margins
    )

    return fig_doughnut_chart_e


def create_doughnut_chart_s(df):
    # 从数据库中获取数据
    _, _, s_score, _ = get_score(df)  # 假设 get_score() 是一个数据库查询函数

    # 调试输出，确保查询结果有效
    print(f"Retrieved S score: {s_score}")

    # 如果 s_score 是空的，或者包含无效值，则返回一个空的图表
    if s_score is None or s_score.empty or s_score.iloc[0] is None:
        return go.Figure()  # 返回一个空的图表，避免显示空白

    # 将 s_score 转换为浮动类型，并保留两位小数
    s_score = float(s_score.iloc[0].round(2))  # Convert to float with two decimal places
    remain_s_score = round(45.90 - s_score, 2)

    # 创建圆环图
    fig_doughnut_chart_s = go.Figure()

    fig_doughnut_chart_s.add_trace(go.Pie(
        labels=["S Score", ""],  # Labels
        values=[s_score, remain_s_score],  # Score and remaining score
        hole=0.5,  # Adjusted hole size for a fuller chart
        marker=dict(colors=["#228B22", "#DCDCDC"]),  # Set color for score part
        showlegend=False,  # Disable legend
        textinfo="none",  # Hide default text, use custom text instead
        hoverinfo="label+value",  # Display label and score on hover
        rotation=210
    ))

    # Add "S Score" label at the center
    fig_doughnut_chart_s.update_layout(
        annotations=[
            dict(
                text="S Score",
                x=0.5, y=0.5,
                font=dict(size=30, color="black"),
                showarrow=False
            ),
            # Place the score at the bottom center of the chart
            dict(
                text=str(s_score),  # Display the score value
                x=0.5, y=0.25,  # Adjust y to control vertical position
                font=dict(size=28, color="black"),
                showarrow=False
            )
        ],
        margin=dict(t=5, b=5, l=5, r=5),
        height=350 # Reduce margins
    )

    return fig_doughnut_chart_s

def create_doughnut_chart_g(df):
    _, _, _, g_score = get_score(df)
    g_score = float(g_score.iloc[0].round(2))  # Convert to float with two decimal places
    remain_g_score = round(20.57 - g_score, 2)

    fig_doughnut_chart_g = go.Figure()

    # Create the doughnut chart
    fig_doughnut_chart_g.add_trace(go.Pie(
        labels=["G Score", ""],  # Labels
        values=[g_score, remain_g_score],  # Score and remaining score
        hole=0.5,  # Adjusted hole size for a fuller chart
        marker=dict(colors=["#228B22", "#DCDCDC"]),  # Set color for score part
        showlegend=False,  # Disable legend
        textinfo="none",  # Hide default text, use custom text instead
        hoverinfo="label+value",  # Display label and score on hover
        rotation=350
    ))

    # Add "E Score" label at the center
    fig_doughnut_chart_g.update_layout(
        annotations=[
            dict(
                text="G Score",
                x=0.5, y=0.5,
                font=dict(size=30, color="black"),
                showarrow=False
            ),
            # Place the score at the bottom center of the chart
            dict(
                text=str(g_score),  # Display the score value
                x=0.5, y=0.25,  # Adjust y to control vertical position
                font=dict(size=28, color="black"),
                showarrow=False
            )
        ],
        margin=dict(t=5, b=5, l=5, r=5)  # Reduce margins
    )

    return fig_doughnut_chart_g


def create_bar_chart(df):
    import plotly.graph_objects as go

    values = df.iloc[-1].to_dict()
    e_metrics = ['Emission_intensities', 'Energy_consumption_intensity', 'Waste_generated', 'Water_intensity']
    s_metrics = ['Employees_covered_by_health_insurance',
                 'Company_donated', 'Avg_training_hours_per_employee', 'Employees_above_50', 'Female_employees',
                 'Employee_satisfaction_rate', 'New_hires_female', 'New_hires_above_50', 'Total_turnover',
                 'Turnover_female', 'Turnover_above_50', 'Fatalities', 'High_consequence_injuries',
                 'Work_related_injuries']
    g_metrics = ['Board_independence', 'Women_in_management_team', 'Women_on_board']

    # 分别计算 E、S、G 的值
    e_values = [values[metric] for metric in e_metrics]
    s_values = [values[metric] for metric in s_metrics]
    g_values = [values[metric] for metric in g_metrics]

    # 创建柱状图
    fig_bar_chart = go.Figure()

    # E 的柱状图
    fig_bar_chart.add_trace(go.Bar(
        x=e_metrics,
        y=e_values,
        name='E (Environment)',
        marker=dict(color='limegreen'),
        text=e_values,
        textposition='auto',
    ))

    # S 的柱状图
    fig_bar_chart.add_trace(go.Bar(
        x=s_metrics,
        y=s_values,
        name='S (Social)',
        marker=dict(color='lightblue'),
        text=s_values,
        textposition='auto',
    ))

    # G 的柱状图
    fig_bar_chart.add_trace(go.Bar(
        x=g_metrics,
        y=g_values,
        name='G (Governance)',
        marker=dict(color='darkgreen'),
        text=g_values,
        textposition='auto',
    ))

    # 添加标题
    annotations = []

    # 固定 Y 轴的顶部
    fixed_y_position = max(max(e_values), max(s_values), max(g_values)) + 20

    # 添加 E 的标题
    annotations.append(dict(
        x=e_metrics[len(e_metrics) // 2],  # 水平位置居中
        y=fixed_y_position,  # 固定在 Y 轴顶部
        text="E Score",
        showarrow=False,
        font=dict(size=16, color='limegreen', family="Arial Black"),
        xanchor='center'
    ))

    # 添加 S 的标题
    annotations.append(dict(
        x=s_metrics[len(s_metrics) // 2],
        y=fixed_y_position,
        text="S Score",
        showarrow=False,
        font=dict(size=16, color='lightblue', family="Arial Black"),
        xanchor='center'
    ))

    # 添加 G 的标题
    annotations.append(dict(
        x=g_metrics[len(g_metrics) // 2],
        y=fixed_y_position,
        text="G Score",
        showarrow=False,
        font=dict(size=16, color='darkgreen', family="Arial Black"),
        xanchor='center'
    ))

    # 更新布局
    fig_bar_chart.update_layout(
        title='E, S, G Indicators Bar Chart',
        barmode='group',
        xaxis=dict(title='Metrics', tickangle=45),
        showlegend=True,
        margin=dict(t=40, b=100, l=40, r=40),
        font=dict(size=14),
        plot_bgcolor='white',
        paper_bgcolor='white',
        annotations=annotations  # 添加自定义标题
    )

    return fig_bar_chart


def map():
    world = gpd.read_file("../config/wk11_worldmap.geojson")
    cities = gpd.read_file("../config/wk11_cities.geojson")
    singapore = cities[cities["Country"] == "Singapore"]
    us = world[world["SOV_A3"] == "US1"]
    china = world[world["SOV_A3"] == "CH1"]
    fig, ax = plt.subplots(frameon=False)
    world.plot(color="white", edgecolor="lightgray", ax=ax, legend=False)
    singapore.plot(color="limegreen", marker="o", markersize=30, ax=ax)
    us.plot(color="limegreen", ax=ax)
    china.plot(color="limegreen", ax=ax)
    ax.set_axis_off()

    # 将图像保存到缓冲区并转换为 base64
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    buf.close()
    return image_base64


def generate_summary_investors(df):

    # Calculate esg_level
    total_score, e_score, s_score, g_score = get_score(df)
    total_score = total_score.iloc[0]
    e_score = e_score.iloc[0]
    s_score = s_score.iloc[0]
    g_score = g_score.iloc[0]
    esg_level = determine_esg_level(df)
    e_avg = 20.81
    s_avg = 18.89
    g_avg = 12.47
    # indicators
    e_metrics = ['Emission_intensities', 'Energy_consumption_intensity', 'Waste_generated', 'Water_intensity']
    s_metrics = ['Employee_satisfaction_rate', 'Turnover_by_gender', 'Turnover_by_age']
    g_metrics = ['Board_independence', 'Women_in_the management_team', 'Women_on_the_board']
    # average of indicators
    e_avg_metrics = {'Emission_intensities': 0.12, 'Energy_consumption_intensity': 1.96, 'Waste_generated': 339.90,
                     'Water_intensity': 1.84}
    s_avg_metrics = {'Employee_satisfaction_rate': 80, 'Turnover_by_gender': 65.42, 'Turnover_by_age': 16.28}
    g_avg_metrics = {'Board_independence': 60, 'Women_in_the management_team': 42.34, 'Women_on_the_board': 29.68}
    # Default recommendation: for companies with scores above the industry average.
    e_text = f"The score of environmental performance is {e_score.round(2)}."
    e_advice = (
        "The company's environmental performance exceeds the industry average, indicating strong sustainability practices. \n"
        "However, investors should stay attentive to changes in industry regulations and policies. \n"
        "As evolving standards may impact the company's environmental strategies and compliance requirements over time."
    )

    s_text = f"The score of social performance is {s_score.round(2)}."
    s_advice = (
        "The company's social performance surpasses the industry average, reflecting strong relationships with employees, customers, and communities.\n"
        "Investors are encouraged to consider this as a positive factor, \n"
        "but should continue monitoring social metrics to ensure the company maintains high standards in workforce satisfaction and other metrcis."
    )

    g_text = f"The score of governance performance is {g_score.round(2)}."
    g_advice = (
        "The company's governance performance is above industry average, reflecting strong management and accountability. "
        "Investors should monitor governance practices regularly to ensure they continue to align with best practices and protect shareholder interests."
    )

    # Different scenarios
    # Scenario1: e_score > e_avg and s_score > s_avg and g_score > g_avg
    if e_score > e_avg and s_score > s_avg and g_score > g_avg:
        e_text = f"The score of environmental performance is {e_score.round(2)}, which is higher than the average level of the healthcare industry."
        s_text = f"The score of social performance is {s_score.round(2)}, which is higher than the average level of the healthcare industry."
        g_text = f"The score of governance performance is {g_score.round(2)}, which is higher than the average level of the healthcare industry."

        # Step1: Identify the relatively lowest score among three scores
        lowest_score = min(e_score / 33.53, s_score / 45.90, g_score / 20.57)
        # Situation1
        if lowest_score == e_score / 33.53:
            # find the e_metrcis that are lower than industy average
            low_e_metrics = [metric for metric in e_metrics if df[metric].iloc[-1] < e_avg_metrics[metric]]
            if low_e_metrics:
                e_advice = (
                        "Although the overall environmental score is satisfactory, the following environmental indicators are below industry average: "
                        + ", ".join(low_e_metrics) + ". "
                                                     "It is advisable for investors to pay attention to these areas in order to mitigate potential risks."
                )
            else:
                e_advice = (
                    "The company's environmental performance exceeds the industry average, indicating strong sustainability practices. \n"
                    "However, investors should stay attentive to changes in industry regulations and policies. \n"
                    "As evolving standards may impact the company's environmental strategies and compliance requirements over time."
                )

        # Situation2
        if lowest_score == s_score:
            # Identify social indicators of interest to investors that are below industry averages
            low_s_metrics = [metric for metric in s_metrics if df[metric].iloc[-1] < s_avg_metrics[metric]]
            low_s_metrics = []

            # Employee satisfaction rate
            if df['Employee_satisfaction_rate'].iloc[-1] < s_avg_metrics['Employee_satisfaction_rate']:
                low_s_metrics.append('Employee_satisfaction_rate')

            # Turnover by gender (female) and Turnover by age (aged above 50 years old)
            if df['Turnover_by_gender'].iloc[-1] > s_avg_metrics['Turnover_by_gender']:
                low_s_metrics.append('Turnover_by_gender')

            if df['Turnover_by_age'].iloc[-1] > s_avg_metrics['Turnover_by_age']:
                low_s_metrics.append('Turnover_by_age')

            if low_s_metrics:
                s_advice = (
                        "Although the overall social score is satisfactory, the following social indicators are below industry average: "
                        + ", ".join(low_s_metrics) + ". "
                                                     "Investors should monitor these areas for potential social impact risks."
                )
            else:
                s_advice = (
                    "The company's social performance surpasses the industry average, reflecting strong relationships with employees, customers, and communities.\n"
                    "Investors are encouraged to consider this as a positive factor, \n"
                    "but should continue monitoring social metrics to ensure that the company maintains high standards in workforce satisfaction and community engagement over time."
                )

        # Situation3
        if lowest_score == g_score:
            low_g_metrics = [metric for metric in g_metrics if df[metric].iloc[-1] < g_avg_metrics[metric]]

            if low_g_metrics:
                g_advice = (
                        "Although the overall governance score is satisfactory, the following governance indicators are below industry average: "
                        + ", ".join(low_g_metrics) + ". "
                                                     "It is advisable for investors to focus on these specific governance areas to mitigate potential risks."
                )
            else:
                g_advice = (
                    "The company's governance performance is above industry average, reflecting strong management and accountability. \n"
                    "Investors should monitor governance practices regularly to ensure they continue to align with best practices and protect shareholder interests."
                )

    # Scenario2
    elif e_score > e_avg and s_score > s_avg and g_score <= g_avg:
        g_advice = (
            "The company demonstrates strong performance in environmental and social aspects, suggesting good sustainability practices and a positive impact on society.\n "
            "However, governance performance is below the industry average, which may pose potential risks in areas such as transparency, accountability, and decision-making.\n "
            "Investors are advised to carefully assess the company's governance structures, board diversity, and executive accountability measures to mitigate possible risks. \n"
            "Monitoring compliance with ethical standards and industry regulations is also recommended to ensure long-term stability and shareholder value."
        )

    elif e_score > e_avg and s_score <= s_avg and g_score > g_avg:
        s_advice = (
            "The company shows strong performance in environmental and governance aspects, indicating sound sustainability practices and effective management structures.\n"
            "However, social performance is below the industry average, which may point to challenges in areas such as employee satisfaction, workplace safety, and community relations.\n"
            "Investors are advised to assess the company's approach to social responsibility, including employee well-being, diversity, and community relations.\n"
        )

    elif e_score <= e_avg and s_score > s_avg and g_score > g_avg:
        e_advice = (
            "The company exhibits strong performance in social and governance aspects, suggesting effective management structures and a commitment to employee and community well-being.\n"
            "However, environmental performance is below the industry average, which may indicate potential risks related to resource management, carbon emissions, or waste management practices.\n"
            "Investors should evaluate the company's environmental policies and performance, including emissions reduction, energy efficiency, and waste management.\n"
        )

    # Scenario3
    elif e_score > e_avg and s_score <= s_avg and g_score <= g_avg:
        s_advice = (
            "The company shows strong performance in environmental aspects, indicating sound sustainability practices. \n"
            "However, both social and governance performances are below industry average, suggesting potential challenges with employee satisfaction, workplace safety, and governance accountability. \n"
            "Investors should pay more attention to the company's social responsibility initiatives to assess potential risks."
        )
        g_advice = (
            "The company's governance performance is below the industry average, suggesting possible issues with board oversight, transparency, or accountability.\n"
            "Investors are advised to closely examine the company's governance practices to evaluate risks associated with management reliability and long-term corporate stability."
        )

    elif e_score <= e_avg and s_score > s_avg and g_score <= g_avg:
        e_advice = (
            "The company shows strong social performance, suggesting effective workforce management and community relations. \n"
            "However, low environmental and governance scores suggest potential environmental risks and governance challenges. \n"
            "Investors are advised to investigate the company's environmental policies and governance practices to mitigate risks."
        )
        g_advice = (
            "The company's governance performance is below the industry average, which may indicate potential weaknesses in transparency, accountability, or board effectiveness.\n"
            "Investors should consider reviewing the company's governance structures and policies to assess potential risks related to management practices and decision-making processes."
        )

    elif e_score <= e_avg and s_score <= s_avg and g_score > g_avg:
        e_advice = (
            "The company's governance is strong, indicating sound management structures. However, environmental and social performances are below industry average, \n"
            "suggesting potential risks in sustainability and employee relations. Investors should carefully evaluate these aspects before proceeding."
        )
        s_advice = (
            "The company's social performance is below the industry average, indicating potential challenges in areas such as employee satisfaction, workplace safety, or community engagement.\n"
            "Investors may need to assess the company's efforts in improving social responsibility to reduce potential risks associated with workforce stability and public perception."
        )

    # 4. 所有指标都低于行业均值
    else:
        e_advice = (
            "The company's environmental performance is below industry standards, suggesting potential issues in areas such as emissions control, energy efficiency, and waste management.\n"
            "Investors should examine the company's policies for emissions reduction, resource optimization, and waste disposal to assess environmental risk."
        )
        s_advice = (
            "The company's social performance is also below the industry average, indicating potential issues with employee satisfaction, workplace safety, or community relations.\n"
            "Investors should investigate the company's approach to employee welfare, training, safety, and inclusion, as poor social performance can affect morale and public perception."
        )
        g_advice = (
            "Governance scores below the industry average suggest potential weaknesses in corporate transparency, board diversity, or accountability practices.\n"
            "Investors are advised to closely evaluate governance structures, including board independence, accountability, and ethical compliance, \n"
            "as poor governance may lead to misconduct and weaken shareholder value."
        )

    # 生成总结和建议
    summary = (
        f"The score of ESG performance is {total_score.round(2)}, and the ranking in the industry is {esg_level}.\n\n"
        f"- {e_text}\n  {e_advice}\n\n"
        f"- {s_text}\n  {s_advice}\n\n"
        f"- {g_text}\n  {g_advice}\n"
    )
    return summary


def generate_summary_regulators(df):

    # Calculate esg_level
    total_score, e_score, s_score, g_score = get_score(df)
    total_score = total_score.iloc[0]
    e_score = e_score.iloc[0]
    s_score = s_score.iloc[0]
    g_score = g_score.iloc[0]
    esg_level = determine_esg_level(df)
    e_avg = 20.81
    s_avg = 18.89
    g_avg = 12.47
    # indicators
    e_metrics = ['Emission_intensities', 'Energy_consumption_intensity', 'Waste_generated', 'Water_intensity']
    s_metrics = ['Employee_satisfaction_rate', 'Percentage_of_employees_covered_by_health_insurance', 'Company_donated',
                 "Work_related_injuries"]
    g_metrics = ['Board_independence', 'Women_in_the_management_team', 'Women_on_the_board']
    # average of indicators
    e_avg_metrics = {'Emission_intensities': 0.12, 'Energy_consumption_intensity': 1.96, 'Waste_generated': 339.90,
                     'Water_intensity': 1.84}
    s_avg_metrics = {'Employee_satisfaction_rate': 80, 'Company_donated': 466528.25, "Work_related_injuries": 4.7}
    g_avg_metrics = {'Board_independence': 60, 'Women_in_the_management_team': 42.34, 'Women_on_the_board': 29.68}
    # Default recommendation: for companies with scores above the industry average.
    e_text = f"The score of environmental performance is {e_score.round(2)}."
    e_advice = (
        "The company's environmental performance exceeds the industry average, indicating strong sustainability practices.\n"
        "However, regulatory agencies should monitor changes in environmental policies and standards to ensure the company's practices continue to align with evolving requirements.\n"
        "Attention should be given to the company's ability to adapt its environmental strategies to comply with regulatory updates."
    )

    s_text = f"The score of social performance is {s_score.round(2)}."
    s_advice = (
        "The company's social performance surpasses the industry average, reflecting strong relationships with employees, customers, and communities.\n"
        "Regulatory agencies should encourage the company to maintain these standards, while also monitoring any fluctuations in workforce satisfaction and other social metrics."
    )

    g_text = f"The score of governance performance is {g_score.round(2)}."
    g_advice = (
        "The company's governance performance is above the industry average, reflecting strong management and accountability.\n"
        "Regulatory bodies should continue to ensure that governance practices align with industry standards, focusing on transparency, accountability, and compliance with ethical guidelines."
    )

    # Different scenarios
    # Scenario1: e_score > e_avg and s_score > s_avg and g_score > g_avg
    if e_score > e_avg and s_score > s_avg and g_score > g_avg:
        e_text = f"The score of environmental performance is {e_score.round(2)}, which is higher than the average level of the healthcare industry."
        s_text = f"The score of social performance is {s_score.round(2)}, which is higher than the average level of the healthcare industry."
        g_text = f"The score of governance performance is {g_score.round(2)}, which is higher than the average level of the healthcare industry."

        # Step1: Identify the relatively lowest score among three scores
        lowest_score = min(e_score / 33.53, s_score / 45.90, g_score / 20.57)

        # Situation1
        if lowest_score == e_score / 33.53:
            low_e_metrics = [metric for metric in e_metrics if df[metric].iloc[-1] < e_avg_metrics[metric]]
            if low_e_metrics:
                e_advice = (
                        "Although the company's overall environmental performance is strong, the following environmental indicators are below industry average: "
                        + ", ".join(low_e_metrics) + ".\n"
                                                     "Regulatory agencies should pay close attention to these areas to encourage improvement and ensure the company remains compliant with environmental standards."
                )
            else:
                e_advice = (
                    "The company's environmental performance exceeds the industry average, indicating strong sustainability practices.\n"
                    "However, regulatory agencies should monitor changes in environmental policies to ensure continued alignment with updated standards."
                )

        # Situation2
        if lowest_score == s_score / 45.90:
            low_s_metrics = []

            if df['Employee_satisfaction_rate'].iloc[-1] < s_avg_metrics['Employee_satisfaction_rate']:
                low_s_metrics.append('Employee_satisfaction_rate')

            if df['Company_donated'].iloc[-1] < s_avg_metrics['Company_donated']:
                low_s_metrics.append('Company_donated')

            if df["Work_related_injuries"].iloc[-1] > s_avg_metrics["Work_related_injuries"]:
                low_s_metrics.append("Work_related_injuries")

            if low_s_metrics:
                s_advice = (
                        "Although the company's social performance is generally strong, the following social indicators are below industry average: "
                        + ", ".join(low_s_metrics) + ".\n"
                                                     "Regulatory agencies should monitor these areas to ensure the company addresses any underlying issues and promotes a healthy social environment."
                )
            else:
                s_advice = (
                    "The company's social performance surpasses the industry average, reflecting strong relationships with employees, customers, and communities.\n"
                    "Regulatory agencies should encourage the company to maintain these standards, while monitoring any significant changes."
                )

        # Situation3
        if lowest_score == g_score / 20.57:
            low_g_metrics = [metric for metric in g_metrics if df[metric].iloc[-1] < g_avg_metrics[metric]]

            if low_g_metrics:
                g_advice = (
                        "Although the company's governance score is generally high, the following governance indicators are below industry average: "
                        + ", ".join(low_g_metrics) + ".\n"
                                                     "Regulatory agencies should focus on these governance aspects to promote accountability and prevent potential risks."
                )
            else:
                g_advice = (
                    "The company's governance performance is above industry average, reflecting strong management and accountability.\n"
                    "Regulatory agencies should ensure these practices align with industry standards for sustainable growth and compliance."
                )

    # Other Scenarios
    elif e_score > e_avg and s_score > s_avg and g_score <= g_avg:
        g_advice = (
            "The company demonstrates strong performance in environmental and social aspects, which reflects positively on its sustainability practices.\n"
            "However, governance performance is below industry average. Regulatory agencies should review the company's governance structures to improve transparency, accountability, and decision-making processes."
        )

    elif e_score > e_avg and s_score <= s_avg and g_score > g_avg:
        s_advice = (
            "The company shows strength in environmental and governance aspects, but social performance is below industry average.\n"
            "Regulatory agencies should assess the company's social responsibility initiatives, particularly around workforce satisfaction, to encourage improvement."
        )

    elif e_score <= e_avg and s_score > s_avg and g_score > g_avg:
        e_advice = (
            "The company performs well in social and governance aspects, but its environmental performance is below industry average.\n"
            "Regulatory agencies should focus on the company's environmental practices to ensure alignment with industry standards and encourage sustainable improvements."
        )

    elif e_score > e_avg and s_score <= s_avg and g_score <= g_avg:
        s_advice = (
            "The company has strong environmental practices, but social and governance performances are below industry average.\n"
            "Regulatory agencies should emphasize improvements in social responsibility and governance accountability."
        )
        g_advice = (
            "The company's governance is below industry average, indicating potential issues with oversight and transparency.\n"
            "Regulatory agencies should examine governance practices to mitigate management and compliance risks."
        )

    elif e_score <= e_avg and s_score > s_avg and g_score <= g_avg:
        e_advice = (
            "The company demonstrates good social performance, but its environmental and governance scores are below average.\n"
            "Regulatory agencies should prioritize improvements in environmental practices and governance mechanisms."
        )
        g_advice = (
            "With governance performance below the industry average, regulatory agencies should assess the company’s governance structures to address potential accountability issues."
        )

    elif e_score <= e_avg and s_score <= s_avg and g_score > g_avg:
        e_advice = (
            "The company's governance is strong, but its environmental and social performances are below industry average.\n"
            "Regulatory agencies should consider interventions to improve the company's sustainability and social responsibility efforts."
        )
        s_advice = (
            "The company's social performance falls short of industry standards, indicating areas for improvement in employee and community relations.\n"
            "Regulatory agencies should encourage efforts in these areas to improve social impact."
        )

    # All Scores Below Industry Average
    else:
        e_advice = (
            "The company's environmental performance is below industry standards, suggesting possible issues with emissions, energy efficiency, and waste management.\n"
            "Regulatory agencies should work with the company to address these issues and improve its environmental impact."
        )
        s_advice = (
            "The company's social performance is also below industry average, which may indicate issues with employee satisfaction and community engagement.\n"
            "Regulatory agencies should encourage improvements in social responsibility and workplace conditions."
        )
        g_advice = (
            "The company's governance is below industry standards, highlighting potential weaknesses in transparency, accountability, and ethical compliance.\n"
            "Regulatory agencies should review and promote better governance practices to safeguard shareholder interests."
        )

    # Generate summary and suggestions
    summary = (
        f"The score of ESG performance is {total_score.round(2)}, and the ranking in the industry is {esg_level}.\n\n"
        f"- {e_text}\n  {e_advice}\n\n"
        f"- {s_text}\n  {s_advice}\n\n"
        f"- {g_text}\n  {g_advice}\n"
    )
    return summary


def generate_summary_management(df):

    # Calculate esg_level
    total_score, e_score, s_score, g_score = get_score(df)
    total_score = total_score.iloc[0]
    e_score = e_score.iloc[0]
    s_score = s_score.iloc[0]
    g_score = g_score.iloc[0]
    esg_level = determine_esg_level(df)
    e_avg = 20.81
    s_avg = 18.89
    g_avg = 12.47
    # indicators
    e_metrics = ['Emission_intensities', 'Energy_consumption_intensity', 'Waste_generated', 'Water_intensity']
    s_metrics = ['Employee_satisfaction_rate', 'Percentage_of_employees_covered_by_health_insurance', 'Company_donated',
                 "Work_related_injuries"]
    g_metrics = ['Board_independence', 'Women_in_the_management_team', 'Women_on_the_board']
    # average of indicators
    e_avg_metrics = {'Emission_intensities': 0.12, 'Energy_consumption_intensity': 1.96, 'Waste_generated': 339.90,
                     'Water_intensity': 1.84}
    s_avg_metrics = {'Employee_satisfaction_rate': 80, 'Company_donated': 466528.25, "Work_related_injuries": 4.7}
    g_avg_metrics = {'Board_independence': 60, 'Women_in_the_management_team': 42.34, 'Women_on_the_board': 29.68}

    # Default recommendation: for companies with scores above the industry average.
    e_text = f"The score of environmental performance is {e_score.round(2)}."
    e_advice = (
        "The company's environmental performance exceeds the industry average, demonstrating strong sustainability practices.\n"
        "Management should continue to monitor environmental regulations and industry standards to ensure compliance and maintain leadership in environmental responsibility.\n"
        "It's essential to adapt environmental strategies proactively to align with potential regulatory changes."
    )

    s_text = f"The score of social performance is {s_score.round(2)}."
    s_advice = (
        "The company's social performance surpasses the industry average, reflecting positive relations with employees, customers, and communities.\n"
        "Management should focus on maintaining these standards and consider enhancing social initiatives to further strengthen workforce satisfaction and community engagement."
    )

    g_text = f"The score of governance performance is {g_score.round(2)}."
    g_advice = (
        "The company's governance performance is above industry average, indicating strong management and accountability structures.\n"
        "Management should regularly review governance policies to ensure they align with best practices and reinforce transparency and ethical compliance across all levels."
    )

    # Different scenarios
    # Scenario1: e_score > e_avg and s_score > s_avg and g_score > g_avg
    if e_score > e_avg and s_score > s_avg and g_score > g_avg:
        e_text = f"The score of environmental performance is {e_score.round(2)}, which is higher than the average level of the healthcare industry."
        s_text = f"The score of social performance is {s_score.round(2)}, which is higher than the average level of the healthcare industry."
        g_text = f"The score of governance performance is {g_score.round(2)}, which is higher than the average level of the healthcare industry."

        # Step1: Identify the relatively lowest score among three scores
        lowest_score = min(e_score / 33.53, s_score / 45.90, g_score / 20.57)

        # Situation1
        if lowest_score == e_score / 33.53:
            low_e_metrics = [metric for metric in e_metrics if df[metric].iloc[-1] < e_avg_metrics[metric]]
            if low_e_metrics:
                e_advice = (
                        "Although the company's environmental performance is strong overall, the following environmental metrics are below the industry average: "
                        + ", ".join(low_e_metrics) + ".\n"
                                                     "Management should focus on improving these specific areas to ensure comprehensive environmental leadership."
                )
            else:
                e_advice = (
                    "The company's environmental performance exceeds the industry average. Management should continue to monitor environmental policies to ensure ongoing compliance and proactive alignment with regulatory standards."
                )

        # Situation2
        if lowest_score == s_score / 45.90:
            low_s_metrics = []

            if df['Employee_satisfaction_rate'].iloc[-1] < s_avg_metrics['Employee_satisfaction_rate']:
                low_s_metrics.append('Employee_satisfaction_rate')

            if df['Company_donated'].iloc[-1] < s_avg_metrics['Company_donated']:
                low_s_metrics.append('Company_donated')

            if df["Work_related_injuries"].iloc[-1] > s_avg_metrics["Work_related_injuries"]:
                low_s_metrics.append("Work_related_injuries")

            if low_s_metrics:
                s_advice = (
                        "While the company's social performance is strong overall, the following social metrics are below industry average: "
                        + ", ".join(low_s_metrics) + ".\n"
                                                     "Management should address these areas to promote a healthier work environment and stronger community relations."
                )
            else:
                s_advice = (
                    "The company's social performance surpasses the industry average. Management should maintain these standards while proactively monitoring any shifts in employee or community relations."
                )

        # Situation3
        if lowest_score == g_score / 20.57:
            low_g_metrics = [metric for metric in g_metrics if df[metric].iloc[-1] < g_avg_metrics[metric]]

            if low_g_metrics:
                g_advice = (
                        "Although the company's governance is strong overall, the following governance metrics are below industry average: "
                        + ", ".join(low_g_metrics) + ".\n"
                                                     "Management should focus on improving these areas to strengthen transparency and accountability."
                )
            else:
                g_advice = (
                    "The company's governance performance is above industry average. Management should continue to align governance practices with industry best practices to maintain a robust accountability structure."
                )

    # Other Scenarios
    elif e_score > e_avg and s_score > s_avg and g_score <= g_avg:
        g_advice = (
            "The company shows strong environmental and social performance, indicating solid sustainability practices.\n"
            "However, governance performance is below industry average. Management should focus on enhancing governance structures to improve transparency and decision-making processes."
        )

    elif e_score > e_avg and s_score <= s_avg and g_score > g_avg:
        s_advice = (
            "The company demonstrates strength in environmental and governance aspects, but social performance is below industry average.\n"
            "Management should consider bolstering social responsibility efforts, particularly focusing on workforce satisfaction and community engagement."
        )

    elif e_score <= e_avg and s_score > s_avg and g_score > g_avg:
        e_advice = (
            "The company performs well in social and governance aspects, but environmental performance is below industry average.\n"
            "Management should review environmental policies and practices to align with industry standards and drive improvement."
        )

    elif e_score > e_avg and s_score <= s_avg and g_score <= g_avg:
        s_advice = (
            "The company shows strong environmental practices, but social and governance performances are below industry average.\n"
            "Management should prioritize improvements in social responsibility and governance accountability to mitigate potential risks."
        )
        g_advice = (
            "Governance performance is below industry average, suggesting potential gaps in oversight and transparency.\n"
            "Management should reinforce governance practices to improve accountability and strengthen corporate integrity."
        )

    elif e_score <= e_avg and s_score > s_avg and g_score <= g_avg:
        e_advice = (
            "The company demonstrates good social performance, but its environmental and governance scores are below average.\n"
            "Management should enhance environmental policies and governance structures to support long-term resilience and regulatory alignment."
        )
        g_advice = (
            "With governance performance below industry average, management should review and strengthen governance structures to address accountability issues."
        )

    elif e_score <= e_avg and s_score <= s_avg and g_score > g_avg:
        e_advice = (
            "The company's governance is strong, but its environmental and social performances are below industry average.\n"
            "Management should invest in improving sustainability practices and social responsibility to better meet industry standards."
        )
        s_advice = (
            "The company's social performance falls short of industry standards, indicating potential challenges in workforce and community relations.\n"
            "Management should address these areas to enhance social impact and company reputation."
        )

    # All Scores Below Industry Average
    else:
        e_advice = (
            "The company's environmental performance is below industry standards, suggesting potential issues in emissions control, energy efficiency, and waste management.\n"
            "Management should focus on implementing sustainable practices to improve environmental impact and compliance."
        )
        s_advice = (
            "The company's social performance is also below industry average, indicating possible issues with employee satisfaction and community engagement.\n"
            "Management should work to improve social initiatives and strengthen relationships with both employees and the broader community."
        )
        g_advice = (
            "Governance performance is below industry standards, highlighting potential weaknesses in transparency and accountability.\n"
            "Management should strengthen governance practices to improve oversight, accountability, and alignment with ethical standards."
        )

    # Generate summary and suggestions
    summary = (
        f"The score of ESG performance is {total_score.round(2)}, and the ranking in the industry is {esg_level}.\n\n"
        f"- {e_text}\n  {e_advice}\n\n"
        f"- {s_text}\n  {s_advice}\n\n"
        f"- {g_text}\n  {g_advice}\n"
    )
    return summary


import plotly.graph_objects as go

def create_bar_chart_small(df, title):
    total_score, e_score, s_score, g_score = get_score(df)

    # 确保提取到的分数是数值类型
    if title == 'Environment':
        industry_score = 18.65
        score = e_score.iloc[0] if isinstance(e_score, pd.Series) else e_score
    elif title == 'Social':
        industry_score = 13.50
        score = s_score.iloc[0] if isinstance(s_score, pd.Series) else s_score
    elif title == 'Governance':
        industry_score = 19.98
        score = g_score.iloc[0] if isinstance(g_score, pd.Series) else g_score

    fig_bar = go.Figure()

    # 创建柱状图
    fig_bar.add_trace(go.Bar(
        x=[title],
        y=[score],
        name=f"{title} Score",
        marker=dict(color="lightgreen"),
        width=0.4  # 使柱子稍微变窄，留出空间
    ))

    # 添加行业基准分数线
    fig_bar.add_shape(
        type="line",
        x0=-0.2, x1=0.2,  # 控制线的长度
        y0=industry_score, y1=industry_score,
        line=dict(color="darkgreen", width=2, dash="dash"),
    )

    # 调整标注位置，避免重叠
    fig_bar.add_annotation(
        x=0,  # 水平居中
        y=industry_score + 1,  # 将标注上移，避免与基准线重叠
        text="Industry Score",
        showarrow=False,
        font=dict(color="darkgreen", size=12, family="Times New Roman"),
        xanchor="center",
        yanchor="bottom"  # 让标注在基准线上方
    )

    # 设置布局和尺寸
    fig_bar.update_layout(
        yaxis_title="Score",

        showlegend=False,  # 隐藏图例
        plot_bgcolor="white",
        font=dict(color="darkgreen", size=12, family="Times New Roman"),
        height=325,  # 调整图表高度
        width=275,  # 调整图表宽度
        margin=dict(l=10, r=10, t=30, b=20),  # 控制边距
        yaxis_range=[0, max(float(score), industry_score) + 5],  # 增加顶部空间
    )

    return fig_bar


def suggestion(df):
    recommendations = []
    # 获取需要的指标值，确保每个指标都是单个数值
    emission_intensity = df["Emission_intensities"].iloc[-1]
    energy_consumption_intensity = df["Energy_consumption_intensity"].iloc[-1]
    waste_generated = df["Waste_generated"].iloc[-1]
    water_intensity = df["Water_intensity"].iloc[-1]
    board_independence = df["Board_independence"].iloc[-1]
    women_in_management = df["Women_in_management_team"].iloc[-1]
    women_on_board = df["Women_on_board"].iloc[-1]
    health_insurance_coverage = df["Employees_covered_by_health_insurance"].iloc[-1]
    company_donated = df["Company_donated"].iloc[-1]
    training_hours = df["Avg_training_hours_per_employee"].iloc[-1]
    employee_satisfaction = df["Employee_satisfaction_rate"].iloc[-1]
    current_employees_by_age_groups = df["Employees_above_50"].iloc[-1]
    current_employees_by_gender = df["Female_employees"].iloc[-1]
    new_hires_by_gender = df["New_hires_female"].iloc[-1]
    new_hires_by_age = df["New_hires_above_50"].iloc[-1]
    turnover_by_gender = df["Turnover_female"].iloc[-1]
    turnover_by_age = df["Turnover_above_50"].iloc[-1]
    total_turnover = df["Total_turnover"].iloc[-1]
    fatalities = df["Fatalities"].iloc[-1]
    high_consequence_injuries = df["High_consequence_injuries"].iloc[-1]
    work_related_injuries = df["Work_related_injuries"].iloc[-1]

    recommendations.append("The company has issues in the following indicators:")
    if emission_intensity == 0:
        recommendations.append(
            "If Emission intensities reach 0.18(tCO2e/revenue S$'000), ESG score increases by 0.8 points, revenue increases by 0.66k USD.")
    elif emission_intensity == 25:
        recommendations.append(
            "If Emission intensities reach 0.14(tCO2e/revenue S$'000), ESG score increases by 0.8 points, revenue increases by 0.66k USD.")

    if energy_consumption_intensity == 0:
        recommendations.append(
            "If Energy consumption intensity reach 2.94(MWh/revenue S$'000), ESG score increases by 0.75 points, revenue increases by 0.62k USD.")
    elif energy_consumption_intensity == 25:
        recommendations.append(
            "If Energy consumption intensity reach 2.35(MWh/revenue S$'000), ESG score increases by 0.75 points, revenue increases by 0.62k USD.")

    if waste_generated == 0:
        recommendations.append(
            "If Waste generated reach 508.5(metric ton), ESG score increases by 0.82 points, revenue increases by 0.68k USD.")
    elif waste_generated == 25:
        recommendations.append(
            "If Waste generated reach 406.8(metric ton), ESG score increases by 0.82 points, revenue increases by 0.68k USD.")

    if water_intensity == 0:
        recommendations.append(
            "If Water intensity reach 2.76(Cu M/revenue S$'000), ESG score increases by 0.37 points, revenue increases by 0.31k USD.")
    elif water_intensity == 25:
        recommendations.append(
            "If Water intensity reach 2.21(Cu M/revenue S$'000), ESG score increases by 0.37 points, revenue increases by 0.31k USD.")

    if board_independence == 0:
        recommendations.append(
            "If Board independence reach 30(%), ESG score increases by 0.19 points, revenue increases by 0.15k USD.")
    elif board_independence == 25:
        recommendations.append(
            "If Board independence reach 48(%), ESG score increases by 0.19 points, revenue increases by 0.15k USD.")

    if women_in_management == 0:
        recommendations.append(
            "If Women in the management team reach 21.17(%), ESG score increases by 0.95 points, revenue increases by 0.78k USD.")
    elif women_in_management == 25:
        recommendations.append(
            "If Women in the management team reach 33.87(%), ESG score increases by 0.95 points, revenue increases by 0.78k USD.")

    if women_on_board == 0:
        recommendations.append(
            "If Women on the board reach 14.84(%), ESG score increases by 0.02 points, revenue increases by 0.02k USD.")
    elif women_on_board == 25:
        recommendations.append(
            "If Women on the board reach 23.74(%), ESG score increases by 0.02 points, revenue increases by 0.02k USD.")

    if health_insurance_coverage == 0:
        recommendations.append(
            "If Percentage of employees covered by health insurance reach 50(%), ESG score increases by 0.41 points, revenue increases by 0.34k USD.")
    elif health_insurance_coverage == 25:
        recommendations.append(
            "If Percentage of employees covered by health insurance reach 80(%), ESG score increases by 0.41 points, revenue increases by 0.34k USD.")

    if company_donated == 0:
        recommendations.append(
            "If Company donated reach 233264.13(S$), ESG score increases by 0.07 points, revenue increases by 0.06k USD.")
    elif company_donated == 25:
        recommendations.append(
            "If Company donated reach 373222.6(S$), ESG score increases by 0.07 points, revenue increases by 0.06k USD.")

    if training_hours == 0:
        recommendations.append(
            "If Average training hours per employee reach 13.4(Hours), ESG score increases by 0.86 points, revenue increases by 0.71k USD.")
    elif training_hours == 25:
        recommendations.append(
            "If Average training hours per employee reach 21.45(Hours), ESG score increases by 0.86 points, revenue increases by 0.71k USD.")

    if employee_satisfaction == 0:
        recommendations.append(
            "If Employee satisfaction rate reach 40(%), ESG score increases by 0.47 points, revenue increases by 0.38k USD.")
    elif employee_satisfaction == 25:
        recommendations.append(
            "If Employee satisfaction rate reach 64(%), ESG score increases by 0.47 points, revenue increases by 0.38k USD.")

    if current_employees_by_age_groups == 0:
        recommendations.append(
            "If Current employees by age groups reach 8.93-26.78(%), ESG score increases by 2.2 points, revenue increases by 1.81k USD.")
    elif current_employees_by_age_groups == 50:
        recommendations.append(
            "If Current employees by age groups reach 14.28-21.42(%), ESG score increases by 2.2 points, revenue increases by 1.81k USD.")

    if current_employees_by_gender == 0:
        recommendations.append(
            "If Current employees by gender reach 28.71-86.12(%), ESG score increases by 2.57 points, revenue increases by 2.12k USD.")
    elif current_employees_by_gender == 50:
        recommendations.append(
            "If Current employees by gender reach 45.93-68.89(%), ESG score increases by 2.57 points, revenue increases by 2.12k USD.")

    if new_hires_by_gender == 0:
        recommendations.append(
            "If New hires by gender reach 26.77-80.30(%), ESG score increases by 0.9 points, revenue increases by 0.75k USD.")
    elif new_hires_by_gender == 50:
        recommendations.append(
            "If New hires by gender reach 42.82-64.24(%), ESG score increases by 0.9 points, revenue increases by 0.75k USD.")

    if new_hires_by_age == 0:
        recommendations.append(
            "If New hires by age reach 6.43-19.28(%), ESG score increases by 0.77 points, revenue increases by 0.64k USD.")
    elif new_hires_by_age == 50:
        recommendations.append(
            "If New hires by age reach 10.28-15.42(%), ESG score increases by 0.77 points, revenue increases by 0.64k USD.")

    if turnover_by_gender == 0:
        recommendations.append(
            "If Turnover by gender reach 32.71-98.13(%), ESG score increases by 1.14 points, revenue increases by 0.95k USD.")
    elif turnover_by_gender == 50:
        recommendations.append(
            "If Turnover by gender reach 52.34-78.50(%), ESG score increases by 1.14 points, revenue increases by 0.95k USD.")

    if turnover_by_age == 0:
        recommendations.append(
            "If Turnover by age reach 8.14-24.42(%), ESG score increases by 0.98 points, revenue increases by 0.81k USD.")
    elif turnover_by_age == 50:
        recommendations.append(
            "If Turnover by age reach 13.02-19.54(%), ESG score increases by 0.98 points, revenue increases by 0.81k USD.")

    if total_turnover == 0:
        recommendations.append(
            "If Total turnover reach 0-30(%), ESG score increases by 2.12 points, revenue increases by 1.75k USD.")
    elif total_turnover == 50:
        recommendations.append(
            "If Total turnover reach 10-20(%), ESG score increases by 2.12 points, revenue increases by 1.75k USD.")

    if fatalities == 0:
        recommendations.append(
            "If Fatalities reach 0(number), ESG score increases by 1.71 points, revenue increases by 1.41k USD.")
    elif fatalities == 50:
        recommendations.append(
            "If Fatalities reach (number), ESG score increases by 1.71 points, revenue increases by 1.41k USD.")

    if high_consequence_injuries == 0:
        recommendations.append(
            "If High consequence injuries reach 0(number), ESG score increases by 1.12 points, revenue increases by 0.92k USD.")
    elif high_consequence_injuries == 50:
        recommendations.append(
            "If High consequence injuries reach (number), ESG score increases by 1.12 points, revenue increases by 0.92k USD.")

    if work_related_injuries == 0:
        recommendations.append(
            "If Work related injuries reach 1-2(number), ESG score increases by 2.05 points, revenue increases by 1.69k USD.")
    elif work_related_injuries == 50:
        recommendations.append(
            "If Work related injuries reach 0(number), ESG score increases by 2.05 points, revenue increases by 1.69k USD.")

    # 返回所有建议作为一个字符串
    return "\n".join(recommendations)