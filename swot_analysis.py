from __future__ import annotations

import io
import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

import numpy as np
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from sklearn.cluster import AgglomerativeClustering
from sklearn.feature_extraction.text import TfidfVectorizer


SWOT_DIMENSIONS = ("Força", "Fraqueza", "Oportunidade", "Ameaça")
SWOT_PLURAL = {
    "Força": "Forças",
    "Fraqueza": "Fraquezas",
    "Oportunidade": "Oportunidades",
    "Ameaça": "Ameaças",
}

COLUMN_ALIASES = {
    "Força": {"forca", "forcas", "strength", "strengths", "ponto forte", "pontos fortes"},
    "Fraqueza": {"fraqueza", "fraquezas", "weakness", "weaknesses", "ponto fraco", "pontos fracos"},
    "Oportunidade": {"oportunidade", "oportunidades", "opportunity", "opportunities"},
    "Ameaça": {"ameaca", "ameacas", "threat", "threats", "risco", "riscos"},
}

GENERIC_WORDS = {
    "empresa", "organizacao", "organização", "companhia", "instituicao", "instituição",
    "forca", "força", "forcas", "forças", "fraqueza", "fraquezas", "oportunidade",
    "oportunidades", "ameaca", "ameaça", "ameacas", "ameaças", "possui", "possuir",
    "tem", "ter", "muito", "muita", "muitos", "muitas", "grande", "bom", "boa",
    "bons", "boas", "excelente", "excelentes", "destaque", "destaca", "destacam",
    "principal", "principais", "considero", "considerada", "considerado", "ponto",
    "aspecto", "questao", "questão", "fator", "fatores", "capacidade", "relacionado",
    "relacionada", "relacionados", "relacionadas",
}

FALLBACK_STOPWORDS = {
    "a", "ao", "aos", "aquela", "aquelas", "aquele", "aqueles", "as", "até", "com",
    "como", "da", "das", "de", "dela", "dele", "deles", "do", "dos", "e", "ela",
    "elas", "ele", "eles", "em", "entre", "era", "essa", "essas", "esse", "esses",
    "esta", "está", "estas", "este", "estes", "eu", "foi", "há", "isso", "isto", "já",
    "mais", "mas", "me", "mesmo", "minha", "meu", "na", "nas", "não", "nem", "no",
    "nos", "nós", "nossa", "nosso", "o", "os", "ou", "para", "pela", "pelas", "pelo",
    "pelos", "por", "qual", "quando", "que", "se", "sem", "ser", "sua", "suas", "seu",
    "seus", "também", "tem", "um", "uma", "você",
}

TOKENIZER = RegexpTokenizer(r"[A-Za-zÀ-ÖØ-öø-ÿ]+(?:-[A-Za-zÀ-ÖØ-öø-ÿ]+)?")


@dataclass(frozen=True)
class AnalysisConfig:
    similarity_threshold: float = 0.72
    max_concepts: int = 15
    model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def normalize_text(value: Any) -> str:
    """Normaliza espaços e caracteres sem remover acentos do texto original."""
    text = unicodedata.normalize("NFKC", str(value))
    return re.sub(r"\s+", " ", text).strip()


def normalize_identifier(value: Any) -> str:
    """Cria uma versão sem acentos para comparar nomes de colunas."""
    text = normalize_text(value).casefold()
    text = "".join(
        char for char in unicodedata.normalize("NFD", text)
        if unicodedata.category(char) != "Mn"
    )
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def infer_column_mapping(columns: Iterable[Any]) -> dict[str, Any | None]:
    """Tenta associar automaticamente as colunas do arquivo às quatro dimensões SWOT."""
    columns = list(columns)
    normalized = {column: normalize_identifier(column) for column in columns}
    mapping: dict[str, Any | None] = {}

    for dimension in SWOT_DIMENSIONS:
        aliases = {normalize_identifier(alias) for alias in COLUMN_ALIASES[dimension]}
        exact = next((column for column, name in normalized.items() if name in aliases), None)
        if exact is not None:
            mapping[dimension] = exact
            continue

        partial = next(
            (
                column
                for column, name in normalized.items()
                if any(alias in name or name in alias for alias in aliases)
            ),
            None,
        )
        mapping[dimension] = partial

    return mapping


def get_portuguese_stopwords() -> set[str]:
    """Obtém stopwords do NLTK; usa uma lista local se o recurso não estiver disponível."""
    try:
        words = set(stopwords.words("portuguese"))
    except LookupError:
        words = set(FALLBACK_STOPWORDS)
    return words.union(GENERIC_WORDS)


def tokenize_relevant(text: str, stop_words: set[str]) -> list[str]:
    tokens = TOKENIZER.tokenize(normalize_text(text).casefold())
    return [
        token
        for token in tokens
        if len(token) > 2 and token not in stop_words
    ]


def _fit_agglomerative(embeddings: np.ndarray, *, n_clusters: int | None, distance_threshold: float | None) -> np.ndarray:
    kwargs = {
        "n_clusters": n_clusters,
        "linkage": "average",
        "distance_threshold": distance_threshold,
    }
    try:
        clusterer = AgglomerativeClustering(metric="cosine", **kwargs)
    except TypeError:  # Compatibilidade com versões antigas do scikit-learn.
        clusterer = AgglomerativeClustering(affinity="cosine", **kwargs)
    return clusterer.fit_predict(embeddings)


def cluster_embeddings(
    embeddings: np.ndarray,
    similarity_threshold: float,
    max_concepts: int,
) -> np.ndarray:
    """Agrupa por limiar semântico e garante no máximo max_concepts grupos."""
    sample_count = len(embeddings)
    if sample_count == 0:
        return np.array([], dtype=int)
    if sample_count == 1:
        return np.array([0], dtype=int)

    max_concepts = max(1, min(int(max_concepts), 15, sample_count))
    similarity_threshold = float(np.clip(similarity_threshold, 0.0, 0.99))
    distance_threshold = max(0.01, 1.0 - similarity_threshold)

    labels = _fit_agglomerative(
        embeddings,
        n_clusters=None,
        distance_threshold=distance_threshold,
    )

    if len(np.unique(labels)) > max_concepts:
        labels = _fit_agglomerative(
            embeddings,
            n_clusters=max_concepts,
            distance_threshold=None,
        )

    return labels


def _capitalize_label(text: str) -> str:
    text = normalize_text(text).strip(" .,:;-/|_")
    if not text:
        return "Conceito não identificado"
    return text[0].upper() + text[1:]


def _representative_text(indices: np.ndarray, texts: list[str], embeddings: np.ndarray) -> str:
    cluster_embeddings_matrix = embeddings[indices]
    centroid = cluster_embeddings_matrix.mean(axis=0)
    norm = np.linalg.norm(centroid)
    if norm:
        centroid = centroid / norm
    similarities = cluster_embeddings_matrix @ centroid
    best_similarity = similarities.max()
    candidates = np.where(similarities >= best_similarity - 0.04)[0]
    candidate_lengths = np.array([len(texts[indices[i]].split()) for i in candidates])
    local_index = candidates[np.argmin(candidate_lengths)]
    return texts[indices[local_index]]


def _build_tfidf(texts: list[str], stop_words: set[str]):
    vectorizer = TfidfVectorizer(
        tokenizer=lambda value: tokenize_relevant(value, stop_words),
        token_pattern=None,
        preprocessor=None,
        lowercase=False,
        ngram_range=(1, 3),
        sublinear_tf=True,
        max_features=5000,
    )
    try:
        matrix = vectorizer.fit_transform(texts)
        terms = np.asarray(vectorizer.get_feature_names_out())
        return matrix, terms
    except ValueError:
        return None, None


def _candidate_keyphrases(
    indices: np.ndarray,
    tfidf_matrix,
    tfidf_terms: np.ndarray | None,
) -> list[str]:
    if tfidf_matrix is None or tfidf_terms is None or len(tfidf_terms) == 0:
        return []

    mean_scores = np.asarray(tfidf_matrix[indices].mean(axis=0)).ravel()
    word_counts = np.asarray([len(term.split()) for term in tfidf_terms])

    # Expressões curtas de 2 ou 3 palavras costumam formar conceitos melhores.
    phrase_weight = np.select(
        [word_counts == 3, word_counts == 2, word_counts == 1],
        [1.45, 1.35, 0.90],
        default=0.70,
    )
    adjusted_scores = mean_scores * phrase_weight
    ranked = np.argsort(adjusted_scores)[::-1]

    candidates: list[str] = []
    for index in ranked:
        if adjusted_scores[index] <= 0:
            break
        term = str(tfidf_terms[index])
        if term not in candidates:
            candidates.append(term)
        if len(candidates) >= 8:
            break
    return candidates


def create_cluster_labels(
    labels: np.ndarray,
    texts: list[str],
    embeddings: np.ndarray,
    stop_words: set[str],
) -> dict[int, str]:
    """Gera rótulos curtos e evita nomes duplicados dentro de uma dimensão."""
    tfidf_matrix, tfidf_terms = _build_tfidf(texts, stop_words)
    labels_by_cluster: dict[int, str] = {}
    used_labels: set[str] = set()

    for cluster_id in np.unique(labels):
        indices = np.where(labels == cluster_id)[0]
        representative = _representative_text(indices, texts, embeddings)
        keyphrases = _candidate_keyphrases(indices, tfidf_matrix, tfidf_terms)

        candidates: list[str] = []
        if len(representative.split()) <= 7 and len(representative) <= 90:
            candidates.append(representative)
        candidates.extend(keyphrases)
        if len(representative.split()) > 7:
            candidates.append(" ".join(representative.split()[:7]))

        chosen: str | None = None
        for candidate in candidates:
            formatted = _capitalize_label(candidate)
            normalized = normalize_identifier(formatted)
            if normalized and normalized not in used_labels:
                chosen = formatted
                used_labels.add(normalized)
                break

        if chosen is None:
            base_number = len(labels_by_cluster) + 1
            chosen = f"Conceito {base_number}"
            while normalize_identifier(chosen) in used_labels:
                base_number += 1
                chosen = f"Conceito {base_number}"
            used_labels.add(normalize_identifier(chosen))

        labels_by_cluster[int(cluster_id)] = chosen

    return labels_by_cluster


def analyze_dimension(
    series: pd.Series,
    dimension: str,
    model: Any,
    config: AnalysisConfig,
    stop_words: set[str] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Analisa uma coluna SWOT e devolve o mapeamento bruto e o resumo dos conceitos."""
    stop_words = stop_words or get_portuguese_stopwords()

    raw_records: list[dict[str, Any]] = []
    for position, (source_index, value) in enumerate(series.items(), start=1):
        if pd.isna(value):
            continue
        raw_text = normalize_text(value)
        if not raw_text:
            continue
        raw_records.append(
            {
                "Dimensão": dimension,
                "Linha original": int(source_index) + 2 if isinstance(source_index, (int, np.integer)) else position + 1,
                "Dado bruto": raw_text,
                "Texto normalizado": normalize_identifier(raw_text),
            }
        )

    if not raw_records:
        empty_mapping = pd.DataFrame(
            columns=["Dimensão", "Linha original", "Dado bruto", "Grupo ID", "Conceito agrupado"]
        )
        empty_summary = pd.DataFrame(
            columns=["Dimensão", "Grupo ID", "Conceito agrupado", "Quantidade", "Exemplos"]
        )
        return empty_mapping, empty_summary

    raw_df = pd.DataFrame(raw_records)

    # Textos idênticos são processados uma única vez, mas mantêm sua frequência no resultado.
    unique_df = raw_df.drop_duplicates(subset="Texto normalizado", keep="first").reset_index(drop=True)
    unique_texts = unique_df["Dado bruto"].tolist()

    embeddings = model.encode(
        unique_texts,
        batch_size=32,
        show_progress_bar=False,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    embeddings = np.asarray(embeddings, dtype=float)

    labels = cluster_embeddings(
        embeddings,
        similarity_threshold=config.similarity_threshold,
        max_concepts=config.max_concepts,
    )
    concept_labels = create_cluster_labels(labels, unique_texts, embeddings, stop_words)

    unique_df["Cluster interno"] = labels
    cluster_lookup = dict(zip(unique_df["Texto normalizado"], unique_df["Cluster interno"]))
    raw_df["Cluster interno"] = raw_df["Texto normalizado"].map(cluster_lookup)

    # Renumera os grupos por frequência, do maior para o menor.
    ordered_clusters = (
        raw_df.groupby("Cluster interno")
        .size()
        .sort_values(ascending=False, kind="stable")
        .index
        .tolist()
    )
    group_id_lookup = {cluster_id: order + 1 for order, cluster_id in enumerate(ordered_clusters)}
    raw_df["Grupo ID"] = raw_df["Cluster interno"].map(group_id_lookup).astype(int)
    raw_df["Conceito agrupado"] = raw_df["Cluster interno"].map(concept_labels)

    mapping_df = raw_df[
        ["Dimensão", "Linha original", "Dado bruto", "Grupo ID", "Conceito agrupado"]
    ].sort_values(["Grupo ID", "Linha original"], kind="stable").reset_index(drop=True)

    summary_rows: list[dict[str, Any]] = []
    for group_id, group in mapping_df.groupby("Grupo ID", sort=True):
        examples = list(dict.fromkeys(group["Dado bruto"].tolist()))[:3]
        summary_rows.append(
            {
                "Dimensão": dimension,
                "Grupo ID": int(group_id),
                "Conceito agrupado": group["Conceito agrupado"].iloc[0],
                "Quantidade": int(len(group)),
                "Exemplos": " | ".join(examples),
            }
        )

    summary_df = pd.DataFrame(summary_rows)
    return mapping_df, summary_df


def analyze_swot_dataframe(
    dataframe: pd.DataFrame,
    column_mapping: Mapping[str, Any],
    model: Any,
    config_by_dimension: Mapping[str, AnalysisConfig],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Executa a análise das quatro dimensões da matriz SWOT."""
    stop_words = get_portuguese_stopwords()
    mappings: list[pd.DataFrame] = []
    summaries: list[pd.DataFrame] = []

    for dimension in SWOT_DIMENSIONS:
        column = column_mapping.get(dimension)
        if column is None or column not in dataframe.columns:
            continue
        mapping_df, summary_df = analyze_dimension(
            dataframe[column],
            dimension,
            model,
            config_by_dimension[dimension],
            stop_words=stop_words,
        )
        mappings.append(mapping_df)
        summaries.append(summary_df)

    mapping_result = pd.concat(mappings, ignore_index=True) if mappings else pd.DataFrame()
    summary_result = pd.concat(summaries, ignore_index=True) if summaries else pd.DataFrame()
    return mapping_result, summary_result


def apply_edited_labels(mapping_df: pd.DataFrame, edited_summary_df: pd.DataFrame) -> pd.DataFrame:
    """Aplica ao mapeamento os nomes de conceitos revisados pelo usuário."""
    if mapping_df.empty or edited_summary_df.empty:
        return mapping_df.copy()

    label_lookup = {
        (row["Dimensão"], int(row["Grupo ID"])): normalize_text(row["Conceito agrupado"])
        for _, row in edited_summary_df.iterrows()
    }
    result = mapping_df.copy()
    result["Conceito agrupado"] = [
        label_lookup.get((dimension, int(group_id)), current)
        for dimension, group_id, current in zip(
            result["Dimensão"], result["Grupo ID"], result["Conceito agrupado"]
        )
    ]
    return result


def make_wide_mapping(mapping_df: pd.DataFrame) -> pd.DataFrame:
    """Monta uma tabela com dado bruto e agrupado lado a lado para cada dimensão."""
    columns: dict[str, pd.Series] = {}
    for dimension in SWOT_DIMENSIONS:
        subset = mapping_df[mapping_df["Dimensão"] == dimension].sort_values("Linha original", kind="stable")
        plural = SWOT_PLURAL[dimension]
        columns[f"{plural} - Dado bruto"] = pd.Series(subset["Dado bruto"].tolist(), dtype="object")
        columns[f"{plural} - Conceito agrupado"] = pd.Series(
            subset["Conceito agrupado"].tolist(), dtype="object"
        )
    return pd.DataFrame(columns)


def build_excel_bytes(
    mapping_df: pd.DataFrame,
    summary_df: pd.DataFrame,
    config_by_dimension: Mapping[str, AnalysisConfig],
    source_filename: str,
) -> bytes:
    """Gera um Excel formatado com matriz consolidada, resumo e mapeamento completo."""
    output = io.BytesIO()
    wide_df = make_wide_mapping(mapping_df)

    category_styles = {
        "Força": {"header": "#548235", "light": "#E2F0D9"},
        "Fraqueza": {"header": "#C65911", "light": "#FCE4D6"},
        "Oportunidade": {"header": "#2F75B5", "light": "#DDEBF7"},
        "Ameaça": {"header": "#7030A0", "light": "#E4DFEC"},
    }

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        workbook = writer.book
        matrix_sheet = workbook.add_worksheet("Matriz SWOT")
        writer.sheets["Matriz SWOT"] = matrix_sheet

        title_format = workbook.add_format(
            {
                "bold": True,
                "font_size": 18,
                "font_color": "#1F1F1F",
                "align": "center",
                "valign": "vcenter",
            }
        )
        subtitle_format = workbook.add_format(
            {"italic": True, "font_color": "#666666", "align": "center"}
        )
        matrix_sheet.merge_range("A1:E1", "Matriz SWOT consolidada", title_format)
        matrix_sheet.merge_range(
            "A2:E2",
            f"Arquivo de origem: {source_filename}",
            subtitle_format,
        )

        def write_quadrant(dimension: str, start_row: int, start_col: int) -> None:
            style = category_styles[dimension]
            header_format = workbook.add_format(
                {
                    "bold": True,
                    "font_color": "#FFFFFF",
                    "bg_color": style["header"],
                    "align": "center",
                    "valign": "vcenter",
                    "border": 1,
                }
            )
            concept_format = workbook.add_format(
                {
                    "bg_color": style["light"],
                    "text_wrap": True,
                    "valign": "top",
                    "border": 1,
                }
            )
            count_format = workbook.add_format(
                {
                    "bg_color": style["light"],
                    "align": "center",
                    "valign": "vcenter",
                    "border": 1,
                }
            )
            matrix_sheet.write(start_row, start_col, SWOT_PLURAL[dimension], header_format)
            matrix_sheet.write(start_row, start_col + 1, "Qtd.", header_format)

            subset = (
                summary_df[summary_df["Dimensão"] == dimension]
                .sort_values(["Quantidade", "Grupo ID"], ascending=[False, True], kind="stable")
                .head(15)
            )
            for offset in range(15):
                row = start_row + 1 + offset
                if offset < len(subset):
                    record = subset.iloc[offset]
                    matrix_sheet.write(row, start_col, record["Conceito agrupado"], concept_format)
                    matrix_sheet.write_number(row, start_col + 1, int(record["Quantidade"]), count_format)
                else:
                    matrix_sheet.write_blank(row, start_col, None, concept_format)
                    matrix_sheet.write_blank(row, start_col + 1, None, count_format)

        write_quadrant("Força", 3, 0)
        write_quadrant("Fraqueza", 3, 3)
        write_quadrant("Oportunidade", 21, 0)
        write_quadrant("Ameaça", 21, 3)

        matrix_sheet.set_column("A:A", 42)
        matrix_sheet.set_column("B:B", 8)
        matrix_sheet.set_column("C:C", 3)
        matrix_sheet.set_column("D:D", 42)
        matrix_sheet.set_column("E:E", 8)
        matrix_sheet.set_row(0, 28)
        matrix_sheet.freeze_panes(3, 0)

        summary_df.to_excel(writer, sheet_name="Conceitos", index=False)
        mapping_df.to_excel(writer, sheet_name="Mapeamento", index=False)
        wide_df.to_excel(writer, sheet_name="Dados lado a lado", index=False)

        parameter_rows = []
        for dimension in SWOT_DIMENSIONS:
            config = config_by_dimension[dimension]
            parameter_rows.append(
                {
                    "Dimensão": dimension,
                    "Limiar de similaridade": config.similarity_threshold,
                    "Máximo de conceitos": config.max_concepts,
                    "Modelo semântico": config.model_name,
                }
            )
        parameters_df = pd.DataFrame(parameter_rows)
        parameters_df.to_excel(writer, sheet_name="Parâmetros", index=False)

        header_format = workbook.add_format(
            {
                "bold": True,
                "font_color": "#FFFFFF",
                "bg_color": "#1F4E78",
                "align": "center",
                "valign": "vcenter",
                "border": 1,
            }
        )
        text_format = workbook.add_format({"text_wrap": True, "valign": "top", "border": 1})
        integer_format = workbook.add_format({"align": "center", "border": 1, "num_format": "0"})
        decimal_format = workbook.add_format({"align": "center", "border": 1, "num_format": "0.00"})

        sheet_settings = {
            "Conceitos": [16, 10, 34, 12, 70],
            "Mapeamento": [16, 14, 70, 10, 34],
            "Dados lado a lado": [55] * len(wide_df.columns),
            "Parâmetros": [16, 22, 20, 58],
        }

        for sheet_name, widths in sheet_settings.items():
            worksheet = writer.sheets[sheet_name]
            worksheet.freeze_panes(1, 0)
            worksheet.autofilter(0, 0, max(1, worksheet.dim_rowmax), max(0, worksheet.dim_colmax))
            worksheet.set_row(0, 24, header_format)
            for column_index, width in enumerate(widths):
                worksheet.set_column(column_index, column_index, width)

            # Formatação dos dados.
            max_row = max(1, worksheet.dim_rowmax)
            max_col = max(0, worksheet.dim_colmax)
            for column_index in range(max_col + 1):
                worksheet.set_column(column_index, column_index, widths[column_index], text_format)

            # Reaplica o cabeçalho após a formatação das colunas.
            for column_index, column_name in enumerate(
                {
                    "Conceitos": summary_df.columns,
                    "Mapeamento": mapping_df.columns,
                    "Dados lado a lado": wide_df.columns,
                    "Parâmetros": parameters_df.columns,
                }[sheet_name]
            ):
                worksheet.write(0, column_index, column_name, header_format)

            if sheet_name == "Conceitos":
                worksheet.set_column(1, 1, 10, integer_format)
                worksheet.set_column(3, 3, 12, integer_format)
            elif sheet_name == "Mapeamento":
                worksheet.set_column(1, 1, 14, integer_format)
                worksheet.set_column(3, 3, 10, integer_format)
            elif sheet_name == "Parâmetros":
                worksheet.set_column(1, 1, 22, decimal_format)
                worksheet.set_column(2, 2, 20, integer_format)

    output.seek(0)
    return output.getvalue()
