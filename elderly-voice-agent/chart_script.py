
import plotly.graph_objects as go

# Create figure
fig = go.Figure()

# Define positions for nodes
# User nodes
user_speak_pos = (0.5, 10)
user_hear_pos = (0.5, 0)

# Frontend nodes (column 1)
daily_pos = (0.5, 8.5)
stt_pos = (0.5, 7.5)
llm_pos = (0.5, 6.5)
tts_pos = (0.5, 1.5)

# Backend nodes (column 2)
api_pos = (5, 6.5)
ws_pos = (5, 5)
msg_pos = (4, 3.5)
call_pos = (5, 3.5)
notif_pos = (6, 3.5)

# Add Frontend group box
fig.add_shape(
    type="rect",
    x0=-0.5, y0=1, x1=1.5, y1=9,
    line=dict(color="#21808d", width=2),
    fillcolor="#e8f4f5",
    opacity=0.3
)

# Add Backend group box
fig.add_shape(
    type="rect",
    x0=3.5, y0=3, x1=6.5, y1=7,
    line=dict(color="#21808d", width=2),
    fillcolor="#f3f3ee",
    opacity=0.3
)

# Function to add a node box
def add_node(fig, pos, text, color="#1FB8CD"):
    x, y = pos
    fig.add_shape(
        type="rect",
        x0=x-0.4, y0=y-0.3, x1=x+0.4, y1=y+0.3,
        line=dict(color="#13343b", width=2),
        fillcolor=color
    )
    fig.add_trace(go.Scatter(
        x=[x], y=[y],
        mode='text',
        text=[text],
        textfont=dict(size=9, color="#13343b"),
        showlegend=False,
        hoverinfo='skip'
    ))

# Function to add arrow
def add_arrow(fig, start, end, label=""):
    x0, y0 = start
    x1, y1 = end
    fig.add_annotation(
        x=x1, y=y1,
        ax=x0, ay=y0,
        xref="x", yref="y",
        axref="x", ayref="y",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor="#333333"
    )

# Add all nodes
add_node(fig, user_speak_pos, "User<br>Speaking", "#B3E5EC")
add_node(fig, daily_pos, "Daily.co<br>Transport", "#1FB8CD")
add_node(fig, stt_pos, "Deepgram<br>STT", "#1FB8CD")
add_node(fig, llm_pos, "OpenAI<br>LLM", "#1FB8CD")
add_node(fig, tts_pos, "Cartesia<br>TTS", "#1FB8CD")
add_node(fig, api_pos, "Flask REST<br>API", "#DB4545")
add_node(fig, ws_pos, "WebSocket", "#DB4545")
add_node(fig, msg_pos, "Messaging", "#2E8B57")
add_node(fig, call_pos, "Call Svc", "#2E8B57")
add_node(fig, notif_pos, "Notification", "#2E8B57")
add_node(fig, user_hear_pos, "User Hears<br>Response", "#B3E5EC")

# Add arrows for flow
add_arrow(fig, user_speak_pos, daily_pos)
add_arrow(fig, daily_pos, stt_pos)
add_arrow(fig, stt_pos, llm_pos)
add_arrow(fig, llm_pos, api_pos)
add_arrow(fig, api_pos, ws_pos)
add_arrow(fig, ws_pos, msg_pos)
add_arrow(fig, ws_pos, call_pos)
add_arrow(fig, ws_pos, notif_pos)
add_arrow(fig, msg_pos, ws_pos)
add_arrow(fig, call_pos, ws_pos)
add_arrow(fig, notif_pos, ws_pos)
add_arrow(fig, ws_pos, api_pos)
add_arrow(fig, api_pos, llm_pos)
add_arrow(fig, llm_pos, tts_pos)
add_arrow(fig, tts_pos, daily_pos)
add_arrow(fig, daily_pos, user_hear_pos)

# Add group labels
fig.add_trace(go.Scatter(
    x=[0.5], y=[9.3],
    mode='text',
    text=["Frontend"],
    textfont=dict(size=11, color="#13343b"),
    showlegend=False,
    hoverinfo='skip'
))

fig.add_trace(go.Scatter(
    x=[5], y=[7.3],
    mode='text',
    text=["Backend"],
    textfont=dict(size=11, color="#13343b"),
    showlegend=False,
    hoverinfo='skip'
))

# Update layout
fig.update_layout(
    title="Elderly Voice Agent Architecture",
    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1, 7]),
    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.5, 10.5]),
    plot_bgcolor='white',
    showlegend=False
)

# Save the figure
fig.write_image("elderly_voice_agent_architecture.png")
fig.write_image("elderly_voice_agent_architecture.svg", format="svg")

print("Chart saved successfully!")
