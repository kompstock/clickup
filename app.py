import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")
st.title("Magazyn z ClickUp - aktualizacja 14.03.2025 - wersja BETA")

file_path = "nazwa_pliku.csv"
separator = ','

try:
    df = pd.read_csv(file_path, sep=separator, encoding='utf-8', on_bad_lines='skip')
    st.write("Plik został wczytany poprawnie!")
    
    if "tags" not in df.columns:
        st.error("Brak kolumny 'tags' w pliku CSV. Sprawdź plik.")
    else:
        st.sidebar.header("Filtry")
        
        # Odczyt parametrów z URL (jeśli istnieją)
        query_params = st.query_params.to_dict()
        
        # Filtr dla "tags"
        unique_tags = df["tags"].unique().tolist()
        default_tag = query_params.get("tag", "Wszystkie")
        selected_tag = st.sidebar.selectbox("Wybierz tag", ["Wszystkie"] + unique_tags, index=(["Wszystkie"] + unique_tags).index(default_tag) if default_tag in ["Wszystkie"] + unique_tags else 0)
        
        # Filtr dla "Procesor (drop down)"
        unique_processors = df["Procesor (drop down)"].unique().tolist()
        default_processor = query_params.get("processor", "Wszystkie")
        selected_processor = st.sidebar.selectbox("Wybierz procesor", ["Wszystkie"] + unique_processors, index=(["Wszystkie"] + unique_processors).index(default_processor) if default_processor in ["Wszystkie"] + unique_processors else 0)
        
        # Filtr dla "Model Procesora (short text)"
        unique_processor_models = df["Model Procesora (short text)"].unique().tolist()
        default_processor_model = query_params.get("processor_model", "Wszystkie")
        selected_processor_model = st.sidebar.selectbox("Wybierz model procesora", ["Wszystkie"] + unique_processor_models, index=(["Wszystkie"] + unique_processor_models).index(default_processor_model) if default_processor_model in ["Wszystkie"] + unique_processor_models else 0)
        
        # Filtr dla "Rozdzielczość (drop down)"
        unique_resolutions = df["Rozdzielczość (drop down)"].unique().tolist()
        default_resolution = query_params.get("resolution", "Wszystkie")
        selected_resolution = st.sidebar.selectbox("Wybierz rozdzielczość", ["Wszystkie"] + unique_resolutions, index=(["Wszystkie"] + unique_resolutions).index(default_resolution) if default_resolution in ["Wszystkie"] + unique_resolutions else 0)
        
        # Filtr dla "Przeznaczenie (drop down)" z multiwyborem
        unique_destinations = df["Przeznaczenie (drop down)"].unique().tolist()
        default_destinations = query_params.get("destinations", [])
        if isinstance(default_destinations, str):  # Jeśli tylko jedna wartość, zamień na listę
            default_destinations = [default_destinations]
        selected_destinations = st.sidebar.multiselect("Wybierz przeznaczenie", unique_destinations, default=default_destinations)
        
        # Filtr dla "Lists"
        unique_lists = df["Lists"].unique().tolist()
        default_list = query_params.get("list", "Wszystkie")
        selected_list = st.sidebar.selectbox("Wybierz listę", ["Wszystkie"] + unique_lists, index=(["Wszystkie"] + unique_lists).index(default_list) if default_list in ["Wszystkie"] + unique_lists else 0)
        
        # Aktualizacja parametrów URL po wybraniu filtrów
        new_query_params = {
            "tag": selected_tag,
            "processor": selected_processor,
            "processor_model": selected_processor_model,
            "resolution": selected_resolution,
            "destinations": selected_destinations,
            "list": selected_list
        }
        st.query_params.from_dict(new_query_params)
        
        # Filtrowanie danych
        filtered_df = df.copy()
        
        if selected_tag != "Wszystkie":
            if pd.isna(selected_tag):
                filtered_df = filtered_df[filtered_df["tags"].isna()]
            else:
                filtered_df = filtered_df[filtered_df["tags"] == selected_tag]
                
        if selected_processor != "Wszystkie":
            if pd.isna(selected_processor):
                filtered_df = filtered_df[filtered_df["Procesor (drop down)"].isna()]
            else:
                filtered_df = filtered_df[filtered_df["Procesor (drop down)"] == selected_processor]
                
        if selected_processor_model != "Wszystkie":
            if pd.isna(selected_processor_model):
                filtered_df = filtered_df[filtered_df["Model Procesora (short text)"].isna()]
            else:
                filtered_df = filtered_df[filtered_df["Model Procesora (short text)"] == selected_processor_model]
                
        if selected_resolution != "Wszystkie":
            if pd.isna(selected_resolution):
                filtered_df = filtered_df[filtered_df["Rozdzielczość (drop down)"].isna()]
            else:
                filtered_df = filtered_df[filtered_df["Rozdzielczość (drop down)"] == selected_resolution]
                
        if selected_destinations:
            filtered_df = filtered_df[filtered_df["Przeznaczenie (drop down)"].isin(selected_destinations)]
            
        if selected_list != "Wszystkie":
            if pd.isna(selected_list):
                filtered_df = filtered_df[filtered_df["Lists"].isna()]
            else:
                filtered_df = filtered_df[filtered_df["Lists"] == selected_list]
        
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
        
        st.write("### Pogrupowane modele - całość")
        with st.expander("Pokaż/ukryj tabelę z tagami", expanded=False):
            tags_summary = df["tags"].value_counts().reset_index()
            tags_summary.columns = ["Tag", "Liczba egzemplarzy"]
            st.dataframe(tags_summary, height=500)

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
