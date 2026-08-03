from io import BytesIO
import pandas as pd
import plotly.express as px
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
import streamlit as st

ARQUIVO = "SWOT_Higienizado.xlsx"

st.set_page_config(
    page_title="Dashboard Matriz SWOT — EPROC/SEPLAN",
    page_icon="🎯",
    layout="wide",
)

QUADRANTES = {
    "Forcas": {
        "label": "💪 Forças",
        "cor": "#2E8B3A",
        "cor_plotly": "Greens_r",
    },
    "Fraquezas": {
        "label": "⚠️ Fraquezas",
        "cor": "#E67E22",
        "cor_plotly": "Oranges_r",
    },
    "Oportunidades": {
        "label": "🚀 Oportunidades",
        "cor": "#2980B9",
        "cor_plotly": "Blues_r",
    },
    "Ameacas": {
        "label": "🔴 Ameaças",
        "cor": "#C0392B",
        "cor_plotly": "Reds_r",
    },
}

# ══════════════════════════════════════════════════════════════════
# FUNÇÃO PARA GERAR O PDF
# ══════════════════════════════════════════════════════════════════


def gerar_pdf_swot(caminho_excel):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20,
    )
    elements = []
    styles = getSampleStyleSheet()

    # Estilos customizados
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#1E3A8A"),
        alignment=1,
    )
    subtitle_style = ParagraphStyle(
        "SubTitleStyle",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#64748B"),
        alignment=1,
        spaceAfter=15,
    )
    quadrante_style = ParagraphStyle(
        "QuadranteStyle",
        parent=styles["Heading2"],
        fontSize=12,
        leading=15,
        spaceBefore=12,
        spaceAfter=6,
    )
    cell_header_style = ParagraphStyle(
        "CellHeader",
        parent=styles["Normal"],
        fontSize=8,
        fontName="Helvetica-Bold",
        textColor=colors.white,
        alignment=0,
    )
    cell_body_style = ParagraphStyle(
        "CellBody", parent=styles["Normal"], fontSize=7, leading=9
    )

    # Cabeçalho
    elements.append(
        Paragraph(
            "Relatório Consolidado da Matriz SWOT — EPROC/SEPLAN", title_style
        )
    )
    elements.append(
        Paragraph(
            "Resultado do processo de higienização e agrupamento semântico.",
            subtitle_style,
        )
    )
    elements.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor("#CBD5E1"),
            spaceAfter=10,
        )
    )

    # Construção de tabelas por quadrante
    for sheet, info in QUADRANTES.items():
        df = pd.read_excel(caminho_excel, sheet_name=sheet)

        q_style = ParagraphStyle(
            f"Q_{sheet}",
            parent=quadrante_style,
            textColor=colors.HexColor(info["cor"]),
        )
        elements.append(Paragraph(info["label"], q_style))

        # Cabeçalho da tabela
        data = [[
            Paragraph("#", cell_header_style),
            Paragraph("Conceito Consolidado", cell_header_style),
            Paragraph("Freq.", cell_header_style),
            Paragraph("%", cell_header_style),
            Paragraph("Respostas Originais Agrupadas", cell_header_style),
        ]]

        # Linhas da tabela
        for _, row in df.iterrows():
            originais_formatadas = str(row["Respostas_Originais"]).replace(
                " ||| ", "<br/>• "
            )
            data.append([
                Paragraph(str(row["Rank"]), cell_body_style),
                Paragraph(str(row["Conceito_Consolidado"]), cell_body_style),
                Paragraph(str(row["Frequencia"]), cell_body_style),
                Paragraph(f"{row['Percentual']}%", cell_body_style),
                Paragraph(f"• {originais_formatadas}", cell_body_style),
            ])

        # Largura das colunas (Total A4 ~550pt)
        t = Table(data, colWidths=[20, 140, 35, 35, 320])
        t.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(info["cor"])),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#E2E8F0"),
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#F8FAFC")],
                ),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        elements.append(t)
        elements.append(Spacer(1, 10))

    doc.build(elements)
    buffer.seek(0)
    return buffer


# ══════════════════════════════════════════════════════════════════
# STREAMLIT UI
# ══════════════════════════════════════════════════════════════════

st.title("🎯 Matriz SWOT — EPROC/SEPLAN")
st.markdown("Análise visual e relatório completo da matriz de diagnósticos.")

try:
    # Botão de exportação PDF na Barra Lateral
    with st.sidebar:
        st.header("📄 Exportar Dados")
        st.markdown(
            "Gere o relatório completo consolidado em PDF com todos os conceitos e respostas."
        )

        pdf_bytes = gerar_pdf_swot(ARQUIVO)
        st.download_button(
            label="📥 Baixar PDF Completo",
            data=pdf_bytes,
            file_name="Matriz_SWOT_EPROC_Consolidada.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
        st.divider()

    # Abas para separar Visão Geral (Gráficos) e Tabelas Detalhadas
    tab_dash, tab_matriz = st.tabs(
        ["📊 Dashboard & Gráficos", "📋 Matriz Detalhada (Tabelas)"]
    )

    with tab_dash:
        # Métricas do Resumo
        try:
            df_resumo = pd.read_excel(ARQUIVO, sheet_name="Resumo")
            cols_m = st.columns(len(df_resumo))
            for idx, row in df_resumo.iterrows():
                with cols_m[idx]:
                    st.metric(
                        label=row["Quadrante"],
                        value=f"{row['Conceitos_Consolidados']} conceitos",
                        delta=f"{row['Respostas_Brutas']} respostas",
                    )
        except Exception:
            pass

        st.divider()

        # Gráficos de Barras Horizontais (Top Conceitos por Quadrante)
        g_col1, g_col2 = st.columns(2)
        cols_graficos = [g_col1, g_col2, g_col1, g_col2]

        for idx, (sheet, info) in enumerate(QUADRANTES.items()):
            df = pd.read_excel(ARQUIVO, sheet_name=sheet)

            with cols_graficos[idx]:
                st.subheader(info["label"])
                fig = px.bar(
                    df.sort_values("Frequencia", ascending=True),
                    x="Frequencia",
                    y="Conceito_Consolidado",
                    orientation="h",
                    text="Frequencia",
                    labels={
                        "Frequencia": "Frequência",
                        "Conceito_Consolidado": "Conceito",
                    },
                    color="Frequencia",
                    color_continuous_scale=info["cor_plotly"],
                )
                fig.update_layout(
                    showlegend=False,
                    coloraxis_showscale=False,
                    height=380,
                    margin=dict(l=0, r=20, t=30, b=0),
                )
                fig.update_traces(textposition="outside")
                st.plotly_chart(fig, use_container_width=True)

    with tab_matriz:
        m_col1, m_col2 = st.columns(2)
        cols_tabelas = [m_col1, m_col2, m_col1, m_col2]

        for i, (sheet, info) in enumerate(QUADRANTES.items()):
            df = pd.read_excel(ARQUIVO, sheet_name=sheet)

            with cols_tabelas[i]:
                st.markdown(
                    f"<h3 style='color:{info['cor']}'>{info['label']}</h3>",
                    unsafe_allow_html=True,
                )

                st.dataframe(
                    df,
                    column_config={
                        "Rank": st.column_config.NumberColumn(
                            "#", format="%d", width="small"
                        ),
                        "Conceito_Consolidado": st.column_config.TextColumn(
                            "Conceito", width="medium"
                        ),
                        "Frequencia": st.column_config.NumberColumn(
                            "Freq.", format="%d", width="small"
                        ),
                        "Percentual": st.column_config.NumberColumn(
                            "%", format="%.1f%%", width="small"
                        ),
                        "Respostas_Originais": st.column_config.TextColumn(
                            "Respostas Originais", width="large"
                        ),
                    },
                    use_container_width=True,
                    hide_index=True,
                )
                st.divider()

except FileNotFoundError:
    st.error(
        f"Arquivo '{ARQUIVO}' não encontrado. Execute o `higieniza_swot.py` antes."
    )