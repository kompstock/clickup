import pandas as pd
import streamlit as st

# Włączenie szerokiego trybu
st.set_page_config(layout="wide")

# Tytuł aplikacji
st.title("Magazyn z ClickUp - aktualizacja 10.03.2025 - wersja BETA")

# Ścieżka do pliku CSV w folderze z kodem
file_path = "nazwa_pliku.csv"  # Zmień na rzeczywistą nazwę swojego pliku

# Wybór separatora
separator = st.selectbox("Wybierz separator", [',', ';', '\t', ' '])

try:
    # Wczytanie pliku CSV z wybranym separatorem
    df = pd.read_csv(file_path, sep=separator, encoding='utf-8', on_bad_lines='skip')
    st.write("Plik został wczytany poprawnie!")
    
    # Sprawdzenie, czy kolumna "tags" istnieje
    if "tags" not in df.columns:
        st.error("Brak kolumny 'tags' w pliku CSV. Sprawdź plik.")
    else:
        # Filtry po lewej stronie
        st.sidebar.header("Filtry")
        
        # Filtr dla "tags"
        unique_tags = df["tags"].unique().tolist()
        selected_tag = st.sidebar.selectbox("Wybierz tag", ["Wszystkie"] + unique_tags)
        
        # Filtr dla "Procesor (drop down)"
        unique_processors = df["Procesor (drop down)"].unique().tolist()
        selected_processor = st.sidebar.selectbox("Wybierz procesor", ["Wszystkie"] + unique_processors)
        
        # Filtr dla "Model Procesora (short text)"
        unique_processor_models = df["Model Procesora (short text)"].unique().tolist()
        selected_processor_model = st.sidebar.selectbox("Wybierz model procesora", ["Wszystkie"] + unique_processor_models)
        
        # Filtr dla "Rozdzielczość (drop down)"
        unique_resolutions = df["Rozdzielczość (drop down)"].unique().tolist()
        selected_resolution = st.sidebar.selectbox("Wybierz rozdzielczość", ["Wszystkie"] + unique_resolutions)
        
        # Filtr dla "Przeznaczenie (drop down)" z multiwyborem
        unique_destinations = df["Przeznaczenie (drop down)"].unique().tolist()
        selected_destinations = st.sidebar.multiselect("Wybierz przeznaczenie", unique_destinations)
        
        # Filtr dla "Lists"
        unique_lists = df["Lists"].unique().tolist()
        selected_list = st.sidebar.selectbox("Wybierz listę", ["Wszystkie"] + unique_lists)
        
        # Filtrowanie danych
        filtered_df = df.copy()
        
        # Filtrowanie po "tags"
        if selected_tag != "Wszystkie":
            filtered_df = filtered_df[filtered_df["tags"] == selected_tag]
            
        # Filtrowanie po "Procesor (drop down)"
        if selected_processor != "Wszystkie":
            filtered_df = filtered_df[filtered_df["Procesor (drop down)"] == selected_processor]
            
        # Filtrowanie po "Model Procesora (short text)"
        if selected_processor_model != "Wszystkie":
            filtered_df = filtered_df[filtered_df["Model Procesora (short text)"] == selected_processor_model]
            
        # Filtrowanie po "Rozdzielczość (drop down)"
        if selected_resolution != "Wszystkie":
            filtered_df = filtered_df[filtered_df["Rozdzielczość (drop down)"] == selected_resolution]
            
        # Filtrowanie po "Przeznaczenie (drop down)" z multiwyborem
        if selected_destinations:  # Jeśli wybrano jakiekolwiek wartości
            filtered_df = filtered_df[filtered_df["Przeznaczenie (drop down)"].isin(selected_destinations)]
            
        # Filtrowanie po "Lists"
        if selected_list != "Wszystkie":
            filtered_df = filtered_df[filtered_df["Lists"] == selected_list]
        
        # Wyświetlanie przefiltrowanych danych
        st.write("### Przefiltrowane dane")
        st.dataframe(filtered_df, height=500)  # Tabela o wysokości 500 pikseli
        
        # Wyświetlanie liczby pokazywanych pozycji
        st.write(f"Liczba pokazywanych pozycji: {len(filtered_df)}")
        
        # Przygotowanie pliku Excel do pobrania
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
        
        # Dodatkowa tabela z tagami - domyślnie ukryta
        st.write("### Pogrupowane modele - całość")
        with st.expander("Pokaż/ukryj tabelę z tagami", expanded=False):
            # Grupowanie tagów i liczenie wystąpień
            tags_summary = df["tags"].value_counts().reset_index()
            tags_summary.columns = ["Tag", "Liczba egzemplarzy"]
            # Wyświetlanie tabeli z wysokością wystarczającą na 100 pozycji
            st.dataframe(tags_summary, height=500)  # Wysokość 2000 pikseli dla ~100 wierszy

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
