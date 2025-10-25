"""
Visualization module for TAM/SAM/SOM analysis
Creates professional charts and graphs
"""

import plotly.graph_objects as go
from typing import Dict, Any


def create_market_funnel_chart(analysis: Dict[str, Any]) -> go.Figure:
    """
    Create a funnel chart showing TAM/SAM/SOM for 2024.
    
    Args:
        analysis: TAM/SAM/SOM analysis dictionary
        
    Returns:
        Plotly figure object
    """
    tam_2024 = analysis['TAM']['numbers']['2024']
    sam_2024 = analysis['SAM']['numbers']['2024']
    som_2024 = analysis['SOM']['numbers']['2024']
    
    fig = go.Figure()
    
    fig.add_trace(go.Funnel(
        name='2024',
        y=['TAM', 'SAM', 'SOM'],
        x=[tam_2024, sam_2024, som_2024],
        textposition="inside",
        textinfo="value+percent initial",
        marker=dict(color=['#3498db', '#2ecc71', '#f39c12']),
        connector=dict(line=dict(color='#7f8c8d', dash='dot', width=3))
    ))
    
    fig.update_layout(
        title="Market Funnel Analysis - 2024",
        height=400,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def create_growth_chart(analysis: Dict[str, Any]) -> go.Figure:
    """
    Create a line chart showing growth projections over time.
    
    Args:
        analysis: TAM/SAM/SOM analysis dictionary
        
    Returns:
        Plotly figure object
    """
    years = list(range(2024, 2031))
    tam_values = [analysis['TAM']['numbers'][str(year)] for year in years]
    sam_values = [analysis['SAM']['numbers'][str(year)] for year in years]
    som_values = [analysis['SOM']['numbers'][str(year)] for year in years]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=years, y=tam_values,
        mode='lines+markers',
        name='TAM',
        line=dict(color='#3498db', width=3),
        marker=dict(size=8),
        hovertemplate='<b>TAM</b><br>Year: %{x}<br>Size: %{y:,}<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=years, y=sam_values,
        mode='lines+markers',
        name='SAM',
        line=dict(color='#2ecc71', width=3),
        marker=dict(size=8),
        hovertemplate='<b>SAM</b><br>Year: %{x}<br>Size: %{y:,}<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=years, y=som_values,
        mode='lines+markers',
        name='SOM',
        line=dict(color='#f39c12', width=3),
        marker=dict(size=8),
        hovertemplate='<b>SOM</b><br>Year: %{x}<br>Size: %{y:,}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Market Size Projections (2024-2030)",
        xaxis_title="Year",
        yaxis_title="Market Size",
        height=450,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor='#e0e0e0'),
        yaxis=dict(gridcolor='#e0e0e0')
    )
    
    return fig


def create_comparison_chart(analysis: Dict[str, Any]) -> go.Figure:
    """
    Create a bar chart comparing 2024 vs 2030.
    
    Args:
        analysis: TAM/SAM/SOM analysis dictionary
        
    Returns:
        Plotly figure object
    """
    categories = ['TAM', 'SAM', 'SOM']
    values_2024 = [
        analysis['TAM']['numbers']['2024'],
        analysis['SAM']['numbers']['2024'],
        analysis['SOM']['numbers']['2024']
    ]
    values_2030 = [
        analysis['TAM']['numbers']['2030'],
        analysis['SAM']['numbers']['2030'],
        analysis['SOM']['numbers']['2030']
    ]
    
    fig = go.Figure(data=[
        go.Bar(
            name='2024',
            x=categories,
            y=values_2024,
            marker_color='#3498db',
            text=values_2024,
            texttemplate='%{text:,}',
            textposition='outside'
        ),
        go.Bar(
            name='2030',
            x=categories,
            y=values_2030,
            marker_color='#2ecc71',
            text=values_2030,
            texttemplate='%{text:,}',
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title="Market Comparison: 2024 vs 2030",
        barmode='group',
        height=400,
        xaxis_title="Market Segment",
        yaxis_title="Market Size",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor='#e0e0e0'),
        yaxis=dict(gridcolor='#e0e0e0')
    )
    
    return fig


def create_growth_rate_chart(analysis: Dict[str, Any]) -> go.Figure:
    """
    Create a chart showing year-over-year growth rates.
    
    Args:
        analysis: TAM/SAM/SOM analysis dictionary
        
    Returns:
        Plotly figure object
    """
    years = list(range(2025, 2031))
    
    def calculate_growth_rates(numbers_dict):
        rates = []
        for i in range(len(years)):
            current_year = str(2024 + i + 1)
            prev_year = str(2024 + i)
            current = numbers_dict[current_year]
            previous = numbers_dict[prev_year]
            growth = ((current - previous) / previous) * 100 if previous > 0 else 0
            rates.append(growth)
        return rates
    
    tam_growth = calculate_growth_rates(analysis['TAM']['numbers'])
    sam_growth = calculate_growth_rates(analysis['SAM']['numbers'])
    som_growth = calculate_growth_rates(analysis['SOM']['numbers'])
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='TAM Growth',
        x=years,
        y=tam_growth,
        marker_color='#3498db'
    ))
    
    fig.add_trace(go.Bar(
        name='SAM Growth',
        x=years,
        y=sam_growth,
        marker_color='#2ecc71'
    ))
    
    fig.add_trace(go.Bar(
        name='SOM Growth',
        x=years,
        y=som_growth,
        marker_color='#f39c12'
    ))
    
    fig.update_layout(
        title="Year-over-Year Growth Rate (%)",
        xaxis_title="Year",
        yaxis_title="Growth Rate (%)",
        barmode='group',
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor='#e0e0e0'),
        yaxis=dict(gridcolor='#e0e0e0')
    )
    
    return fig

def create_cost_breakdown_chart(yearly_breakdown):
    """Create a stacked bar chart showing cost breakdown by year"""
    years = [item['year'] for item in yearly_breakdown]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Development',
        x=years,
        y=[item['one_time_development'] for item in yearly_breakdown],
        marker_color='#1f77b4'
    ))
    
    fig.add_trace(go.Bar(
        name='Customer Acquisition',
        x=years,
        y=[item['customer_acquisition'] for item in yearly_breakdown],
        marker_color='#ff7f0e'
    ))
    
    fig.add_trace(go.Bar(
        name='Distribution',
        x=years,
        y=[item['distribution_operations'] for item in yearly_breakdown],
        marker_color='#2ca02c'
    ))
    
    fig.add_trace(go.Bar(
        name='After Sales',
        x=years,
        y=[item['after_sales'] for item in yearly_breakdown],
        marker_color='#d62728'
    ))
    
    fig.add_trace(go.Bar(
        name='COGS',
        x=years,
        y=[item['total_cogs'] for item in yearly_breakdown],
        marker_color='#9467bd'
    ))
    
    fig.update_layout(
        title="Cost Breakdown by Year",
        xaxis_title="Year",
        yaxis_title="Cost ($)",
        barmode='stack',
        height=500,
        hovermode='x unified'
    )
    
    return fig

def create_cost_per_unit_chart(yearly_breakdown):
    """Create a line chart showing COGS per unit over time"""
    years = [item['year'] for item in yearly_breakdown]
    cogs_per_unit = [item['cogs_per_unit'] for item in yearly_breakdown]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=years,
        y=cogs_per_unit,
        mode='lines+markers',
        name='COGS per Unit',
        line=dict(color='#e74c3c', width=3),
        marker=dict(size=10)
    ))
    
    fig.update_layout(
        title="Cost of Goods Sold per Unit Over Time",
        xaxis_title="Year",
        yaxis_title="COGS per Unit ($)",
        height=400,
        hovermode='x'
    )
    
    return fig

def create_total_cost_chart(yearly_breakdown):
    """Create a line chart showing total costs over time"""
    years = [item['year'] for item in yearly_breakdown]
    total_costs = [item['total_cost'] for item in yearly_breakdown]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=years,
        y=total_costs,
        mode='lines+markers',
        name='Total Cost',
        line=dict(color='#3498db', width=3),
        marker=dict(size=10),
        fill='tozeroy'
    ))
    
    fig.update_layout(
        title="Total Costs Over Time",
        xaxis_title="Year",
        yaxis_title="Total Cost ($)",
        height=400,
        hovermode='x'
    )
    
    return fig


def create_income_chart(yearly_projections: list, model_type: str) -> go.Figure:
    """
    Create a line chart showing income projections over time.
    
    Args:
        yearly_projections: List of yearly projection dictionaries
        model_type: Type of income model (Royalties, Subscription, Single Buy)
        
    Returns:
        Plotly figure object
    """
    years = [str(proj.get('year', '')) for proj in yearly_projections]
    incomes = [proj.get('yearly_income', 0) for proj in yearly_projections]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=years,
        y=incomes,
        mode='lines+markers',
        name='Yearly Income',
        line=dict(color='#27ae60', width=3),
        marker=dict(size=12, color='#27ae60'),
        fill='tozeroy',
        fillcolor='rgba(39, 174, 96, 0.2)'
    ))
    
    fig.update_layout(
        title=f"{model_type} Income Projections",
        xaxis_title="Year",
        yaxis_title="Income (€)",
        height=450,
        hovermode='x unified',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        yaxis=dict(tickformat=',.0f', tickprefix='€')
    )
    
    return fig


def create_income_comparison_chart(yearly_projections: list, cost_breakdown: dict, model_type: str) -> go.Figure:
    """
    Create a chart comparing income vs costs over time.
    
    Args:
        yearly_projections: List of yearly income projection dictionaries
        cost_breakdown: Dictionary of yearly cost breakdown
        model_type: Type of income model
        
    Returns:
        Plotly figure object
    """
    years = [str(proj.get('year', '')) for proj in yearly_projections]
    incomes = [proj.get('yearly_income', 0) for proj in yearly_projections]
    costs = [cost_breakdown.get(year, {}).get('total_cost', 0) for year in years]
    profits = [inc - cost for inc, cost in zip(incomes, costs)]
    
    fig = go.Figure()
    
    # Income bars
    fig.add_trace(go.Bar(
        name='Income',
        x=years,
        y=incomes,
        marker_color='#27ae60',
        text=[f'€{val:,.0f}' for val in incomes],
        textposition='outside'
    ))
    
    # Cost bars
    fig.add_trace(go.Bar(
        name='Costs',
        x=years,
        y=costs,
        marker_color='#e74c3c',
        text=[f'€{val:,.0f}' for val in costs],
        textposition='outside'
    ))
    
    # Profit line
    fig.add_trace(go.Scatter(
        name='Profit',
        x=years,
        y=profits,
        mode='lines+markers',
        line=dict(color='#3498db', width=3),
        marker=dict(size=10, symbol='diamond'),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title=f"{model_type} - Income vs Costs Analysis",
        xaxis_title="Year",
        yaxis_title="Amount (€)",
        yaxis2=dict(
            title="Profit (€)",
            overlaying='y',
            side='right'
        ),
        height=500,
        barmode='group',
        hovermode='x unified',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig


def create_cumulative_profit_chart(yearly_projections: list, cost_breakdown: dict) -> go.Figure:
    """
    Create a chart showing cumulative profit over time.
    
    Args:
        yearly_projections: List of yearly income projection dictionaries
        cost_breakdown: Dictionary of yearly cost breakdown
        
    Returns:
        Plotly figure object
    """
    years = [str(proj.get('year', '')) for proj in yearly_projections]
    incomes = [proj.get('yearly_income', 0) for proj in yearly_projections]
    costs = [cost_breakdown.get(year, {}).get('total_cost', 0) for year in years]
    
    # Calculate cumulative profit
    cumulative_profit = []
    running_total = 0
    for inc, cost in zip(incomes, costs):
        running_total += (inc - cost)
        cumulative_profit.append(running_total)
    
    fig = go.Figure()
    
    # Cumulative profit area
    fig.add_trace(go.Scatter(
        x=years,
        y=cumulative_profit,
        mode='lines+markers',
        name='Cumulative Profit',
        line=dict(color='#9b59b6', width=3),
        marker=dict(size=12),
        fill='tozeroy',
        fillcolor='rgba(155, 89, 182, 0.3)'
    ))
    
    # Add break-even line
    fig.add_hline(y=0, line_dash="dash", line_color="red", 
                  annotation_text="Break-even Point", annotation_position="right")
    
    fig.update_layout(
        title="Cumulative Profit Over Time",
        xaxis_title="Year",
        yaxis_title="Cumulative Profit (€)",
        height=450,
        hovermode='x unified',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(tickformat=',.0f', tickprefix='€')
    )
    
    return fig
