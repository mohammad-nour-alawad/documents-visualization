# visualization.py

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def interactive_timeline(dates_df):
    """
    Create an interactive timeline using Plotly.
    """
    if dates_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No Data Available", x=0.5, y=0.5, showarrow=False)
        return fig

    # Convert 'year' to datetime
    dates_df['year_dt'] = pd.to_datetime(dates_df['year'], format='%Y', errors='coerce')
    dates_df = dates_df.dropna(subset=['year_dt'])

    dates_df = dates_df.sort_values('year_dt')
    fig = px.scatter(dates_df, x='year_dt', y=[1]*len(dates_df),
                     text='event', title='Interactive Events Timeline',
                     labels={'x': 'Year', 'y': ''})
    fig.update_traces(textposition='top center')
    fig.update_yaxes(showticklabels=False)
    fig.update_layout(showlegend=False, height=400)
    return fig


def interactive_relationships(persons_df, relationships_df):
    """
    Create an interactive network graph using Plotly.
    """
    G = nx.Graph()

    # Add nodes
    for _, row in persons_df.iterrows():
        G.add_node(row['name'], role=row['role'])

    # Add edges
    for _, row in relationships_df.iterrows():
        G.add_edge(row['person'], row['other_person'], relationship=row['relationship'])

    if G.number_of_nodes() == 0:
        fig = go.Figure()
        fig.add_annotation(text="No Data Available", x=0.5, y=0.5, showarrow=False)
        return fig

    pos = nx.spring_layout(G, k=0.5, seed=42)

    edge_x = []
    edge_y = []
    edge_text = []
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_text.append(edge[2]['relationship'])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#888'),
        hoverinfo='text',
        text=edge_text,
        mode='lines')

    node_x = []
    node_y = []
    node_text = []
    for node in G.nodes(data=True):
        x, y = pos[node[0]]
        node_x.append(x)
        node_y.append(y)
        node_text.append(f"{node[0]} ({node[1]['role']})")

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="top center",
        hoverinfo='text',
        marker=dict(
            showscale=False,
            color='lightblue',
            size=20,
            line_width=2))

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title='Interactive Persons Relationships',
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    return fig
