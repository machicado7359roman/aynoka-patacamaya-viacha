"""Paleta compartida de las cuatro estaciones."""
import streamlit as st

def aplicar_estilo():
    st.html("""<style>
    :is(.st-key-laboratorio,.st-key-ficha) {background:#f7f1e4!important;color:#193e34!important;color-scheme:light}
    :is(.st-key-laboratorio,.st-key-ficha) h1,:is(.st-key-laboratorio,.st-key-ficha) h2,:is(.st-key-laboratorio,.st-key-ficha) h3,
    :is(.st-key-laboratorio,.st-key-ficha) p,:is(.st-key-laboratorio,.st-key-ficha) label,
    :is(.st-key-laboratorio,.st-key-ficha) [data-testid="stMetricValue"],
    :is(.st-key-laboratorio,.st-key-ficha) [data-testid="stMetricLabel"],
    :is(.st-key-laboratorio,.st-key-ficha) [data-testid="stText"],
    :is(.st-key-laboratorio,.st-key-ficha) [data-testid="stMarkdownContainer"] {color:#193e34!important}
    :is(.st-key-laboratorio,.st-key-ficha) [data-testid="stCaptionContainer"] p {color:#52695d!important}
    :is(.st-key-laboratorio,.st-key-ficha) [data-testid="stVerticalBlockBorderWrapper"],
    :is(.st-key-laboratorio,.st-key-ficha) [data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"]:is([style*="border"]),
    :is(.st-key-laboratorio,.st-key-ficha) [data-testid="stExpander"] details {background:#fffcf4!important;border-color:#d8c9ad!important;border-radius:14px}
    :is(.st-key-laboratorio,.st-key-ficha) [data-testid="stExpander"] summary {color:#193e34!important;background:#fffcf4!important}
    :is(.st-key-laboratorio,.st-key-ficha) [data-baseweb="select"] > div,
    :is(.st-key-laboratorio,.st-key-ficha) [data-testid="stFileUploaderDropzone"],
    :is(.st-key-laboratorio,.st-key-ficha) input {background:#fffcf4!important;color:#193e34!important;border-color:#cabb9e!important}
    :is(.st-key-laboratorio,.st-key-ficha) [data-baseweb="select"] span {color:#193e34!important}
    :is(.st-key-laboratorio,.st-key-ficha) button {background:#254c3c!important;border-color:#254c3c!important;color:#fffdf5!important}
    :is(.st-key-laboratorio,.st-key-ficha) button p {color:#fffdf5!important}
    :is(.st-key-laboratorio,.st-key-ficha) [data-testid="stAlert"] {background:#e8eedf!important;color:#193e34!important;border:1px solid #c4d2b9}
    :is(.st-key-laboratorio,.st-key-ficha) a {color:#246c55!important}
    :is(.st-key-laboratorio,.st-key-ficha) h1,:is(.st-key-laboratorio,.st-key-ficha) h2,:is(.st-key-laboratorio,.st-key-ficha) h3 {font-family:Georgia,serif;letter-spacing:-.02em}
    :is(.st-key-laboratorio,.st-key-ficha) [data-baseweb="select"] svg {fill:#193e34!important}
    [data-baseweb="popover"] [role="listbox"], [data-baseweb="popover"] [role="option"] {background:#fffcf4!important;color:#193e34!important}
    :is(.st-key-laboratorio,.st-key-ficha) [data-testid="stMetric"] {background:#fffcf4;border:1px solid #d8c9ad;border-radius:12px;padding:14px;margin-bottom:8px}
    :is(.st-key-laboratorio,.st-key-ficha) [data-testid="stLinkButton"] a {background:#254c3c!important;color:#fffdf5!important;border-color:#254c3c!important}
    :is(.st-key-laboratorio,.st-key-ficha) [data-testid="stLinkButton"] a p {color:#fffdf5!important}
    </style>""")

def linea(datos, y_label=None, color="#32755a", **kwargs):
    import plotly.graph_objects as go
    fig=go.Figure(go.Scatter(x=datos.index,y=datos.values,mode="lines",line=dict(color=color)))
    fig.update_layout(template="plotly_white",paper_bgcolor="#f7f1e4",plot_bgcolor="#fffcf4",font=dict(color="#193e34"),height=260,margin=dict(l=15,r=15,t=15,b=25),yaxis_title=y_label or datos.name)
    st.plotly_chart(fig,theme=None,use_container_width=True)
