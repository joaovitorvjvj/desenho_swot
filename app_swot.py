from __future__ import annotations

import hashlib
import io
import json
from io import BytesIO
from pathlib import Path

import nltk
import pandas as pd
import plotly.express as px
import streamlit as st
from groq import Groq
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
from sentence_transformers import SentenceTransformer

from swot_analysis import (
    AnalysisConfig,
    SWOT_DIMENSIONS,
    SWOT_PLURAL,
    analyze_swot_dataframe,
    apply_edited_labels,
    build_excel_bytes,
    infer_column_mapping,
)

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
GROQ_MODEL = "llama-3.3-70b-versatile"
APP_DIR = Path(__file__).resolve().parent

# ══════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO DE QUADRANTES E CORES (DASHBOARD, TOWS & PDF)
# ══════════════════════════════════════════════════════════════════
QUADRANTES = {
    "Força": {
        "label": "💪 Forças",
        "cor": "#2E8B3A",
        "cor_plotly": "Greens_r",
    },
    "Fraqueza": {
        "label": "⚠️ Fraquezas",
        "cor": "#E67E22",
        "cor_plotly": "Oranges_r",
    },
    "Oportunidade": {
        "label": "🚀 Oportunidades",
        "cor": "#2980B9",
        "cor_plotly": "Blues_r",
    },
    "Ameaça": {
        "label": "🔴 Ameaças",
        "cor": "#C0392B",
        "cor_plotly": "Reds_r",
    },
}

TOWS_TIPOS = [
    "SO — Ofensiva (Alavancagem)",
    "WO — Reforço (Virada)",
    "ST — Proteção (Confronto)",
    "WT — Defensiva (Sobrevivência)",
]

st.set_page_config(
    page_title="Análise SWOT & Objetivos Estratégicos",
    page_icon="🎯",
    layout="wide",
)


# ══════════════════════════════════════════════════════════════════
# INICIALIZAÇÃO DE RECURSOS E MODELOS
# ══════════════════════════════════════════════════════════════════
@st.cache_resource(show_spinner=False)
def load_model(model_name: str) -> SentenceTransformer:
    return SentenceTransformer(model_name)


@st.cache_resource(show_spinner=False)
def prepare_nltk() -> bool:
    try:
        nltk.data.find("corpora/stopwords")
    except LookupError:
        try:
            nltk.download("stopwords", quiet=True)
        except Exception:
            return False
    return True


@st.cache_data(show_spinner=False)
def read_excel_file(file_bytes: bytes, filename: str) -> pd.DataFrame:
    suffix = Path(filename).suffix.casefold()
    engine = "xlrd" if suffix == ".xls" else "openpyxl"
    return pd.read_excel(io.BytesIO(file_bytes), engine=engine)


def safe_default_index(options: list, value) -> int:
    try:
        return options.index(value)
    except ValueError:
        return 0


# ══════════════════════════════════════════════════════════════════
# CAMADA DE IA (GROQ API) & FALLBACK TEMPLATE
# ══════════════════════════════════════════════════════════════════
def generate_tows_with_groq(summary_df: pd.DataFrame, api_key: str) -> pd.DataFrame:
    """Gera Objetivos Estratégicos e KPIs fluidos usando a API da Groq."""
    forcas = summary_df[summary_df["Dimensão"] == "Força"].nlargest(3, "Quantidade")["Conceito agrupado"].tolist()
    fraquezas = summary_df[summary_df["Dimensão"] == "Fraqueza"].nlargest(3, "Quantidade")["Conceito agrupado"].tolist()
    oportunidades = summary_df[summary_df["Dimensão"] == "Oportunidade"].nlargest(3, "Quantidade")["Conceito agrupado"].tolist()
    ameacas = summary_df[summary_df["Dimensão"] == "Ameaça"].nlargest(3, "Quantidade")["Conceito agrupado"].tolist()

    prompt = f"""
    Você é um consultor sênior em Planejamento Estratégico.
    Analise os seguintes conceitos consolidados de uma Matriz SWOT:

    - FORÇAS: {', '.join(forcas) if forcas else 'Nenhum'}
    - FRAQUEZAS: {', '.join(fraquezas) if fraquezas else 'Nenhum'}
    - OPORTUNIDADES: {', '.join(oportunidades) if oportunidades else 'Nenhum'}
    - AMEAÇAS: {', '.join(ameacas) if ameacas else 'Nenhum'}

    Sua tarefa é cruzar esses fatores (Matriz TOWS) e formular 4 Objetivos Estratégicos práticos e com excelente redação corporativa no formato JSON.

    Gere exatamente 4 itens na lista 'estrategias', correspondendo aos tipos:
    1. "SO — Ofensiva (Alavancagem)" (Força + Oportunidade)
    2. "WO — Reforço (Virada)" (Fraqueza + Oportunidade)
    3. "ST — Proteção (Confronto)" (Força + Ameaça)
    4. "WT — Defensiva (Sobrevivência)" (Fraqueza + Ameaça)

    Responda EXCLUSIVAMENTE um objeto JSON válido no seguinte formato:
    {{
      "estrategias": [
        {{
          "Tipo": "SO — Ofensiva (Alavancagem)",
          "Cruzamento Semântico": "Força: '...' + Oportunidade: '...'",
          "Objetivo Estratégico": "Frase de ação clara, fluida, iniciada por verbo no infinitivo.",
          "Métrica / KPi Recomendado": "KPI mensurável e alinhado ao objetivo."
        }},
        ...
      ]
    }}
    """

    try:
        client = Groq(api_key=api_key)
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é um assistente especialista em matriz SWOT/TOWS que responde estritamente em JSON."},
                {"role": "user", "content": prompt}
            ],
            model=GROQ_MODEL,
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        response_text = chat_completion.choices[0].message.content
        data = json.loads(response_text)
        return pd.DataFrame(data.get("estrategias", []))

    except Exception as e:
        st.error(f"Erro ao consultar a API da Groq: {e}. Usando gerador estático de segurança.")
        return generate_default_tows(summary_df)


def generate_default_tows(summary_df: pd.DataFrame) -> pd.DataFrame:
    """Gerador estático baseado em templates simples (Fallback sem IA)."""
    forcas = summary_df[summary_df["Dimensão"] == "Força"].nlargest(1, "Quantidade")["Conceito agrupado"].tolist()
    fraquezas = summary_df[summary_df["Dimensão"] == "Fraqueza"].nlargest(1, "Quantidade")["Conceito agrupado"].tolist()
    oportunidades = summary_df[summary_df["Dimensão"] == "Oportunidade"].nlargest(1, "Quantidade")["Conceito agrupado"].tolist()
    ameacas = summary_df[summary_df["Dimensão"] == "Ameaça"].nlargest(1, "Quantidade")["Conceito agrupado"].tolist()

    rows = []
    if forcas and oportunidades:
        rows.append({
            "Tipo": "SO — Ofensiva (Alavancagem)",
            "Cruzamento Semântico": f"Força: '{forcas[0]}' + Oportunidade: '{oportunidades[0]}'",
            "Objetivo Estratégico": f"Aproveitar a oportunidade de {oportunidades[0].lower()} através da força em {forcas[0].lower()}.",
            "Métrica / KPi Recomendado": "Taxa de crescimento do projeto",
        })
    if fraquezas and oportunidades:
        rows.append({
            "Tipo": "WO — Reforço (Virada)",
            "Cruzamento Semântico": f"Fraqueza: '{fraquezas[0]}' + Oportunidade: '{oportunidades[0]}'",
            "Objetivo Estratégico": f"Mitigar a fraqueza em {fraquezas[0].lower()} para capturar a oportunidade de {oportunidades[0].lower()}.",
            "Métrica / KPi Recomendado": "Índice de eficiência operacional",
        })
    if forcas and ameacas:
        rows.append({
            "Tipo": "ST — Proteção (Confronto)",
            "Cruzamento Semântico": f"Força: '{forcas[0]}' + Ameaça: '{ameacas[0]}'",
            "Objetivo Estratégico": f"Utilizar a força em {forcas[0].lower()} para neutralizar os impactos de {ameacas[0].lower()}.",
            "Métrica / KPi Recomendado": "Índice de mitigação de riscos",
        })
    if fraquezas and ameacas:
        rows.append({
            "Tipo": "WT — Defensiva (Sobrevivência)",
            "Cruzamento Semântico": f"Fraqueza: '{fraquezas[0]}' + Ameaça: '{ameacas[0]}'",
            "Objetivo Estratégico": f"Reduzir vulnerabilidades internas associadas a {fraquezas[0].lower()} e evitar riscos de {ameacas[0].lower()}.",
            "Métrica / KPi Recomendado": "Redução de passivos / falhas",
        })

    return pd.DataFrame(rows if rows else [{
        "Tipo": "SO — Ofensiva (Alavancagem)",
        "Cruzamento Semântico": "Insuficiente",
        "Objetivo Estratégico": "Insira os dados da SWOT para gerar objetivos",
        "Métrica / KPi Recomendado": "KPI Principal"
    }])


# ══════════════════════════════════════════════════════════════════
# GERADOR DE PDF (REPORTLAB INTEGRADO COM TOWS)
# ══════════════════════════════════════════════════════════════════
def gerar_pdf_swot(summary_df: pd.DataFrame, mapping_df: pd.DataFrame, tows_df: pd.DataFrame) -> BytesIO:
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
    section_style = ParagraphStyle(
        "SectionStyle",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=14,
        spaceAfter=6,
    )
    quadrante_style = ParagraphStyle(
        "QuadranteStyle",
        parent=styles["Heading3"],
        fontSize=11,
        leading=14,
        spaceBefore=10,
        spaceAfter=4,
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

    elements.append(Paragraph("Relatório Estratégico Consolidado — Matriz SWOT & TOWS", title_style))
    elements.append(
        Paragraph("Análise Semântica de Diagnósticos e Plano de Objetivos Estratégicos.", subtitle_style)
    )
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E1"), spaceAfter=10))

    if not tows_df.empty:
        elements.append(Paragraph("🎯 Objetivos Estratégicos (Matriz TOWS)", section_style))
        tows_data = [[
            Paragraph("Tipo de Estratégia", cell_header_style),
            Paragraph("Cruzamento SWOT", cell_header_style),
            Paragraph("Objetivo Estratégico", cell_header_style),
            Paragraph("KPI / Métrica", cell_header_style),
        ]]

        for _, row in tows_df.iterrows():
            tows_data.append([
                Paragraph(str(row.get("Tipo", "")), cell_body_style),
                Paragraph(str(row.get("Cruzamento Semântico", "")), cell_body_style),
                Paragraph(str(row.get("Objetivo Estratégico", "")), cell_body_style),
                Paragraph(str(row.get("Métrica / KPi Recomendado", "")), cell_body_style),
            ])

        t_tows = Table(tows_data, colWidths=[110, 140, 200, 100])
        t_tows.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F5F9")]),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
        ]))
        elements.append(t_tows)
        elements.append(Spacer(1, 15))

    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E2E8F0"), spaceAfter=10))
    elements.append(Paragraph("📋 Diagnóstico Detalhado dos Quadrantes", section_style))

    for dimension, info in QUADRANTES.items():
        df_summary_dim = summary_df[summary_df["Dimensão"] == dimension].sort_values(
            ["Quantidade", "Grupo ID"], ascending=[False, True]
        )

        if df_summary_dim.empty:
            continue

        total_respostas_dim = df_summary_dim["Quantidade"].sum()
        q_style = ParagraphStyle(
            f"Q_{dimension}",
            parent=quadrante_style,
            textColor=colors.HexColor(info["cor"]),
        )
        elements.append(Paragraph(info["label"], q_style))

        data = [[
            Paragraph("#", cell_header_style),
            Paragraph("Conceito Consolidado", cell_header_style),
            Paragraph("Freq.", cell_header_style),
            Paragraph("%", cell_header_style),
            Paragraph("Respostas Originais Agrupadas", cell_header_style),
        ]]

        for _, row in df_summary_dim.iterrows():
            grupo_id = row["Grupo ID"]
            conceito = row["Conceito agrupado"]
            qtd = row["Quantidade"]
            percentual = (qtd / total_respostas_dim * 100) if total_respostas_dim > 0 else 0.0

            respostas_originais = mapping_df[
                (mapping_df["Dimensão"] == dimension) & (mapping_df["Grupo ID"] == grupo_id)
            ]["Dado bruto"].tolist()

            originais_formatadas = "<br/>• ".join([str(r) for r in respostas_originais])

            data.append([
                Paragraph(str(grupo_id), cell_body_style),
                Paragraph(str(conceito), cell_body_style),
                Paragraph(str(qtd), cell_body_style),
                Paragraph(f"{percentual:.1f}%", cell_body_style),
                Paragraph(f"• {originais_formatadas}", cell_body_style),
            ])

        t = Table(data, colWidths=[20, 140, 35, 35, 320])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(info["cor"])),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 10))

    doc.build(elements)
    buffer.seek(0)
    return buffer


# ══════════════════════════════════════════════════════════════════
# INTERFACE DO USUÁRIO & RENDERIZAÇÃO
# ══════════════════════════════════════════════════════════════════
def show_intro() -> None:
    st.title("🎯 Análise Semântica SWOT & Objetivos Estratégicos")
    st.markdown(
        "Carregue sua Matriz SWOT para agrupar respostas semelhantes com inteligência semântica, "
        "visualizar gráficos dinâmicos e gerar **Objetivos Estratégicos com IA (Groq)**."
    )


def render_results() -> None:
    analysis = st.session_state.get("swot_analysis")
    if not analysis:
        return

    original_mapping = analysis["mapping"]
    original_summary = analysis["summary"]
    configs = analysis["configs"]
    filename = analysis["filename"]

    st.divider()

    # 1. Editor de Conceitos Agrupados
    with st.expander("✏️ **Revisar e Editar Conceitos Agrupados**", expanded=False):
        st.info("Altere o nome dos conceitos consolidados. As alterações sincronizam todo o dashboard.")
        edited_summary = st.data_editor(
            original_summary,
            key="concept_editor",
            hide_index=True,
            use_container_width=True,
            disabled=["Dimensão", "Grupo ID", "Quantidade", "Exemplos"],
            column_config={
                "Dimensão": st.column_config.TextColumn(width="small"),
                "Grupo ID": st.column_config.NumberColumn(format="%d", width="small"),
                "Conceito agrupado": st.column_config.TextColumn(required=True, width="medium"),
                "Quantidade": st.column_config.NumberColumn(format="%d", width="small"),
                "Exemplos": st.column_config.TextColumn(width="large"),
            },
        )

    edited_mapping = apply_edited_labels(original_mapping, edited_summary)

    # Obter chave Groq da sessão ou secret
    groq_api_key = st.session_state.get("groq_api_key", "")

    # Inicializa TOWS se não existir no estado
    if "tows_df" not in st.session_state:
        if groq_api_key:
            st.session_state["tows_df"] = generate_tows_with_groq(edited_summary, groq_api_key)
        else:
            st.session_state["tows_df"] = generate_default_tows(edited_summary)

    # 2. Métricas
    total_records = len(edited_mapping)
    total_concepts = len(edited_summary)
    metric_columns = st.columns(6)
    metric_columns[0].metric("Registros analisados", total_records)
    metric_columns[1].metric("Conceitos totais", total_concepts)
    for index, dimension in enumerate(SWOT_DIMENSIONS, start=2):
        metric_columns[index].metric(
            SWOT_PLURAL[dimension],
            int((edited_summary["Dimensão"] == dimension).sum()),
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. Abas Principais
    tab_tows, tab_dash, tab_matriz, tab_raw = st.tabs(
        [
            "🎯 Objetivos Estratégicos (Matriz TOWS)",
            "📊 Dashboard & Gráficos",
            "📋 Matriz Detalhada",
            "🔍 Dado Bruto Mapeado",
        ]
    )

    # ABA 1: OBJETIVOS ESTRATÉGICOS
    with tab_tows:
        st.subheader("🎯 Matriz de Objetivos Estratégicos (TOWS)")
        st.markdown(
            "Configure as ações estratégicas geradas pelo cruzamento dos fatores da Matriz SWOT."
        )

        btn_col1, btn_col2 = st.columns([1, 3])
        with btn_col1:
            if st.button("🤖 Recriar Objetivos com IA (Groq)", type="secondary", use_container_width=True):
                if groq_api_key:
                    with st.spinner("Gerando redação corporativa e KPIs via Groq..."):
                        st.session_state["tows_df"] = generate_tows_with_groq(edited_summary, groq_api_key)
                        st.rerun()
                else:
                    st.warning("Insira sua chave de API da Groq na barra lateral para usar a IA.")

        edited_tows = st.data_editor(
            st.session_state["tows_df"],
            key="tows_editor",
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Tipo": st.column_config.SelectboxColumn("Tipo de Estratégia", options=TOWS_TIPOS, required=True, width="medium"),
                "Cruzamento Semântico": st.column_config.TextColumn("Cruzamento de Fatores SWOT", width="large"),
                "Objetivo Estratégico": st.column_config.TextColumn("Objetivo Estratégico", width="large", required=True),
                "Métrica / KPi Recomendado": st.column_config.TextColumn("KPI / Métrica", width="medium"),
            },
        )
        st.session_state["tows_df"] = edited_tows

    # ABA 2: DASHBOARD & GRÁFICOS
    with tab_dash:
        g_col1, g_col2 = st.columns(2)
        cols_graficos = [g_col1, g_col2, g_col1, g_col2]

        for idx, (dimension, info) in enumerate(QUADRANTES.items()):
            df_dim = edited_summary[edited_summary["Dimensão"] == dimension].copy()

            with cols_graficos[idx]:
                st.subheader(info["label"])
                if df_dim.empty:
                    st.info("Nenhum dado encontrado para esta dimensão.")
                else:
                    fig = px.bar(
                        df_dim.sort_values("Quantidade", ascending=True),
                        x="Quantidade",
                        y="Conceito agrupado",
                        orientation="h",
                        text="Quantidade",
                        labels={
                            "Quantidade": "Frequência",
                            "Conceito agrupado": "Conceito",
                        },
                        color="Quantidade",
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

    # ABA 3: MATRIZ DETALHADA
    with tab_matriz:
        m_col1, m_col2 = st.columns(2)
        cols_tabelas = [m_col1, m_col2, m_col1, m_col2]

        for i, (dimension, info) in enumerate(QUADRANTES.items()):
            df_dim = edited_summary[edited_summary["Dimensão"] == dimension].copy()

            with cols_tabelas[i]:
                st.markdown(
                    f"<h3 style='color:{info['cor']}'>{info['label']}</h3>",
                    unsafe_allow_html=True,
                )

                if df_dim.empty:
                    st.write("Sem registros.")
                else:
                    total_dim = df_dim["Quantidade"].sum()
                    df_dim["Percentual"] = (df_dim["Quantidade"] / total_dim * 100) if total_dim > 0 else 0

                    st.dataframe(
                        df_dim[["Grupo ID", "Conceito agrupado", "Quantidade", "Percentual", "Exemplos"]],
                        column_config={
                            "Grupo ID": st.column_config.NumberColumn("#", format="%d", width="small"),
                            "Conceito agrupado": st.column_config.TextColumn("Conceito", width="medium"),
                            "Quantidade": st.column_config.NumberColumn("Freq.", format="%d", width="small"),
                            "Percentual": st.column_config.NumberColumn("%", format="%.1f%%", width="small"),
                            "Exemplos": st.column_config.TextColumn("Exemplos de Respostas", width="large"),
                        },
                        use_container_width=True,
                        hide_index=True,
                    )
                st.divider()

    # ABA 4: DADO BRUTO MAPEADO
    with tab_raw:
        st.markdown("#### Mapeamento Completo de Respostas Brutas")
        st.dataframe(
            edited_mapping[["Dimensão", "Linha original", "Dado bruto", "Grupo ID", "Conceito agrupado"]],
            column_config={
                "Linha original": st.column_config.NumberColumn("Linha Excel", format="%d"),
            },
            hide_index=True,
            use_container_width=True,
        )

    # 4. Downloads na Barra Lateral
    with st.sidebar:
        st.divider()
        st.header("📄 Exportar Resultados")

        excel_bytes = build_excel_bytes(
            edited_mapping,
            edited_summary,
            config_by_dimension=configs,
            source_filename=filename,
        )
        st.download_button(
            "📊 Baixar Excel Completo",
            data=excel_bytes,
            file_name=f"Analise_SWOT_{filename}",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True,
        )

        pdf_bytes = gerar_pdf_swot(edited_summary, edited_mapping, edited_tows)
        st.download_button(
            label="📥 Baixar PDF com Objetivos Estratégicos",
            data=pdf_bytes,
            file_name="Relatorio_Estrategico_SWOT_TOWS.pdf",
            mime="application/pdf",
            use_container_width=True,
        )


# ══════════════════════════════════════════════════════════════════
# EXECUÇÃO DA APLICAÇÃO
# ══════════════════════════════════════════════════════════════════
show_intro()
prepare_nltk()

# Sidebar: Configuração da IA Groq
st.sidebar.header("🤖 Configuração da IA Groq")
groq_input_key = st.sidebar.text_input(
    "Groq API Key",
    type="password",
    value=st.session_state.get("groq_api_key", ""),
    help="Cole aqui sua API Key gratuita da Groq (gsk_...)",
)
if groq_input_key:
    st.session_state["groq_api_key"] = groq_input_key

uploaded_file = st.file_uploader(
    "Envie o arquivo Excel da Matriz SWOT",
    type=["xlsx", "xls"],
    accept_multiple_files=False,
)

if uploaded_file is not None:
    uploaded_bytes = uploaded_file.getvalue()
    file_signature = hashlib.sha256(uploaded_bytes).hexdigest()
    previous_analysis = st.session_state.get("swot_analysis")

    if previous_analysis and previous_analysis.get("file_signature") != file_signature:
        st.session_state.pop("swot_analysis", None)
        st.session_state.pop("concept_editor", None)
        st.session_state.pop("tows_df", None)

    try:
        dataframe = read_excel_file(uploaded_bytes, uploaded_file.name)
    except Exception as error:
        st.error(f"Não foi possível ler o arquivo: {error}")
        st.stop()

    if dataframe.empty:
        st.error("O arquivo não contém dados.")
        st.stop()

    st.success(f"Arquivo carregado com sucesso: {uploaded_file.name}")
    with st.expander("🔍 Prévia das primeiras 20 linhas"):
        st.dataframe(dataframe.head(20), hide_index=True, use_container_width=True)

    inferred_mapping = infer_column_mapping(dataframe.columns)
    available_columns = ["Não selecionar"] + list(dataframe.columns)

    st.sidebar.header("⚙️ Configurações Semânticas")
    similarity_threshold = st.sidebar.slider(
        "Limiar de similaridade",
        min_value=0.50,
        max_value=0.90,
        value=0.72,
        step=0.01,
    )

    st.sidebar.markdown("##### Máximo de conceitos por dimensão")
    max_concepts = {
        dimension: st.sidebar.number_input(
            SWOT_PLURAL[dimension],
            min_value=1,
            max_value=15,
            value=15,
            step=1,
            key=f"max_{dimension}",
        )
        for dimension in SWOT_DIMENSIONS
    }

    st.markdown("#### Associação das Colunas")
    mapping_columns = st.columns(4)
    selected_mapping = {}
    for container, dimension in zip(mapping_columns, SWOT_DIMENSIONS):
        inferred = inferred_mapping.get(dimension)
        default_value = inferred if inferred in dataframe.columns else "Não selecionar"
        with container:
            selected = st.selectbox(
                SWOT_PLURAL[dimension],
                options=available_columns,
                index=safe_default_index(available_columns, default_value),
                key=f"column_{dimension}_{uploaded_file.name}",
            )
            selected_mapping[dimension] = None if selected == "Não selecionar" else selected

    selected_columns = [column for column in selected_mapping.values() if column is not None]
    duplicate_columns = len(selected_columns) != len(set(selected_columns))
    missing_dimensions = [dimension for dimension, column in selected_mapping.items() if column is None]

    if duplicate_columns:
        st.error("Cada dimensão SWOT deve usar uma coluna diferente.")
    if missing_dimensions:
        st.warning(
            "Selecione as quatro colunas antes de iniciar: "
            + ", ".join(SWOT_PLURAL[dimension] for dimension in missing_dimensions)
            + "."
        )

    analyze_button = st.button(
        "🚀 Processar e Gerar Objetivos Estratégicos",
        type="primary",
        disabled=duplicate_columns or bool(missing_dimensions),
        use_container_width=True,
    )

    if analyze_button:
        configs = {
            dimension: AnalysisConfig(
                similarity_threshold=similarity_threshold,
                max_concepts=int(max_concepts[dimension]),
                model_name=MODEL_NAME,
            )
            for dimension in SWOT_DIMENSIONS
        }

        try:
            with st.spinner("Agrupando conceitos e formulando matriz de objetivos estratégicos..."):
                model = load_model(MODEL_NAME)
                mapping_df, summary_df = analyze_swot_dataframe(
                    dataframe,
                    selected_mapping,
                    model,
                    configs,
                )
        except Exception as error:
            st.exception(error)
            st.stop()

        if mapping_df.empty:
            st.error("Não foram encontrados textos válidos nas colunas selecionadas.")
        else:
            st.session_state["swot_analysis"] = {
                "mapping": mapping_df,
                "summary": summary_df,
                "configs": configs,
                "filename": uploaded_file.name,
                "file_signature": file_signature,
            }
            st.session_state.pop("concept_editor", None)
            st.session_state.pop("tows_df", None)
            st.rerun()

render_results()
