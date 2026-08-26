import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from streamlit_sortables import sort_items

# ReportLab imports para geração de PDF profissional
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.pdfgen import canvas

# ---------------------------------------------------------
# Configuração Global e Estilo da Página
# ---------------------------------------------------------
st.set_page_config(
    page_title="Planejamento Estratégico EPROC/SEPLAN",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS personalizada
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 0rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .card-swot-f { background-color: #D1FAE5; border-left: 5px solid #10B981; padding: 10px; border-radius: 4px; }
    .card-swot-fq { background-color: #FEE2E2; border-left: 5px solid #EF4444; padding: 10px; border-radius: 4px; }
    .card-swot-o { background-color: #DBEAFE; border-left: 5px solid #3B82F6; padding: 10px; border-radius: 4px; }
    .card-swot-a { background-color: #FEF3C7; border-left: 5px solid #F59E0B; padding: 10px; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Base de Dados Explicita: 40 Fatores SWOT discriminados
# ---------------------------------------------------------
@st.cache_data
def get_full_swot_data():
    data = [
        # 10 FORÇAS
        {"ID": "F01", "Categoria": "Força", "Tipo": "Interno", "Fator": "Equipe técnica com alta qualificação em gestão pública", "Impacto": "Alto", "Pontucao": 5},
        {"ID": "F02", "Categoria": "Força", "Tipo": "Interno", "Fator": "Alinhamento com as diretrizes governamentais vigentes", "Impacto": "Alto", "Pontucao": 5},
        {"ID": "F03", "Categoria": "Força", "Tipo": "Interno", "Fator": "Processos finalísticos digitais e padronizados no EPROC", "Impacto": "Alto", "Pontucao": 4},
        {"ID": "F04", "Categoria": "Força", "Tipo": "Interno", "Fator": "Capacidade de geração de relatórios gerenciais em tempo real", "Impacto": "Médio", "Pontucao": 4},
        {"ID": "F05", "Categoria": "Força", "Tipo": "Interno", "Fator": "Alto nível de engajamento dos gestores de setor", "Impacto": "Alto", "Pontucao": 5},
        {"ID": "F06", "Categoria": "Força", "Tipo": "Interno", "Fator": "Infraestrutura de dados centralizada e segura", "Impacto": "Alto", "Pontucao": 4},
        {"ID": "F07", "Categoria": "Força", "Tipo": "Interno", "Fator": "Transparência auditável nas rotinas operacionais", "Impacto": "Médio", "Pontucao": 4},
        {"ID": "F08", "Categoria": "Força", "Tipo": "Interno", "Fator": "Cultura organizacional orientada à melhoria contínua", "Impacto": "Médio", "Pontucao": 3},
        {"ID": "F09", "Categoria": "Força", "Tipo": "Interno", "Fator": "Rede corporativa estável e com redundância", "Impacto": "Médio", "Pontucao": 3},
        {"ID": "F10", "Categoria": "Força", "Tipo": "Interno", "Fator": "Boa articulação e comunicação interdepartamental", "Impacto": "Médio", "Pontucao": 4},

        # 10 FRAQUEZAS
        {"ID": "Fq01", "Categoria": "Fraqueza", "Tipo": "Interno", "Fator": "Sistemas legados dependentes de manutenção legada", "Impacto": "Alto", "Pontucao": 5},
        {"ID": "Fq02", "Categoria": "Fraqueza", "Tipo": "Interno", "Fator": "Limitação orçamentária para treinamento contínuo", "Impacto": "Alto", "Pontucao": 4},
        {"ID": "Fq03", "Categoria": "Fraqueza", "Tipo": "Interno", "Fator": "Gargalo no tempo médio de atendimento de chamados complexos", "Impacto": "Médio", "Pontucao": 4},
        {"ID": "Fq04", "Categoria": "Fraqueza", "Tipo": "Interno", "Fator": "Sobrecarga de trabalho em períodos de encerramento fiscal", "Impacto": "Alto", "Pontucao": 5},
        {"ID": "Fq05", "Categoria": "Fraqueza", "Tipo": "Interno", "Fator": "Documentação formal de processos internos incompleta", "Impacto": "Médio", "Pontucao": 3},
        {"ID": "Fq06", "Categoria": "Fraqueza", "Tipo": "Interno", "Fator": "Alta rotatividade na equipe de suporte terceirizado", "Impacto": "Médio", "Pontucao": 4},
        {"ID": "Fq07", "Categoria": "Fraqueza", "Tipo": "Interno", "Fator": "Dependência de fornecedores específicos para customização", "Impacto": "Alto", "Pontucao": 4},
        {"ID": "Fq08", "Categoria": "Fraqueza", "Tipo": "Interno", "Fator": "Baixa automação em tarefas administrativas repetitivas", "Impacto": "Médio", "Pontucao": 3},
        {"ID": "Fq09", "Categoria": "Fraqueza", "Tipo": "Interno", "Fator": "Infraestrutura física limitada para expansão de equipes", "Impacto": "Baixo", "Pontucao": 2},
        {"ID": "Fq10", "Categoria": "Fraqueza", "Tipo": "Interno", "Fator": "Falhas pontuais na integração de projetos transversais", "Impacto": "Médio", "Pontucao": 3},

        # 10 OPORTUNIDADES
        {"ID": "O01", "Categoria": "Oportunidade", "Tipo": "Externo", "Fator": "Integração de Inteligência Artificial para triagem de processos", "Impacto": "Alto", "Pontucao": 5},
        {"ID": "O02", "Categoria": "Oportunidade", "Tipo": "Externo", "Fator": "Parcerias acadêmicas para inovação no setor público", "Impacto": "Médio", "Pontucao": 4},
        {"ID": "O03", "Categoria": "Oportunidade", "Tipo": "Externo", "Fator": "Captação de recursos via fundos internacionais de modernização", "Impacto": "Alto", "Pontucao": 5},
        {"ID": "O04", "Categoria": "Oportunidade", "Tipo": "Externo", "Fator": "Expansão de metodologias EAD para capacitação em escala", "Impacto": "Médio", "Pontucao": 4},
        {"ID": "O05", "Categoria": "Oportunidade", "Tipo": "Externo", "Fator": "Conexão de dados com sistemas e plataformas nacionais", "Impacto": "Alto", "Pontucao": 5},
        {"ID": "O06", "Categoria": "Oportunidade", "Tipo": "Externo", "Fator": "Adoção de automação robótica de processos (RPA)", "Impacto": "Alto", "Pontucao": 4},
        {"ID": "O07", "Categoria": "Oportunidade", "Tipo": "Externo", "Fator": "Revisão e desburocratização de marcos regulatórios", "Impacto": "Médio", "Pontucao": 3},
        {"ID": "O08", "Categoria": "Oportunidade", "Tipo": "Externo", "Fator": "Consolidação do trabalho híbrido focado em entregas", "Impacto": "Médio", "Pontucao": 3},
        {"ID": "O09", "Categoria": "Oportunidade", "Tipo": "Externo", "Fator": "Uso intensivo de Analytics para apoio à decisão governamental", "Impacto": "Alto", "Pontucao": 5},
        {"ID": "O10", "Categoria": "Oportunidade", "Tipo": "Externo", "Fator": "Benchmarking contínuo com órgãos estaduais de referência", "Impacto": "Médio", "Pontucao": 3},

        # 10 AMEAÇAS
        {"ID": "A01", "Categoria": "Ameaça", "Tipo": "Externo", "Fator": "Contingenciamento severo de orçamento público", "Impacto": "Alto", "Pontucao": 5},
        {"ID": "A02", "Categoria": "Ameaça", "Tipo": "Externo", "Fator": "Alterações repentinas na legislação de diretrizes fiscais", "Impacto": "Alto", "Pontucao": 4},
        {"ID": "A03", "Categoria": "Ameaça", "Tipo": "Externo", "Fator": "Risco crescente de ataques cibernéticos e sequestro de dados", "Impacto": "Alto", "Pontucao": 5},
        {"ID": "A04", "Categoria": "Ameaça", "Tipo": "Externo", "Fator": "Aumento excessivo nos custos de licenças de software", "Impacto": "Médio", "Pontucao": 4},
        {"ID": "A05", "Categoria": "Ameaça", "Tipo": "Externo", "Fator": "Resistência de usuários externos às transformações digitais", "Impacto": "Médio", "Pontucao": 3},
        {"ID": "A06", "Categoria": "Ameaça", "Tipo": "Externo", "Fator": "Escassez de fornecedores homologados para licitações de TI", "Impacto": "Médio", "Pontucao": 3},
        {"ID": "A07", "Categoria": "Ameaça", "Tipo": "Externo", "Fator": "Instabilidades recorrentes na infraestrutura elétrica/telecom regional", "Impacto": "Médio", "Pontucao": 3},
        {"ID": "A08", "Categoria": "Ameaça", "Tipo": "Externo", "Fator": "Evasão de talentos técnicos para o setor privado", "Impacto": "Alto", "Pontucao": 4},
        {"ID": "A09", "Categoria": "Ameaça", "Tipo": "Externo", "Fator": "Burocracia excessiva e atrasos nos fluxos de compras públicas", "Impacto": "Alto", "Pontucao": 4},
        {"ID": "A10", "Categoria": "Ameaça", "Tipo": "Externo", "Fator": "Instabilidade econômica nacional afetando repasses estaduais", "Impacto": "Alto", "Pontucao": 4}
    ]
    return pd.DataFrame(data)

# ---------------------------------------------------------
# Gerador de PDF Avançado (ReportLab Canvas)
# ---------------------------------------------------------
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Cabeçalho
        self.drawString(54, 750, "SEPLAN/EPROC - Planejamento Estratégico Consolidado")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 742, 558, 742)
        
        # Rodapé
        page_text = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(558, 40, page_text)
        self.drawString(54, 40, "Documento Oficial de Diretrizes Estratégicas")
        self.line(54, 52, 558, 52)
        self.restoreState()

def build_pdf_report(df_swot):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=54, rightMargin=54,
        topMargin=72, bottomMargin=72
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Heading1'],
        fontSize=22, textColor=colors.HexColor("#1E3A8A"), spaceAfter=15
    )
    h2_style = ParagraphStyle(
        'SectionH2', parent=styles['Heading2'],
        fontSize=14, textColor=colors.HexColor("#0F766E"), spaceBefore=12, spaceAfter=8
    )

    story = []
    story.append(Paragraph("Relatório do Planejamento Estratégico", title_style))
    story.append(Paragraph("<b>Órgão:</b> SEPLAN / EPROC | <b>Ciclo:</b> 2026-2030", styles['Normal']))
    story.append(Spacer(1, 15))

    story.append(Paragraph("1. Diagnóstico da Matriz SWOT (40 Fatores)", h2_style))
    story.append(Paragraph("Resumo quantitativo dos fatores internos e externos levantados na pesquisa de campo.", styles['Normal']))
    story.append(Spacer(1, 10))

    # Tabela SWOT Consolidada
    table_data = [["ID", "Categoria", "Fator Estratégico", "Impacto", "Nota"]]
    for _, r in df_swot.iterrows():
        table_data.append([r['ID'], r['Categoria'], Paragraph(r['Fator'], styles['Normal']), r['Impacto'], str(r['Pontucao'])])

    t_swot = Table(table_data, colWidths=[35, 75, 270, 60, 40])
    t_swot.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('ALIGN', (0,0), (0,-1), 'CENTER'),
        ('ALIGN', (3,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    
    story.append(t_swot)
    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer

# ---------------------------------------------------------
# Interface Principal - Streamlit Navigation
# ---------------------------------------------------------
df_swot = get_full_swot_data()

st.markdown('<div class="main-header">Planejamento Estratégico EPROC / SEPLAN</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Plataforma Integrada de Gestão Estratégica, BSC, TOWS e Planos de Ação</div>', unsafe_allow_html=True)

menu = st.sidebar.radio(
    "Navegação do Projeto:",
    [
        "1. Diagnóstico SWOT (40 Fatores)",
        "2. Cruzamentos TOWS (Interativo)",
        "3. Mapa Estratégico (BSC)",
        "4. Planos de Ação 5W2H & ROI",
        "5. Memorial Metodológico",
        "6. Exportação de PDF"
    ]
)

# ---------------------------------------------------------
# 1. DIAGNÓSTICO SWOT
# ---------------------------------------------------------
if menu == "1. Diagnóstico SWOT (40 Fatores)":
    st.subheader("📊 Diagnóstico Organizacional Completo")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Forças (Interno)", len(df_swot[df_swot['Categoria']=='Força']))
    c2.metric("Fraquezas (Interno)", len(df_swot[df_swot['Categoria']=='Fraqueza']))
    c3.metric("Oportunidades (Externo)", len(df_swot[df_swot['Categoria']=='Oportunidade']))
    c4.metric("Ameaças (Externo)", len(df_swot[df_swot['Categoria']=='Ameaça']))
    
    st.markdown("---")
    
    col_chart, col_filter = st.columns([2, 1])
    with col_filter:
        st.write("**Filtros de Visualização**")
        cat_sel = st.multiselect("Categorias:", df_swot['Categoria'].unique(), default=df_swot['Categoria'].unique())
        imp_sel = st.multiselect("Nível de Impacto:", df_swot['Impacto'].unique(), default=df_swot['Impacto'].unique())
        
        filtered = df_swot[(df_swot['Categoria'].isin(cat_sel)) & (df_swot['Impacto'].isin(imp_sel))]
        st.write(f"Exibindo **{len(filtered)}** dos 40 fatores.")

    with col_chart:
        fig = px.bar(
            filtered, x="Categoria", y="Pontucao", color="Impacto", title="Matriz de Relevância dos Fatores SWOT",
            barmode="group", color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Lista Detalhada dos Fatores")
    for cat in ['Força', 'Fraqueza', 'Oportunidade', 'Ameaça']:
        if cat in cat_sel:
            st.markdown(f"#### {cat}s")
            cat_items = filtered[filtered['Categoria']==cat]
            for _, r in cat_items.iterrows():
                css_class = f"card-swot-{cat[0].lower() if cat != 'Fraqueza' else 'fq'}"
                st.markdown(f"<div class='{css_class}'><b>[{r['ID']}]</b> {r['Fator']} | <i>Impacto: {r['Impacto']}</i></div><br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. CRUZAMENTOS TOWS (INTERATIVO COM SORTABLES)
# ---------------------------------------------------------
elif menu == "2. Cruzamentos TOWS (Interativo)":
    st.subheader("🔀 Cruzamentos Estratégicos (Matriz TOWS)")
    st.markdown("Organize prioridades e defina combinações ativas arrastando os elementos.")

    st.info("💡 **Painel Interativo de Priorização:** Mova os fatores estratégicos entre os blocos de execução.")
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.write("**Estratégias SO (Alavancagem: Força + Oportunidade)**")
        so_items = sort_items([
            "[SO-1] Aplicar a equipe técnica no desenvolvimento de IA para triagem EPROC",
            "[SO-2] Usar a base centralizada para integração com plataformas nacionais"
        ], multi_containers=False, key="so_sort")
        
        st.write("**Estratégias ST (Vulnerabilidade: Força + Ameaça)**")
        st_items = sort_items([
            "[ST-1] Utilizar a estabilidade de rede para suportar redundâncias anti-ataque cibernético",
            "[ST-2] Usar a transparência dos processos para mitigar riscos de cortes orçamentários"
        ], multi_containers=False, key="st_sort")

    with col_right:
        st.write("**Estratégias WO (Restrições: Fraqueza + Oportunidade)**")
        wo_items = sort_items([
            "[WO-1] Adotar EAD institucional para contornar restrições orçamentárias de capacitação",
            "[WO-2] Substituir manutenção de sistemas legados por automação robótica (RPA)"
        ], multi_containers=False, key="wo_sort")

        st.write("**Estratégias WT (Problemas Críticos: Fraqueza + Ameaça)**")
        wt_items = sort_items([
            "[WT-1] Automatizar tarefas repetitivas para diminuir impacto por evasão de pessoal",
            "[WT-2] Padronizar documentação para reduzir tempo de resposta de chamados"
        ], multi_containers=False, key="wt_sort")

# ---------------------------------------------------------
# 3. MAPA ESTRATÉGICO BSC
# ---------------------------------------------------------
elif menu == "3. Mapa Estratégico (BSC)":
    st.subheader("🗺️ Mapa Estratégico em 4 Perspectivas")
    
    perspectivas = [
        {"Perspectiva": "1. Sociedade / Clientes", "Cor": "#1E3A8A", "Objetivos": ["Garantir Transparência nos Processos", "Reduzir Tempo de Resposta da SEPLAN"]},
        {"Perspectiva": "2. Processos Internos", "Cor": "#0D9488", "Objetivos": ["Automatizar 50% dos Fluxos via RPA", "Aprimorar Governança de Dados"]},
        {"Perspectiva": "3. Aprendizado e Crescimento", "Cor": "#D97706", "Objetivos": ["Capacitar 100% da Equipe em Analytics", "Promover Cultura de Inovação"]},
        {"Perspectiva": "4. Recursos e Orçamento", "Cor": "#DC2626", "Objetivos": ["Otimizar Alocação de Recursos de TI", "Maximizar ROI de Projetos Digital"]}
    ]

    for p in perspectivas:
        st.markdown(f"<div style='background-color:{p['Cor']}; padding:8px; border-radius:5px; color:white; font-weight:bold;'>{p['Perspectiva']}</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.info(f"📌 {p['Objetivos'][0]}")
        c2.info(f"📌 {p['Objetivos'][1]}")
        st.markdown("<div style='text-align:center; color:#94A3B8;'>↓ Relação de Causa e Efeito ↓</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. PLANOS DE AÇÃO 5W2H & ROI
# ---------------------------------------------------------
elif menu == "4. Planos de Ação 5W2H & ROI":
    st.subheader("📋 Planos de Ação 5W2H & Simulação de Impacto")
    
    actions = pd.DataFrame([
        {"O quê (What)": "Implantar RPA no EPROC", "Quem (Who)": "TI", "Quando (When)": "Q3 2026", "Onde (Where)": "SEPLAN", "Por que (Why)": "Eliminar tarefas repetitivas", "Como (How)": "Contratação de ferramenta RPA", "Custo (R$)": 50000, "ROI Est. (%)": 160},
        {"O quê (What)": "Plano EAD de Capacitação", "Quem (Who)": "RH", "Quando (When)": "Q2 2026", "Onde (Where)": "Portal SEPLAN", "Por que (Why)": "Mitigar defasagem técnica", "Como (How)": "Plataforma OpenSource EAD", "Custo (R$)": 15000, "ROI Est. (%)": 210},
        {"O quê (What)": "Reforço de Segurança Cibernética", "Quem (Who)": "Infra", "Quando (When)": "Q4 2026", "Onde (Where)": "Data Center", "Por que (Why)": "Proteger dados do EPROC", "Como (How)": "Auditoria externa e Firewalls", "Custo (R$)": 35000, "ROI Est. (%)": 120}
    ])

    st.dataframe(actions, use_container_width=True)

    st.markdown("---")
    st.subheader("🎮 Calculadora Interativa de ROI Estratégico")
    
    col_a, col_b = st.columns(2)
    investimento = col_a.number_input("Investimento Estimado (R$):", value=100000, step=5000)
    economia_horas = col_b.number_input("Horas Economizadas/Ano na Equipe:", value=1500, step=100)
    
    custo_hora_medio = 65.00
    retorno_financeiro = economia_horas * custo_hora_medio
    roi = ((retorno_financeiro - investimento) / investimento) * 100

    st.metric("Retorno Estimado em Horas/Ano", f"R$ {retorno_financeiro:,.2f}", delta=f"ROI: {roi:.1f}%")

# ---------------------------------------------------------
# 5. MEMORIAL METODOLÓGICO
# ---------------------------------------------------------
elif menu == "5. Memorial Metodológico":
    st.subheader("📜 Memorial Descritivo da Metodologia")
    st.markdown("""
    O Planejamento Estratégico da **EPROC/SEPLAN** foi construído seguindo uma sequência metodológica rigorosa:
    
    1. **Fase de Diagnóstico:** Levantamento de 40 fatores críticos divididos equitativamente entre Forças, Fraquezas, Oportunidades e Ameaças.
    2. **Fase de Formulação (TOWS):** Cruzamento dos ambientes interno e externo para definição de planos defensivos, ofensivos e de adaptação.
    3. **Fase de Alinhamento (BSC):** Estruturação dos objetivos em 4 perspectivas clássicas do Balanced Scorecard com mapeamento de causa e efeito.
    4. **Fase Operacional (5W2H):** Desdobramento em ações mensuráveis com estimativa de retorno sobre o investimento (ROI).
    """)

# ---------------------------------------------------------
# 6. EXPORTAÇÃO DE PDF
# ---------------------------------------------------------
elif menu == "6. Exportação de PDF":
    st.subheader("📄 Exportar Documento Completo em PDF")
    st.write("Clique no botão abaixo para compilar todos os dados consolidados da aplicação em um relatório executivo.")
    
    pdf_data = build_pdf_report(df_swot)
    st.download_button(
        label="📥 Baixar Planejamento Estratégico em PDF",
        data=pdf_data,
        file_name="Planejamento_Estrategico_EPROC_SEPLAN_Completo.pdf",
        mime="application/pdf"
    )
