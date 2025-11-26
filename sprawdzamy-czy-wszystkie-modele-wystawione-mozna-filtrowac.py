import io
import pandas as pd
import streamlit as st

# === USTAWIENIA PLIKU Z DANYMI ===
FILE_PATH = "nazwa_pliku.csv"   # tu wpisz dokładną nazwę pliku z repo
SEPARATOR = ","                 # jeśli CSV ma ; to zmień na ";"

st.set_page_config(layout="wide")
st.title("📦 26.11 Sprawdzamy, czy wszystkie modele są wystawione (z możliwością filtrowania konfiguracji)")

st.caption("Dane z ClickUp – grupowanie po modelu, procesorze, grafice i dotyku.")

@st.cache_data(show_spinner=False)
def load_data(path: str, sep: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep=sep, encoding="utf-8", on_bad_lines="skip")
    return df

# === WCZYTANIE DANYCH ===
try:
    df = load_data(FILE_PATH, SEPARATOR)
except FileNotFoundError:
    st.error(f"Nie znaleziono pliku: {FILE_PATH}. Upewnij się, że plik jest w repo obok tego skryptu.")
    st.stop()
except Exception as e:
    st.error(f"Błąd przy wczytywaniu pliku: {e}")
    st.stop()

st.success(f"Plik `{FILE_PATH}` został wczytany poprawnie.")

st.subheader("Podgląd danych (pierwsze 50 wierszy)")
st.dataframe(df.head(50), use_container_width=True)

# === SPRAWDZAMY KOLUMNY ===
required_cols = [
    "tags",
    "Procesor (drop down)",
    "Model Procesora (short text)",
    "Grafika (short text)",
    "Matryca (labels)",
]

missing = [c for c in required_cols if c not in df.columns]
if missing:
    st.error("Brakuje wymaganych kolumn w pliku CSV:\n" + ", ".join(missing))
    st.stop()

# Normalizacja modelu procesora dla spójności (lower/strip)
df["Model Procesora (short text)"] = (
    df["Model Procesora (short text)"]
    .astype(str)
    .str.lower()
    .str.strip()
)

# === SIDEBAR – USTAWIENIA GRUPOWANIA ===
st.sidebar.header("🔧 Ustawienia grupowania")

use_cpu_model = st.sidebar.checkbox("Uwzględnij **Model procesora (H)**", value=True)
use_gpu = st.sidebar.checkbox("Uwzględnij **Grafikę (I)**", value=True)

st.sidebar.subheader("🎯 Filtr modeli (tags)")
all_models = sorted(df["tags"].dropna().unique().tolist())
selected_models = st.sidebar.multiselect(
    "Wybierz modele (puste = wszystkie)",
    options=all_models,
)

# === FILTROWANIE PO MODELACH ===
if selected_models:
    df_filtered = df[df["tags"].isin(selected_models)].copy()
else:
    df_filtered = df.copy()

# === DOTYK / BRAK DOTYKU Z MATRYCY ===
mat = df_filtered["Matryca (labels)"].astype(str)
df_filtered["Dotyk_flag"] = mat.str.contains("dotyk", case=False, na=False).map(
    {True: "Dotyk", False: "Brak dotyku"}
)

# === BUDOWANIE KOLUMN DO GRUPOWANIA ===
group_cols = ["tags", "Procesor (drop down)"]  # model + typ CPU zawsze

if use_cpu_model:
    group_cols.append("Model Procesora (short text)")

if use_gpu:
    group_cols.append("Grafika (short text)")

group_cols.append("Dotyk_flag")  # zawsze rozróżniamy dotyk / brak dotyku

# === GRUPOWANIE ===
grouped = (
    df_filtered
    .groupby(group_cols, dropna=False)
    .size()
    .reset_index(name="Ilość sztuk")
)

# sortujemy po modelu, procesorze, dotyku
sort_cols = [c for c in ["tags", "Procesor (drop down)", "Dotyk_flag"] if c in grouped.columns]
grouped = grouped.sort_values(by=sort_cols)

# === WYNIK ===
st.subheader("📊 Zestawienie konfiguracji")
st.write(f"Liczba różnych konfiguracji: **{len(grouped)}**")

st.dataframe(grouped, use_container_width=True)

# === EXPORT DO EXCEL ===
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
    grouped.to_excel(writer, index=False, sheet_name="Zestawienie")
buffer.seek(0)

st.download_button(
    label="📥 Pobierz zestawienie do Excel",
    data=buffer,
    file_name="zestawienie_konfiguracji_magazynu.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
