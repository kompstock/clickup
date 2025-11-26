import io
import pandas as pd
import streamlit as st

# --- USTAWIENIA ---
FILE_PATH = "nazwa_pliku.csv"  # <-- 
SEPARATOR = ","                    # jeśli trzeba, zmień na ";"

st.set_page_config(page_title="Zestawienie konfiguracji magazynu", layout="wide")
st.title("📦 Zestawienie konfiguracji laptopów z magazynu (ClickUp)")

@st.cache_data(show_spinner=False)
def load_data(path: str, sep: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep=sep, encoding="utf-8", on_bad_lines="skip")
    return df

# --- Wczytanie danych ---
try:
    df = load_data(FILE_PATH, SEPARATOR)
except FileNotFoundError:
    st.error(f"Nie znaleziono pliku: {FILE_PATH}. Upewnij się, że plik CSV jest w repo obok app.py.")
    st.stop()
except Exception as e:
    st.error(f"Błąd przy wczytywaniu pliku: {e}")
    st.stop()

st.success(f"Plik `{FILE_PATH}` został wczytany poprawnie.")
st.write("Podgląd danych (pierwsze 50 wierszy):")
st.dataframe(df.head(50), use_container_width=True)

# --- Sprawdzenie wymaganych kolumn ---
required_cols = [
    "tags",
    "Procesor (drop down)",
    "Model Procesora (short text)",
    "Grafika (short text)",
    "Matryca (labels)",
]

missing = [c for c in required_cols if c not in df.columns]
if missing:
    st.error("Brakuje kolumn w pliku CSV:\n" + ", ".join(missing))
    st.stop()

# Normalizacja modelu CPU (żeby i7-6820HQ vs I7-6820hq nie rozdzielało)
df["Model Procesora (short text)"] = (
    df["Model Procesora (short text)"]
    .astype(str)
    .str.lower()
    .str.strip()
)

# --- Sidebar: ustawienia grupowania ---
st.sidebar.header("🔧 Ustawienia grupowania")

use_cpu_model = st.sidebar.checkbox("Uwzględnij *Model procesora (H)*", value=True)
use_gpu = st.sidebar.checkbox("Uwzględnij *Grafikę (I)*", value=True)

# Opcjonalny filtr po modelu (tags)
st.sidebar.subheader("🎯 Filtr modeli (tags)")
all_models = sorted(df["tags"].dropna().unique().tolist())
selected_models = st.sidebar.multiselect(
    "Wybierz modele (puste = wszystkie)",
    options=all_models,
)

# --- Filtrowanie wejściowych danych po modelu ---
if selected_models:
    df_filtered = df[df["tags"].isin(selected_models)].copy()
else:
    df_filtered = df.copy()

# --- Flaga Dotyk / Brak dotyku z Matryca (labels) ---
mat = df_filtered["Matryca (labels)"].astype(str)
df_filtered["__Dotyk__"] = mat.str.contains("dotyk", case=False, na=False).map(
    {True: "Dotyk", False: "Brak dotyku"}
)

# --- Budowa listy kolumn do grupowania ---
group_cols = ["tags", "Procesor (drop down)"]  # model + typ CPU zawsze

if use_cpu_model:
    group_cols.append("Model Procesora (short text)")

if use_gpu:
    group_cols.append("Grafika (short text)")

group_cols.append("__Dotyk__")  # zawsze rozróżniamy dotyk

# --- Grupowanie ---
grouped = (
    df_filtered
    .groupby(group_cols, dropna=False)
    .size()
    .reset_index(name="Ilość sztuk")
)

# Sortowanie wyników po modelu, CPU i Dotyk/Brak dotyku
sort_cols = ["tags", "Procesor (drop down)", "__Dotyk__"]
sort_cols = [c for c in sort_cols if c in grouped.columns]

grouped = grouped.sort_values(by=sort_cols)

# --- Wyświetlenie wyniku ---
st.subheader("📊 Zestawienie konfiguracji")
st.write(f"Liczba różnych konfiguracji: **{len(grouped)}**")
st.dataframe(grouped, use_container_width=True)

# --- Export do Excela ---
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
