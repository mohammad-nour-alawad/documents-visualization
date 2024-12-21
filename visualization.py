# visualization.py

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# def visualize_timeline(dates_df):
#     """
#     Visualize events on a timeline using matplotlib.
#     """
#     if dates_df.empty:
#         fig = plt.figure()
#         plt.text(0.5, 0.5, "No Data Available", ha='center', va='center')
#         return fig

#     # Convert 'year' to datetime
#     dates_df['year_dt'] = pd.to_datetime(dates_df['year'], format='%Y', errors='coerce')
#     dates_df = dates_df.dropna(subset=['year_dt'])

#     # Sort by year
#     dates_df = dates_df.sort_values('year_dt')

#     fig, ax = plt.subplots(figsize=(12, 2))
#     ax.hlines(1, dates_df['year_dt'].min(), dates_df['year_dt'].max(), colors='skyblue')
#     ax.eventplot(dates_df['year_dt'], lineoffsets=1, colors='red')

#     for _, row in dates_df.iterrows():
#         ax.text(row['year_dt'], 1.02, row['event'], rotation=45, ha='right', va='bottom', fontsize=8)

#     ax.set_yticks([])
#     ax.set_xlabel('Year')
#     ax.set_title('Events Timeline')
#     plt.tight_layout()
#     return fig


# def visualize_relationships(persons_df, relationships_df):
#     """
#     Visualize relationships using networkx and matplotlib.
#     """
#     fig = plt.figure(figsize=(14, 10))

#     if persons_df.empty or relationships_df.empty:
#         plt.text(0.5, 0.5, "No Relationship Data Available", ha='center', va='center', fontsize=14)
#         return fig

#     G = nx.Graph()

#     # Add nodes
#     for _, row in persons_df.iterrows():
#         G.add_node(row['name'], role=row['role'])

#     # Add edges with relationship type
#     for _, row in relationships_df.iterrows():
#         G.add_edge(row['person'], row['other_person'], relationship=row['relationship'])

#     pos = nx.kamada_kawai_layout(G)

#     # Calculate node sizes based on degree
#     degrees = dict(G.degree())
#     node_sizes = [300 + degrees[node]*100 for node in G.nodes()]

#     nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color='lightblue', alpha=0.9)
#     nx.draw_networkx_edges(G, pos, width=1.5, alpha=0.7)
#     nx.draw_networkx_labels(G, pos, font_size=10, font_family="sans-serif")

#     # Create edge labels
#     edge_labels = nx.get_edge_attributes(G, 'relationship')
#     for edge, label in edge_labels.items():
#         x0, y0 = pos[edge[0]]
#         x1, y1 = pos[edge[1]]
#         xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
#         plt.text(xm, ym, label, fontsize=9, color='black',
#                  horizontalalignment='center', verticalalignment='center',
#                  bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))

#     plt.title('Persons Relationships')
#     plt.axis('off')
#     plt.tight_layout()
#     return fig


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
