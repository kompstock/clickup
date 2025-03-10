import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")
st.title("Magazyn z ClickUp - aktualizacja 10.03.2025 - wersja BETA")

file_path = "nazwa_pliku.csv"
separator = ','

try:
    df = pd.read_csv(file_path, sep=separator, encoding='utf-8', on_bad_lines='skip')
    st.write("Plik został wczytany poprawnie!")
    
    if "tags" not in df.columns:
        st.error("Brak kolumny 'tags' w pliku CSV. Sprawdź plik.")
    else:
        st.sidebar.header("Filtry")
        
        unique_tags = df["tags"].unique().tolist()
        selected_tag = st.sidebar.selectbox("Wybierz tag", ["Wszystkie"] + unique_tags)
        
        unique_processors = df["Procesor (drop down)"].unique().tolist()
        selected_processor = st.sidebar.selectbox("Wybierz procesor", ["Wszystkie"] + unique_processors)
        
        unique_processor_models = df["Model Procesora (short text)"].unique().tolist()
        selected_processor_model = st.sidebar.selectbox("Wybierz model procesora", ["Wszystkie"] + unique_processor_models)
        
        unique_resolutions = df["Rozdzielczość (drop down)"].unique().tolist()
        selected_resolution = st.sidebar.selectbox("Wybierz rozdzielczość", ["Wszystkie"] + unique_resolutions)
        
        unique_destinations = df["Przeznaczenie (drop down)"].unique().tolist()
        selected_destinations = st.sidebar.multiselect("Wybierz przeznaczenie", unique_destinations)
        
        unique_lists = df["Lists"].unique().tolist()
        selected_list = st.sidebar.selectbox("Wybierz listę", ["Wszystkie"] + unique_lists)
        
        filtered_df = df.copy()
        
        # Filtrowanie po "tags"
        if selected_tag != "Wszystkie":
            if pd.isna(selected_tag):
                filtered_df = filtered_df[filtered_df["tags"].isna()]
            else:
                filtered_df = filtered_df[filtered_df["tags"] == selected_tag]
                
        # Filtrowanie po "Procesor (drop down)"
        if selected_processor != "Wszystkie":
            if pd.isna(selected_processor):
                filtered_df = filtered_df[filtered_df["Procesor (drop down)"].isna()]
            else:
                filtered_df = filtered_df[filtered_df["Procesor (drop down)"] == selected_processor]
                
        # Filtrowanie po "Model Procesora (short text)"
        if selected_processor_model != "Wszystkie":
            if pd.isna(selected_processor_model):
                filtered_df = filtered_df[filtered_df["Model Procesora (short text)"].isna()]
            else:
                filtered_df = filtered_df[filtered_df["Model Procesora (short text)"] == selected_processor_model]
                
        # Filtrowanie po "Rozdzielczość (drop down)"
        if selected_resolution != "Wszystkie":
            if pd.isna(selected_resolution):
                filtered_df = filtered_df[filtered_df["Rozdzielczość (drop down)"].isna()]
            else:
                filtered_df = filtered_df[filtered_df["Rozdzielczość (drop down)"] == selected_resolution]
                
        # Filtrowanie po "Przeznaczenie (drop down)" z multiwyborem
        if selected_destinations:
            filtered_df = filtered_df[filtered_df["Przeznaczenie (drop down)"].isin(selected_destinations)]
            
        # Filtrowanie po "Lists"
        if selected_list != "Wszystkie":
            if pd.isna(selected_list):
                filtered_df = filtered_df[filtered_df["Lists"].isna()]
            else:
                filtered_df = filtered_df[filtered_df["Lists"] == selected_list]
        
        st.write("### Przefiltrowane dane")
        st.dataframe(filtered_df, height=500)
        st.write(f"Liczba pokazywanych pozycji: {len(filtered_df)}")
        
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
