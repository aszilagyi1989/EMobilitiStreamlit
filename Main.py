import streamlit as st
import os
import pandas as pd
from datetime import datetime
from databricks import sql
import folium
from folium.plugins import FastMarkerCluster
from streamlit_folium import st_folium
from streamlit_option_menu import option_menu
import plotly.express as px
from sklearn.cluster import KMeans

@st.cache_resource
def get_databricks_connection():
  return sql.connect(
    server_hostname = st.secrets["DATABRICKS_SERVER_HOSTNAME"], 
    http_path = st.secrets["DATABRICKS_HTTP_PATH"],
    access_token = st.secrets["DATABRICKS_TOKEN"]
  )

@st.cache_data
def load_databricks_EmobilitiData(): # fetch_raw_data():
  conn = get_databricks_connection()
  cursor = conn.cursor()
  cursor.execute("select * from DQ.EMOBILITI_2025_V3")
  EMOBILITI = cursor.fetchall_arrow().to_pandas()
  
  cursor.close()
  conn.close()
  
  EMOBILITI['DQEA007'] = pd.to_numeric(EMOBILITI['DQEA007'].astype(str).str.replace(',', '.'), errors = 'coerce')
  EMOBILITI['DQEA008'] = pd.to_numeric(EMOBILITI['DQEA008'].astype(str).str.replace(',', '.'), errors = 'coerce')
  
  EMOBILITI['lat'] = pd.to_numeric(EMOBILITI['lat'].astype(str).str.replace(',', '.'), errors = 'coerce')
  EMOBILITI['long'] = pd.to_numeric(EMOBILITI['long'].astype(str).str.replace(',', '.'), errors = 'coerce')
  
  EMOBILITI['DQEA009'] = pd.to_numeric(EMOBILITI['DQEA009'], errors = 'coerce')
  EMOBILITI['DQEA013'] = pd.to_numeric(EMOBILITI['DQEA013'], errors = 'coerce')
  EMOBILITI['DQEA014'] = pd.to_numeric(EMOBILITI['DQEA014'], errors = 'coerce')
  EMOBILITI['DQEA015'] = pd.to_numeric(EMOBILITI['DQEA015'], errors = 'coerce')
  EMOBILITI['DQEA016'] = pd.to_numeric(EMOBILITI['DQEA016'], errors = 'coerce')
  EMOBILITI['DQEA017'] = pd.to_numeric(EMOBILITI['DQEA017'], errors = 'coerce')
  EMOBILITI['DQEA018'] = pd.to_numeric(EMOBILITI['DQEA018'], errors = 'coerce')
  EMOBILITI['DQEA019'] = pd.to_numeric(EMOBILITI['DQEA019'], errors = 'coerce')
  EMOBILITI['DQEA020'] = pd.to_numeric(EMOBILITI['DQEA020'], errors = 'coerce')
  EMOBILITI['DQEA021'] = pd.to_numeric(EMOBILITI['DQEA021'], errors = 'coerce')
  EMOBILITI['DQEA022'] = pd.to_numeric(EMOBILITI['DQEA022'], errors = 'coerce')
  EMOBILITI['DQEA023'] = pd.to_numeric(EMOBILITI['DQEA023'], errors = 'coerce')
  EMOBILITI['DQEA024'] = pd.to_numeric(EMOBILITI['DQEA024'], errors = 'coerce')
  EMOBILITI['DQEA025'] = pd.to_numeric(EMOBILITI['DQEA025'], errors = 'coerce')
  EMOBILITI['DQEA026'] = pd.to_numeric(EMOBILITI['DQEA026'], errors = 'coerce')
  EMOBILITI['DQEA027'] = pd.to_numeric(EMOBILITI['DQEA027'], errors = 'coerce')
  EMOBILITI['DQEA028'] = pd.to_numeric(EMOBILITI['DQEA028'], errors = 'coerce')
  EMOBILITI['DQEA029'] = pd.to_numeric(EMOBILITI['DQEA029'], errors = 'coerce')
  
  # EMOBILITI = EMOBILITI.dropna(subset = ['DQEA007', 'DQEA008', 'lat', 'long']).copy()
  
  # directory = os.path.dirname(os.path.abspath(__file__))
  # df = pd.read_csv(os.path.join(directory, "CSV", "2025_KSH__Emobiliti_v3.csv"), sep = ";", decimal = ",")
  
  return EMOBILITI # df

@st.cache_data
def load_data():
  df = load_databricks_EmobilitiData().copy() # fetch_raw_data().copy()
  df["DQEA012"] = pd.to_datetime(df["DQEA012"], format = "mixed", errors = "coerce")
  df = df[(df["DQEA012"] > datetime.now()) | (df["DQEA012"].isna())]
  df["IRSZ_VAROS"] = (df["DQEA003"].astype(str) + " " + df["DQEA005"])

  return df

@st.cache_data(ttl = 1)
def load_data2():
  df = load_databricks_EmobilitiData().copy() # fetch_raw_data().copy()
  df["DQEA012"] = pd.to_datetime(df["DQEA012"], format = "mixed", errors = "coerce")
  df["IRSZ_VAROS"] = (df["DQEA003"].astype(str) + " " + df["DQEA005"])

  return df

@st.cache_data
def load_megszunt_data():
  df = load_databricks_EmobilitiData().copy() # fetch_raw_data().copy()
  df["DQEA012"] = pd.to_datetime(df["DQEA012"], format = "mixed", errors = "coerce")
  df = df[(df["DQEA012"] < datetime.now())]
  df["IRSZ_VAROS"] = (df["DQEA003"].astype(str) + " " + df["DQEA005"])

  return df

st.set_page_config(
  layout = "wide",
  page_title = "OSAP 2607 - E-töltőállomások regiszter adatai",
  page_icon = "https://map.ksh.hu/timea/images/shortcut.ico",
  menu_items = {'Get help': 'mailto:sz.adam1989@gmail.com',
                'Report a bug': 'mailto:sz.adam1989@gmail.com',
                'About': 'Ez a webalkalmazás a 2607-es OSAP számú adatátvétel üzemben lévő E-töltőállomásait tartalmazza a 2025. adatév alapján.'}
)


selected = option_menu(
    menu_title = None, 
    options = ["Térkép", "Piaci Elemzés", "Klaszterezés", "Anomáliák", "Élettartam", "Fehér Foltok"],
    icons = ['map', 'bar-chart-line', 'diagram-3', 'exclamation-triangle', 'hourglass-split', 'circle'], 
    menu_icon = None, 
    default_index = 0, 
    orientation = 'horizontal', 
    styles = {
        "container": {
            "padding": "0!important", 
            "background-color": "#f0f2f6",
            "max-width": "100%"
        },
        "icon": {
            "color": "#ff4b4b", 
            "font-size": "20px"
        },
        "nav-link": {
            "font-size": "16px", 
            "text-align": "center", 
            "margin": "0px", 
            "padding": "10px",
            "--hover-color": "#dee2e6",
            "list-style": "none"  # Explicit eltünteti a listajeleket (nyilakat)
        },
        "nav-link-selected": {
            "background-color": "#003366", 
            "color": "white",
            "font-weight": "bold"
        },
    }
)

with st.sidebar:
  selected_year = st.selectbox(
    "Adatidőszak kiválasztása",
    options = ["Aktuális adatok", "2025.12.31", "2024.12.31", "2023.12.31", "2022.12.31", "2021.12.31", "2020.12.31", "2019.12.31", "2018.12.31", "2017.12.31", "2016.12.31", "2015.12.31", "2014.12.31", "2013.12.31", "2012.12.31", "2011.12.31", "2010.12.31"]
  )
  
  if selected_year != "Aktuális adatok":
    # Ha a felhasználó egy konkrét év végét választja ki
    RAW_DATAS = load_data2()
    
    # teszt_sorok = RAW_DATAS[RAW_DATAS["DQEA011"].astype(str).str.contains("0222", na=False)]
    # st.write("DEBUG - Talált 0222-es gépek száma a nyers adatban:", len(teszt_sorok))
    # st.dataframe(teszt_sorok) 

    RAW_DATAS["DQEA011"] = pd.to_datetime(RAW_DATAS["DQEA011"], format = "mixed", errors = "coerce")
    RAW_DATAS["DQEA012"] = pd.to_datetime(RAW_DATAS["DQEA012"], format = "mixed", errors = "coerce")
    
    # Kivágjuk az évszámot a szövegből (pl. "2025.12.31" -> 2025) és felépítjük a datetime objektumot
    year_int = int(selected_year.split(".")[0])
    hatarido = pd.Timestamp(datetime(year_int, 12, 31))
    
    # A szűrésnél MIND KÉT feltétel ugyanazt a dinamikus határidőt használja
    DATAS = RAW_DATAS[
      (RAW_DATAS["DQEA011"] <= hatarido) & 
      ((RAW_DATAS["DQEA012"] >= hatarido) | (RAW_DATAS["DQEA012"].isna()))
    ]
    
    default_value = "1007 Budapest"
    label1 = f"{year_int}. december 31-én üzemelő töltők"
    label2 = f"Térképen mutatott {year_int}-es töltők"
    
  else:
    work = st.checkbox("Az üzemelők helyett a már leszerelt töltőberendezések mutatása")
    if work:
      DATAS = load_megszunt_data()
      default_value = "1011 Budapest"
      label1 = "Összes leszerelt töltőberendezés"
      label2 = "Térképen mutatot leszerelt töltőberendezés"
    else:
      DATAS = load_data()
      default_value = "1007 Budapest"
      label1 = "Összes regisztrált üzemben lévő töltőberendezés"
      label2 = "Térképen mutatot üzemben lévő töltőberendezés"
  
  full_City = st.checkbox("Csak településnevek (irányítószám nélkül)")
  if full_City:
    Cities_All = sorted(DATAS["DQEA005"].unique().tolist())
    City = st.multiselect("Töltőberendezés település megnevezése", Cities_All, Cities_All)
    filtered_DATAS = DATAS[DATAS["DQEA005"].isin(City)]
  else:
    Cities_All = sorted(DATAS["IRSZ_VAROS"].unique().tolist())
    City = st.multiselect("Töltőberendezés település megnevezése", Cities_All, Cities_All)
    filtered_DATAS = DATAS[DATAS["IRSZ_VAROS"].isin(City)]
  
  Names_All = sorted(filtered_DATAS["DQEA002"].unique().tolist())
  Name = st.multiselect("Töltőberendezés üzemeltető neve", Names_All, Names_All)
  filtered_DATAS = filtered_DATAS[filtered_DATAS["DQEA002"].isin(Name)]
  
  Types_All = sorted(filtered_DATAS["DQEA030"].fillna("Nincs megadva").unique().tolist())
  selected_plugs = st.selectbox("Csatlakozó típusa", Types_All, index = None, placeholder = "Válassz csatlakozótípust!")
  
  if selected_plugs:
    if selected_plugs == "Nincs megadva":
      filtered_Locations = filtered_DATAS[(filtered_DATAS["DQEA030"].isna())]
    else:
      filtered_Locations = filtered_DATAS[(filtered_DATAS["DQEA030"] == selected_plugs)]
  else:
    filtered_Locations = filtered_DATAS.copy()
  
  coordinates = st.checkbox("Javított koordinátákkal")

# tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🗺️ Térkép", "📊 Piaci Elemzés (Analyst)", "🔬 Klaszterezés (Scientist)", "⚠️ Adathibák & Anomáliák", "⏳ Élettartam Elemzés", "⚪ Fehér Foltok Elemzése"])

if selected == "Térkép":
  map = folium.Map(location = [47.1625, 19.5033], zoom_start = 7, control_scale = True)
  callback_data = []
    
  for index, row in filtered_Locations.iterrows():
    message = ""
    # if selected_year == "Aktuális adatok":
      # if work:
    message += f"<br>Üzembehelyezés dátuma: {str(row['DQEA011'])[:10]}"
    message += f"<br>Leszerelés dátuma: {str(row['DQEA012'])[:10]}"
    
    if selected_plugs:
      if selected_plugs == "csak AC":
        if row['DQEA018'] != 0:
          message += f"<br>Type2 csatl.: {row['DQEA013'] / row['DQEA018']:.0f} kw és {row['DQEA018']} db"
          
        if row['DQEA019'] != 0:
          message += f"<br>Egyéb AC csatl.: {row['DQEA014'] / row['DQEA019']:.0f} kw és {row['DQEA019']} db"
      
      if selected_plugs == "csak DC":
        if row['DQEA020'] != 0:
          message += f"<br>CCS2 csatl.: {row['DQEA015'] / row['DQEA020']:.0f} kw és {row['DQEA020']} db"
              
        if row['DQEA021'] != 0:
          message += f"<br>Chademo csatl.: {row['DQEA016'] / row['DQEA021']:.0f} kw és {row['DQEA021']} db"
              
        if row['DQEA022'] != 0:
          message += f"<br>Egyéb DC csatl.: {row['DQEA017'] / row['DQEA022']:.0f} kw és {row['DQEA022']} db"
    
      if selected_plugs == "AC és DC képes":
        if row['DQEA018'] != 0:
          message += f"<br>Type2 csatl.: {row['DQEA013'] / row['DQEA018']:.0f} kw és {row['DQEA018']} db"
          
        if row['DQEA019'] != 0:
          message += f"<br>Egyéb AC csatl.: {row['DQEA014'] / row['DQEA019']:.0f} kw és {row['DQEA019']} db"
      
        if row['DQEA020'] != 0:
          message += f"<br>CCS2 csatl.: {row['DQEA015'] / row['DQEA020']:.0f} kw és {row['DQEA020']} db"
              
        if row['DQEA021'] != 0:
          message += f"<br>Chademo csatl.: {row['DQEA016'] / row['DQEA021']:.0f} kw és {row['DQEA021']} db"
              
        if row['DQEA022'] != 0:
          message += f"<br>Egyéb DC csatl.: {row['DQEA017'] / row['DQEA022']:.0f} kw és {row['DQEA022']} db"
      
    popup_text = f"Üzemeltető: {row['DQEA002']}<br>Cím: {(row['IRSZ_VAROS'] + ', ' + row['DQEA006'])} {message}"
    if coordinates:
      callback_data.append([row["lat"], row["long"], popup_text])
    else:
      callback_data.append([row["DQEA007"], row["DQEA008"], popup_text])

  callback = """
    function (row) {
        var marker = L.marker(new L.LatLng(row[0], row[1]));
        marker.bindPopup(row[2]);
        return marker;
    };
  """

  # Itt adjuk át a callback-et
  FastMarkerCluster(data = callback_data, callback = callback).add_to(map)
  
  if not filtered_Locations.empty:
    if coordinates:
      sw = filtered_Locations[['lat', 'long']].min().tolist()
      ne = filtered_Locations[['lat', 'long']].max().tolist()
    else:
      sw = filtered_Locations[['DQEA007', 'DQEA008']].min().tolist()
      ne = filtered_Locations[['DQEA007', 'DQEA008']].max().tolist()
    map.fit_bounds([sw, ne])
  
  st_folium(map, width = 'stretch', height = 600, returned_objects = [], key = "töltő_térkép")
  
  sorok_szama, oszlopok_szama = DATAS.shape
  sorok_szama2, oszlopok_szama2 = filtered_Locations.shape
  col1, col2 = st.columns(2)
  with col1:
    st.metric(label = label1, value = f"{sorok_szama} db")
  
  with col2:
    st.metric(label = label2, value = f"{sorok_szama2} db")

if selected ==  "Piaci Elemzés":
  if not filtered_Locations.empty:
    st.subheader("Top Üzemeltetők töltőállomások száma alapján")
    operator_counts = filtered_Locations["DQEA002"].value_counts().reset_index()
    operator_counts.columns = ["Üzemeltető", "Töltőberendezések száma [db]"]
    
    fig = px.bar(
        operator_counts.head(10), 
        x = "Üzemeltető", 
        y = "Töltőberendezések száma [db]",
        labels = {"Töltőberendezések száma [db]": "Töltők száma (db)"}
    )
    
    st.plotly_chart(fig, width = 'stretch') # 'content'
  
    st.subheader("Összegzett csatlakozási teljesítmények (kw)")
    total_kw = {
        "Type2 AC": filtered_Locations['DQEA013'].sum(),
        "Egyéb AC": filtered_Locations['DQEA014'].sum(),
        "CCS2 DC": filtered_Locations['DQEA015'].sum(),
        "Chademo DC": filtered_Locations['DQEA016'].sum(),
        "Egyéb DC": filtered_Locations['DQEA017'].sum()
    }
    kw_df = pd.DataFrame(list(total_kw.items()), columns=["Csatlakozó típus", "Összteljesítmény [kW]"])
    
    fig2 = px.bar(
        kw_df, 
        x = "Csatlakozó típus", 
        y = "Összteljesítmény [kW]" #,
        # labels = {"Töltőberendezések száma [db]": "Töltők száma (db)"}
    )
    
    st.plotly_chart(fig2, width = 'stretch') # 'content'
  
  else:
    st.warning("Nincs megjeleníthető adat a jelenlegi szűrési feltételek mellett.")

if selected == "Klaszterezés":
  st.header("🔬 Földrajzi Klaszterezés (K-Means ML Modell)")
  st.write("Ez a gépi tanulási modell a GPS koordináták alapján csoportosítja a szűrt töltőállomásokat optimalizált hálózati gócokba (hubokba).")
  if len(filtered_Locations) >= 3:
    # 1. Felkészítjük a koordináta adatokat a modell számára
    if coordinates:
      X = filtered_Locations[['lat', 'long']]
      lat_Name = "lat"
      long_Name = "long"
    else:
      X = filtered_Locations[['DQEA007', 'DQEA008']]
      lat_Name = "DQEA007"
      long_Name = "DQEA008"
    
    # Csúszka a klaszterek (csoportok) számának dinamikus beállításához
    num_clusters = st.slider("Klaszterek (Hálózati gócok) száma:", min_value = 2, max_value = min(10, len(filtered_Locations)), value = 3)
    
    # 2. A K-Means modell tanítása és predikciója
    kmeans = KMeans(n_clusters = num_clusters, random_state = 42, n_init = 10)
    filtered_Locations['Klaszter_ID'] = kmeans.fit_predict(X)
    
    # Kinyerjük a csoportok középpontjait (súlypontjait)
    centroids = kmeans.cluster_centers_
    
    # 3. Megjelenítés egy interaktív Plotly térképen
    fig_ml = px.scatter_map(
      filtered_Locations,
      lat = lat_Name, # "DQEA007",
      lon = long_Name, # "DQEA008",
      color = filtered_Locations['Klaszter_ID'].astype(str),
      hover_name = "DQEA002",
      hover_data = ["IRSZ_VAROS"],
      zoom = 6,
      height = 500,
      title = "Töltőberendezések csoportosítása földrajzi elhelyezkedés alapján"
    )
    
    # Ingyenes, regisztráció nélkül működő térképstílus beállítása
    fig_ml.update_layout(
      map_style = "open-street-map", # JAVÍTÁS: mapbox_style helyett map_style!
      margin = {"r":0, "t":40, "l":0, "b":0},
      legend_title = "Klaszter azonosító"
    )
    
    st.plotly_chart(fig_ml, width = 'stretch') # 'content'
    
    # Statisztika mutatása a klaszterekről
    st.subheader("Gócok statisztikái")
    for i in range(num_clusters):
      cluster_data = filtered_Locations[filtered_Locations['Klaszter_ID'] == i]
      st.write(f"**{i}. számú csoport:** {len(cluster_data)} db töltőállomást tartalmaz ezen a területen.")
        
  else:
    st.warning("A gépi tanulási modell futtatásához legalább 3 darab töltőberendezést kell kiválasztania a szűrőkkel.")
    
if selected == "Anomáliák":
  st.header("⚠️ Adathibák & Anomáliák")
  st.write("Ez a modul a teljes KSH adatbázis matematikai és logikai ellentmondásait szűri ki, függetlenül az oldalsáv szűrőitől.")

  # JAVÍTÁS: A szűretlen nyers adatbázisból indulunk ki, hogy a sidebar ne rejtse el a hibákat!
  RAW_ANOMALY_DATA = load_data2()

  if RAW_ANOMALY_DATA.empty:
    st.warning("A nyers adatbázis nem elérhető.")
  else:
    anomaly_df = RAW_ANOMALY_DATA.copy()

    # 1. Összesítjük a fizikai darabszámokat
    anomaly_df['Összes_Fizikai_Csatlakozó'] = (
        anomaly_df['DQEA018'].fillna(0) + 
        anomaly_df['DQEA019'].fillna(0) +
        anomaly_df['DQEA020'].fillna(0) + 
        anomaly_df['DQEA021'].fillna(0) + 
        anomaly_df['DQEA022'].fillna(0)
    )

    # 2. Összesítjük a részletező kategória oszlopok darabszámait (utolsó 7 oszlop együtt)
    anomaly_df['Összes_Kategória_Darabszám'] = (
        anomaly_df['DQEA023'].fillna(0) +
        anomaly_df['DQEA024'].fillna(0) +
        anomaly_df['DQEA025'].fillna(0) +
        anomaly_df['DQEA026'].fillna(0) +
        anomaly_df['DQEA027'].fillna(0) +
        anomaly_df['DQEA028'].fillna(0) +
        anomaly_df['DQEA029'].fillna(0)
    )

    # --- ANOMÁLIA SZABÁLYOK ---

    # A: Magyarbóly-típusú hiba (Van max kW, de 0 db az összes fizikai csatlakozó)
    anomaly_df['Fantom_Töltő_Hiba'] = (
        (anomaly_df['DQEA009'].fillna(0) > 0) & 
        (anomaly_df['Összes_Fizikai_Csatlakozó'] == 0)
    )

    # B: Darabszámbeli ellentmondás hiba (A fizikai típusok és a teljesítmény kategóriák összege eltér)
    anomaly_df['Kategória_Ellentmondás_Hiba'] = (
        anomaly_df['Összes_Fizikai_Csatlakozó'] != anomaly_df['Összes_Kategória_Darabszám']
    )

    # C: Főösszeg hiba (A 'Csatlakozási pontok száma összesen' nem egyezik a fizikai oszlopok összegével)
    anomaly_df['Főösszeg_Eltérés_Hiba'] = (
        anomaly_df['DQEA010'].fillna(0) != anomaly_df['Összes_Fizikai_Csatlakozó']
    )

    # Végleges szűrés kombinálása
    anomaly_df['Is_Anomaly'] = (
        anomaly_df['Fantom_Töltő_Hiba'] | 
        anomaly_df['Kategória_Ellentmondás_Hiba'] |
        anomaly_df['Főösszeg_Eltérés_Hiba']
    )
    
    anomalies = anomaly_df[anomaly_df['Is_Anomaly'] == True]
    
    st.metric("Azonosított valós adathibák száma a teljes adatbázisban", f"{len(anomalies)} db")

    if not anomalies.empty:
      st.error("⚠️ Logikai vagy matematikai ellentmondást tartalmazó állomások listája:")
      
      display_cols = [
          'DQEA002', 
          'DQEA005', 
          'DQEA006',
          'DQEA009',
          'DQEA010',
          'DQEA018',
          'DQEA019', 
          'DQEA020',
          'DQEA021',
          'DQEA022',
          'DQEA023',
          'DQEA024',
          'DQEA025', 
          'DQEA026',
          'DQEA027',
          'DQEA028',
          'DQEA029'
      ]
      
      existing_cols = [c for c in display_cols if c in anomalies.columns]
      
      szep_nevek = {
          'DQEA002': 'Üzemeltető',
          'DQEA005': 'Település',
          'DQEA006': 'Közterület',
          'DQEA009': 'Felvehető maximális teljesítmény [kW]',
          'DQEA010': 'Csatlakozási pontok száma összesen',
          'DQEA018': 'Type2 csatlakozó db',
          'DQEA019': 'Egyéb AC csatlakozó db',
          'DQEA020': 'CCS2 csatlakozó db',
          'DQEA021': 'Chademo csatlakozó db',
          'DQEA022': 'Egyéb DC csatlakozó db',
          'DQEA023': 'Slow AC db: P < 7.4 kW',
          'DQEA024': 'Medium-speed AC db: 7.4 kW ? P ? 22 kW',
          'DQEA025': 'Fast AC db: P > 22 kW',
          'DQEA026': 'Slow DC db: P < 50 kW',
          'DQEA027': 'Fast DC db: 50 kW ? P < 150 kW',
          'DQEA028': 'Level 1- Ultra fast DC db: 150 kW ? P < 350 kW',
          'DQEA029': 'Level 2- Ultra fast DC db: P ? 350 kW'
      }
      
      st.dataframe(anomalies[existing_cols], width = 'stretch', column_config = szep_nevek, hide_index = True)
      
      # Statisztikai bontás
      st.subheader("📊 Kimutatás a hibatípusokról")
      col1, col2, col3 = st.columns(3)
      with col1:
          st.metric("Fantom kW", f"{anomalies['Fantom_Töltő_Hiba'].sum()} db")
      with col2:
          st.metric("Kategória elírások", f"{anomalies['Kategória_Ellentmondás_Hiba'].sum()} db")
      with col3:
          st.metric("Főösszeg eltérések", f"{anomalies['Főösszeg_Eltérés_Hiba'].sum()} db")
    else:
      st.success("🎉 Kiváló! Az adatbázis összes adatsora matematikailag és logikailag teljesen konzisztens.")

if selected == "Élettartam":
  st.header("⏳ Leszerelési és Élettartam Elemzés (Survival Analysis)")
  st.write("Ez a modul a töltőberendezések piacon eltöltött idejét és a leszerelési kockázatokat elemzi az üzembe helyezési és leszerelési dátumok alapján a teljes, szűretlen adatbázisból.")

  # A teljes, szűretlen adatbázist kérjük le a load_data2() függvényből, hogy a leszerelteket is lássuk
  RAW_DATAS = load_data2()

  if RAW_DATAS.empty:
    st.warning("A nyers adatbázis nem elérhető.")
  else:
    survival_df = RAW_DATAS.copy()
    
    # Dátumok típuskonverziója a megadott pontos oszlopnevekkel
    survival_df["Kezdő dátum"] = pd.to_datetime(survival_df["DQEA011"], format="mixed", errors="coerce")
    survival_df["DQEA012"] = pd.to_datetime(survival_df["DQEA012"], format="mixed", errors="coerce")
    
    # Hiányzó üzembehelyezési dátumok eldobása (enélkül nem számolható élettartam)
    survival_df = survival_df.dropna(subset=["Kezdő dátum"])
    
    # Esemény (Event) meghatározása: 1 = leszerelve, 0 = még üzemel (cenzúrázott adat)
    survival_df["Még üzemel"] = (survival_df["DQEA012"] > datetime.now()) | (survival_df["DQEA012"].isna())
    survival_df["Observed_Event"] = survival_df["Még üzemel"].apply(lambda x: 0 if x else 1)
    
    # Végdátum rögzítése: ha még üzemel, a mai napig számoljuk az élettartamot
    survival_df["Vég dátum"] = survival_df["DQEA012"]
    survival_df.loc[survival_df["Még üzemel"] == True, "Vég dátum"] = datetime.now()
    
    # Élettartam kiszámítása hónapokban
    survival_df["Élettartam (hónap)"] = (survival_df["Vég dátum"] - survival_df["Kezdő dátum"]).dt.days / 30.44
    
    # Csak a pozitív, értelmes időtartamokat tartjuk meg
    survival_df = survival_df[survival_df["Élettartam (hónap)"] > 0]

    if survival_df.empty:
      st.info("Nincs elegendő historikus dátumadat az élettartam elemzéséhez.")
    else:
      st.subheader("Csoportosított élettartam összehasonlítás")
      
      # Top 5 üzemeltető kiválasztása alapértelmezettnek a pontos oszlopnévvel
      top_operators = survival_df["DQEA002"].value_counts().head(5).index.tolist()
      
      selected_op = st.multiselect(
          "Válasszon üzemeltetőket az életgörbe összehasonlításhoz (Top 5 alapértelmezett):", 
          options=survival_df["DQEA002"].unique().tolist(),
          default=top_operators
      )
      
      if not selected_op:
        st.warning("Kérjük, válasszon ki legalább egy üzemeltetőt!")
      else:
        plot_data = []
        summary_stats = []
        
        # Kaplan-Meier túlélési görbe kiszámítása manuálisan (Pandas alapon)
        for op in selected_op:
          op_df = survival_df[survival_df["DQEA002"] == op].sort_values(by="Élettartam (hónap)")
          
          if op_df.empty:
            continue
            
          total_at_risk = len(op_df)
          survival_prob = 1.0
          
          timeline = [0.0]
          probabilities = [1.0]
          
          # Időpontok szerinti aggregáció
          for t, group in op_df.groupby("Élettartam (hónap)"):
            deaths = len(group[group["Observed_Event"] == 1])
            censored = len(group[group["Observed_Event"] == 0])
            
            if total_at_risk > 0:
              survival_prob *= (1.0 - (deaths / total_at_risk))
            
            timeline.append(t)
            probabilities.append(survival_prob)
            
            total_at_risk -= (deaths + censored)
            
          # Plotly formátum felépítése
          for t, p in zip(timeline, probabilities):
            plot_data.append({
                "Idő (hónap)": t,
                "Túlélési ráta (aktív maradás %)": p * 100,
                "Üzemeltető": op
            })
            
          # Medián élettartam becslése (ahol a görbe 50% alá esik)
          median_life = "Nincs adat (>50hó)"
          for t, p in zip(timeline, probabilities):
            if p <= 0.5:
              median_life = f"{t:.1f} hónap"
              break
              
          summary_stats.append({
              "Üzemeltető": op,
              "Összes vizsgált töltő (db)": len(op_df),
              "Ebből már leszerelt (db)": len(op_df[op_df["Observed_Event"] == 1]),
              "Becsült medián élettartam": median_life
          })
          
        # Grafikon kirajzolása, ha van adat
        if plot_data:
          fig_surf = px.line(
              pd.DataFrame(plot_data), 
              x="Idő (hónap)", 
              y="Túlélési ráta (aktív maradás %)", 
              color="Üzemeltető",
              line_shape="hv", # Lépcsőzetes túlélési függvény formátum
              title="Töltőberendezések piacon maradási görbéje (Kaplan-Meier közelítés)"
          )
          st.plotly_chart(fig_surf, width = 'stretch')
          
          # Összefoglaló statisztikai táblázat
          st.subheader("📊 Élettartam statisztikák üzemeltetőnként")
          st.dataframe(pd.DataFrame(summary_stats), width = 'stretch', hide_index = True)
          
          st.info("💡 **Hogyan olvassa a grafikont?** A függőleges tengely azt mutatja, hogy az üzembe helyezést követő X. hónapban a töltők hány százaléka üzemel még. A meredeken lefelé zuhanó vonalak korai leszerelési hullámot jeleznek az adott üzemeltetőnél.")

if selected == "Fehér Foltok":
  st.header("⚪ Földrajzi Lefedettség és Fehér Foltok Elemzése")
  st.write("Ez a modul a településszintű összesített töltési kapacitásokat (kW) vizsgálja, rávilágítva a túlreprezentált körzetekre és a töltőhálózat fehér foltjaira.")

  white_DATAS = filtered_Locations.copy() # filtered_DATAS.copy() # load_data()
  # A szűrők által érintett, de már megtisztított adatokat használjuk (filtered_Locations helyett filtered_DATAS-ból érdemes dolgozni, hogy a plug_mask ne zavarjon be)
  if white_DATAS.empty:
    st.warning("Nincs megjeleníthető adat a jelenlegi szűrési feltételek mellett.")
  else:
    # 1. Településszintű aggregáció (kW és töltők száma)
    city_coverage = white_DATAS.groupby("DQEA005").agg(
        Összes_Kapacitás_kW=('DQEA009', 'sum'),
        Töltőberendezések_Száma=('DQEA010', 'count')
    ).reset_index()

    # Kiszámoljuk az egy berendezésre jutó átlagos teljesítményt is a városban
    city_coverage['Átlagos_Kapacitás_kW'] = (city_coverage['Összes_Kapacitás_kW'] / city_coverage['Töltőberendezések_Száma']).round(1)
    
    # Sorbarendezzük kapacitás szerint
    city_coverage = city_coverage.sort_values(by="Összes_Kapacitás_kW", ascending=False)

    # --- VIZUALIZÁCIÓ 1: TOP ELLÁTOTT VÁROSOK ---
    st.subheader("🚀 Legmagasabb töltési kapacitással rendelkező települések")
    
    top_n = st.slider(
        "Megjelenítendő települések száma a toplistán:", 
        min_value = 5, 
        max_value = min(45, len(city_coverage)), 
        value = 15, 
        step = 1
    )
    
    # Kiválasztjuk a top n várost (Budapestet érdemes lehet külön figyelni, mert elviheti a pálmát)
    fig_top_cities = px.bar(
        city_coverage.head(top_n),
        x="DQEA005",
        y="Összes_Kapacitás_kW",
        color="Töltőberendezések_Száma",
        labels={
            "DQEA005": "Település",
            "Összes_Kapacitás_kW": "Összteljesítmény (kW)",
            "Töltőberendezések_Száma": "Töltők száma (db)"
        },
        title = f"Top {top_n} település a hálózati összteljesítmény (kW) alapján",
        color_continuous_scale = px.colors.sequential.Viridis
    )
    st.plotly_chart(fig_top_cities, width = 'stretch')

    # --- VIZUALIZÁCIÓ 2: FEHÉR FOLTOK ---
    st.subheader("⚪ Alacsony kapacitású területek (Fehér foltok)")
    st.write("Azok a települések a kijelölt listából, ahol a teljesített hálózati kapacitás kritizálhatóan alacsony (az összteljesítmény nem éri el a 22 kW-ot, vagy alig van csatlakozó).")
    
    # Fehér foltnak minősítjük, ahol az összkapacitás nagyon kevés, de nagyobb mint 0 (a valódi 0-kat az anomáliánál szűrtük)
    white_spots = city_coverage[city_coverage["Összes_Kapacitás_kW"] <= 22].sort_values(by="Összes_Kapacitás_kW")

    if white_spots.empty:
      st.success("🎉 A jelenleg kiválasztott települések mindegyike rendelkezik legalább 22 kW feletti összteljesítménnyel!")
    else:
      col_table, col_info = st.columns([2, 1])
      
      with col_table:
        st.dataframe(
            white_spots.rename(columns={
                "DQEA005": "Település neve",
                "Összes_Kapacitás_kW": "Összkapacitás (kW)",
                "Töltőberendezések_Száma": "Regisztrált töltők (db)",
                "Átlagos_Kapacitás_kW": "Átlagos töltőméret (kW)"
            }), 
            width = 'stretch', 
            hide_index = True
        )
      
      with col_info:
        st.metric("Azonosított fehér folt település", f"{len(white_spots)} db")
        st.info("💡 **Fejlesztési javaslat:** Ezeken a településeken az elektromos autóval érkezők szinte kizárólag éjszakai vagy rendkívül lassú lakossági tempóban tudnak tölteni. Kereskedelmi szempontból ezek a helyszínek ideálisak lehetnek új DC gyorstöltők telepítésére.")

    # --- VIZUALIZÁCIÓ 3: TELJESÍTMÉNY ELOSZLÁS (Bubble chart) ---
    st.subheader("🎯 Települések infrastrukturális összehasonlítása")
    
    fig_bubble = px.scatter(
        city_coverage,
        x = "Töltőberendezések_Száma",
        y = "Összes_Kapacitás_kW",
        size = "Átlagos_Kapacitás_kW",
        hover_name = "DQEA005",
        labels = {
            "Töltőberendezések_Száma": "Töltőberendezések száma (db)",
            "Összes_Kapacitás_kW": "Összesített kapacitás (kW)"
        },
        title = "Települések elhelyezkedése a darabszám és összteljesítmény mátrixában (A buborék mérete az átlagos kW méretét jelzi)",
    )
    st.plotly_chart(fig_bubble, width = 'stretch')
