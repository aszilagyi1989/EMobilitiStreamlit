import streamlit as st
import pandas as pd
from datetime import datetime
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

DATAS = pd.read_csv("https://github.com/aszilagyi1989/EMobilitiStreamlit/raw/refs/heads/main/CSV/2025_KSH__Emobiliti.csv", sep = ";", decimal = ",")
DATAS["Berendezés leszerelésének dátuma"] = pd.to_datetime(DATAS["Berendezés leszerelésének dátuma"], format = "mixed", errors = "coerce")
DATAS = DATAS[(DATAS["Berendezés leszerelésének dátuma"] > datetime.now()) | (DATAS["Berendezés leszerelésének dátuma"].isna())]
DATAS["IRSZ_VAROS"] = (DATAS["Töltőberendezés irányítószáma"].astype(str) + " " + DATAS["Töltőberendezés település megnevezése"])

st.set_page_config(
  layout = "wide",
  page_title = "OSAP 2607 - E-töltőállomások regiszter adatai",
  page_icon = "https://map.ksh.hu/timea/images/shortcut.ico",
  menu_items = {'Get help': 'mailto:sz.adam1989@gmail.com',
                'Report a bug': 'mailto:sz.adam1989@gmail.com',
                'About': 'Ez a webalkalmazás a 2607-es OSAP számú adatátvétel üzemben lévő E-töltőállomásait tartalmazza a 2025. adatév alapján.'}
)

with st.sidebar:
  Cities_All = sorted(DATAS["IRSZ_VAROS"].unique().tolist())
  select_All_Cities = st.checkbox("Összes település kiválasztása", value = False)
  if select_All_Cities:
    City = st.multiselect("Töltőberendezés település megnevezése", Cities_All, default = Cities_All, disabled = True)
    filtered_DATAS = DATAS.copy()
  else:
    City = st.multiselect("Töltőberendezés település megnevezése", Cities_All, "1007 Budapest")
    filtered_DATAS = DATAS[DATAS["IRSZ_VAROS"].isin(City)]
  
  Names_All = sorted(filtered_DATAS["Töltőberendezés üzemeltető neve"].unique().tolist())
  Name = st.multiselect("Töltőberendezés üzemeltető neve", Names_All)
  if Name:
    filtered_DATAS = filtered_DATAS[filtered_DATAS["Töltőberendezés üzemeltető neve"].isin(Name)]
  
  selected_plugs = st.pills("Csatlakozó típusa", options = ["Type2", "Egyéb AC", "CCS2", "Chademo", "Egyéb DC"], default = ["Type2", "Egyéb AC", "CCS2", "Chademo", "Egyéb DC"], selection_mode = "multi")
  
  plug_mask = pd.Series(False, index = filtered_DATAS.index)

  if selected_plugs:
    if "Type2" in selected_plugs:
        plug_mask = plug_mask | (filtered_DATAS["Type2 csatlakozó teljesítménye [kW, per darab]"] > 0)
    
    if "Egyéb AC" in selected_plugs:
        plug_mask = plug_mask | (filtered_DATAS["Egyéb AC csatlakozó teljesítménye [kW, per darab]"] > 0)
    
    if "CCS2" in selected_plugs:
        plug_mask = plug_mask | (filtered_DATAS["CCS2 csatlakozó teljesítménye [kW, per darab]"] > 0)
        
    if "Chademo" in selected_plugs:
        plug_mask = plug_mask | (filtered_DATAS["Chademo csatlakozó teljesítménye [kW, per darab]"] > 0)
        
    if "Egyéb DC" in selected_plugs:
        plug_mask = plug_mask | (filtered_DATAS["Egyéb DC csatlakozó teljesítménye [kW, per darab]"] > 0)

    filtered_Locations = filtered_DATAS[plug_mask]
  else:
    filtered_Locations = pd.DataFrame(columns = filtered_DATAS.columns)
  
  
map = folium.Map(location = [47.1625, 19.5033], zoom_start = 7)
marker_cluster = MarkerCluster().add_to(map)
  
for index, row in filtered_Locations.iterrows():
  message = ""
  if selected_plugs:
    if "Type2" in selected_plugs and row['Type2 csatlakozó darabszáma [db]'] != 0:
      message += f"<br>Type2 teljesítmény, darabszám: {row['Type2 csatlakozó teljesítménye [kW, per darab]'] / row['Type2 csatlakozó darabszáma [db]']:.0f} kw, {row['Type2 csatlakozó darabszáma [db]']} db"
    
    if "Egyéb AC" in selected_plugs and row['Egyéb AC csatlakozó darabszáma [db]'] != 0:
      message += f"<br>Egyéb AC teljesítmény, darabszám: {row['Egyéb AC csatlakozó teljesítménye [kW, per darab]'] / row['Egyéb AC csatlakozó darabszáma [db]']:.0f} kw, {row['Egyéb AC csatlakozó darabszáma [db]']} db"
    
    if "CCS2" in selected_plugs and row['CCS2 csatlakozó darabszáma [db]'] != 0:
      message += f"<br>CCS2 teljesítmény, darabszám: {row['CCS2 csatlakozó teljesítménye [kW, per darab]'] / row['CCS2 csatlakozó darabszáma [db]']:.0f} kw, {row['CCS2 csatlakozó darabszáma [db]']} db"
        
    if "Chademo" in selected_plugs and row['Chademo csatlakozó darabszáma [db]'] != 0:
      message += f"<br>Chademo teljesítmény, darabszám: {row['Chademo csatlakozó teljesítménye [kW, per darab]'] / row['Chademo csatlakozó darabszáma [db]']:.0f} kw, {row['Chademo csatlakozó darabszáma [db]']} db"
        
    if "Egyéb DC" in selected_plugs and row['Egyéb DC csatlakozó darabszáma [db]'] != 0:
      message += f"<br>Egyéb DC teljesítmény és darabszám: {row['Egyéb DC csatlakozó teljesítménye [kW, per darab]'] / row['Egyéb DC csatlakozó darabszáma [db]']:.0f} kw, és {row['Egyéb DC csatlakozó darabszáma [db]']} db"
    
  folium.Marker(
    location = [row["Töltőberendezés GPSKoordiN"], row["Töltőberendezés GPSKoordiE"]],
    popup = f"Üzemeltető: {row['Töltőberendezés üzemeltető neve']}<br>Cím: {(row['IRSZ_VAROS'] + ", " + row['Töltőberendezés közterülete'])} {message}"
  ).add_to(marker_cluster)


st_folium(map, use_container_width = True, height = 600)

sorok_szama, oszlopok_szama = DATAS.shape
sorok_szama2, oszlopok_szama2 = filtered_Locations.shape
col1, col2 = st.columns(2)
with col1:
  st.metric(label = "Összes regisztrált üzemben lévő töltőberendezés", value = f"{sorok_szama} db")

with col2:
  st.metric(label = "Térképen mutatot üzemben lévő töltőberendezés", value = f"{sorok_szama2} db")
