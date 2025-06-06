import pandas as pd
import streamlit as st
import urllib.parse

st.set_page_config(layout="wide")
st.title("Magazyn z ClickUp - aktualizacja 29.05.2025 - wersja BETA")

file_path = "nazwa_pliku.csv"
separator = ','

try:
    df = pd.read_csv(file_path, sep=separator, encoding='utf-8', on_bad_lines='skip')
    st.write("Plik został wczytany poprawnie!")
    
    # Normalizacja modelu procesora
    if "Model Procesora (short text)" in df.columns:
        df["Model Procesora (short text)"] = (
            df["Model Procesora (short text)"]
            .str.lower()
            .str.strip()
        )
    
    if "tags" not in df.columns:
        st.error("Brak kolumny 'tags' w pliku CSV. Sprawdź plik.")
    else:
        st.sidebar.header("Filtry")
        
        # Pobranie parametrów z URL
        query_params = st.experimental_get_query_params()
        default_tag = query_params.get("tag", ["Wszystkie"])[0]
        default_processor = query_params.get("processor", ["Wszystkie"])[0]
        default_processor_model = query_params.get("processor_model", ["Wszystkie"])[0]
        default_resolution = query_params.get("resolution", ["Wszystkie"])[0]
        default_destinations = query_params.get("destinations", [])
        default_list = query_params.get("list", ["Wszystkie"])[0]
        
        # Filtry w sidebarze
        unique_tags = df["tags"].unique().tolist()
        selected_tag = st.sidebar.selectbox(
            "Wybierz tag",
            ["Wszystkie"] + unique_tags,
            index=(["Wszystkie"] + unique_tags).index(default_tag)
                  if default_tag in (["Wszystkie"] + unique_tags) else 0
        )
        
        unique_processors = df["Procesor (drop down)"].unique().tolist()
        selected_processor = st.sidebar.selectbox(
            "Wybierz procesor",
            ["Wszystkie"] + unique_processors,
            index=(["Wszystkie"] + unique_processors).index(default_processor)
                  if default_processor in (["Wszystkie"] + unique_processors) else 0
        )
        
        unique_processor_models = df["Model Procesora (short text)"].unique().tolist()
        if default_processor_model != "Wszystkie":
            default_processor_model = default_processor_model.lower().strip()
        selected_processor_model = st.sidebar.selectbox(
            "Wybierz model procesora",
            ["Wszystkie"] + unique_processor_models,
            index=(["Wszystkie"] + unique_processor_models).index(default_processor_model)
                  if default_processor_model in (["Wszystkie"] + unique_processor_models) else 0
        )
        
        unique_resolutions = df["Rozdzielczość (drop down)"].unique().tolist()
        selected_resolution = st.sidebar.selectbox(
            "Wybierz rozdzielczość",
            ["Wszystkie"] + unique_resolutions,
            index=(["Wszystkie"] + unique_resolutions).index(default_resolution)
                  if default_resolution in (["Wszystkie"] + unique_resolutions) else 0
        )
        
        selected_destinations = st.sidebar.multiselect(
            "Wybierz przeznaczenie",
            df["Przeznaczenie (drop down)"].unique().tolist(),
            default=default_destinations
        )
        
        unique_lists = df["Lists"].unique().tolist()
        selected_list = st.sidebar.selectbox(
            "Wybierz listę",
            ["Wszystkie"] + unique_lists,
            index=(["Wszystkie"] + unique_lists).index(default_list)
                  if default_list in (["Wszystkie"] + unique_lists) else 0
        )
        
        # Ustawienie query params
        new_query_params = {
            "tag": [selected_tag],
            "processor": [selected_processor],
            "processor_model": [selected_processor_model],
            "resolution": [selected_resolution],
            "destinations": selected_destinations,
            "list": [selected_list]
        }
        
        if st.sidebar.button("Kliknij aby udostępnić"):
            st.experimental_set_query_params(**new_query_params)
            query_string = urllib.parse.urlencode(new_query_params, doseq=True)
            base_url = st.request.host_url if hasattr(st, "request") else ""
            full_url = base_url + "?" + query_string if base_url else ""
            st.sidebar.success("Filtry zapisane!")
            st.sidebar.info(f"Skopiuj URL z paska przeglądarki: {full_url}")
        
        # Filtrowanie danych
        filtered_df = df.copy()
        if selected_tag != "Wszystkie":
            filtered_df = (
                filtered_df[filtered_df["tags"].isna()]
                if pd.isna(selected_tag)
                else filtered_df[filtered_df["tags"] == selected_tag]
            )
        if selected_processor != "Wszystkie":
            filtered_df = (
                filtered_df[filtered_df["Procesor (drop down)"].isna()]
                if pd.isna(selected_processor)
                else filtered_df[filtered_df["Procesor (drop down)"] == selected_processor]
            )
        if selected_processor_model != "Wszystkie":
            filtered_df = (
                filtered_df[filtered_df["Model Procesora (short text)"].isna()]
                if pd.isna(selected_processor_model)
                else filtered_df[filtered_df["Model Procesora (short text)"] == selected_processor_model]
            )
        if selected_resolution != "Wszystkie":
            filtered_df = (
                filtered_df[filtered_df["Rozdzielczość (drop down)"].isna()]
                if pd.isna(selected_resolution)
                else filtered_df[filtered_df["Rozdzielczość (drop down)"] == selected_resolution]
            )
        if selected_destinations:
            filtered_df = filtered_df[filtered_df["Przeznaczenie (drop down)"].isin(selected_destinations)]
        if selected_list != "Wszystkie":
            filtered_df = (
                filtered_df[filtered_df["Lists"].isna()]
                if pd.isna(selected_list)
                else filtered_df[filtered_df["Lists"] == selected_list]
            )
        
        # Wyświetlenie przefiltrowanych danych
        st.write("### Przefiltrowane dane")
        st.dataframe(filtered_df, height=500)
        st.write(f"Liczba pokazywanych pozycji: {len(filtered_df)}")
        
        # Eksport do Excel
        excel_buffer = pd.ExcelWriter('filtered_data.xlsx', engine='xlsxwriter')
        filtered_df.to_excel(excel_buffer, index=False)
        excel_buffer.close()
        with open("filtered_data.xlsx", "rb") as f:
            st.download_button(
                label="Pobierz dane jako Excel",
                data=f,
                file_name="filtered_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        # Pogrupowanie modeli z tagami
        st.write("### Pogrupowane modele – tagi + procesor + model (malejąco)")
        models_summary = (
            df
            .value_counts(["tags", "Procesor (drop down)", "Model Procesora (short text)"])
            .reset_index(name="Liczba")
            .sort_values("Liczba", ascending=False)
            .reset_index(drop=True)
        )
        models_summary.columns = ["Tag", "Procesor", "Model Procesora", "Liczba"]
        st.dataframe(models_summary, height=500)

except pd.errors.ParserError as e:
    st.error(f"Błąd parsowania pliku CSV: {e}")
except UnicodeDecodeError as e:
    st.error(f"Błąd kodowania: {e}")
except KeyError as e:
    st.error(f"Brak wymaganej kolumny w pliku CSV: {e}")
except FileNotFoundError:
    st.error(f"Nie znaleziono pliku: {file_path}. Upewnij się, że plik znajduje się w folderze z kodem.")
except Exception as e:
    st.error(f"Nieoczekiwany błąd: {e}")
