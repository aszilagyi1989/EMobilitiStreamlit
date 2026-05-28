from geopy.geocoders import Nominatim
import pandas as pd
import os
from datetime import datetime

directory = os.path.dirname(os.path.abspath(__file__))
DATAS = pd.read_csv(os.path.join(directory, "CSV", "2025_KSH__Emobiliti.csv"), sep = ";", decimal = ",")
DATAS["Berendezés leszerelésének dátuma"] = pd.to_datetime(DATAS["Berendezés leszerelésének dátuma"], format = "mixed", errors = "coerce")
DATAS = DATAS[(DATAS["Berendezés leszerelésének dátuma"] > datetime.now()) | (DATAS["Berendezés leszerelésének dátuma"].isna())]
DATAS["IRSZ_VAROS"] = (DATAS["Töltőberendezés irányítószáma"].astype(str) + " " + DATAS["Töltőberendezés település megnevezése"])

geolocator = Nominatim(user_agent = "sz.adam1989@gmail.com", timeout = 10)
for index, row in DATAS.iterrows():
  # print((row["IRSZ_VAROS"] + " " + row["Töltőberendezés közterülete"]))
  location = geolocator.geocode((row["IRSZ_VAROS"] + " " + row["Töltőberendezés közterülete"]))
  if location:
    print(f"Szélesség: {location.latitude}, Hosszúság: {location.longitude}")
  else: 
    st.error(f"Nem találtam a megadott címet: {(row['IRSZ_VAROS'] + ' ' + row['Töltőberendezés közterülete'])}")
  break
  time.sleep(1.5)
# 
# if location:
#         # st.write(f"Cím: {location.address}")
#         # st.write(f"Szélesség: {location.latitude}, Hosszúság: {location.longitude}")
#         folium.Marker(location = [location.latitude, location.longitude], popup = 'Esemény: {} <br> Helyszín: {} <br> Dátum: {}'.format(result_df['Esemény'].to_numpy(), result_df['Helyszín'].to_numpy(), result_df['Dátum'].to_numpy())).add_to(marker_cluster)
#   else:
#         wrong_address = str(result_df['Cím'].to_numpy())
#         if "utca" in wrong_address:
#           wrong_address = str(wrong_address).replace("utca", "út")
#         elif "út" in wrong_address:
#           wrong_address = str(wrong_address).replace("út", "utca")
#         wrong_address = str(wrong_address).replace("Petőfi-híd budai hídfő", "")
#         wrong_address = str(wrong_address).replace("F épület", "")
#         if ";" in wrong_address:
#           wrong_address = str(wrong_address).split(";")[0]
#         if "és" in wrong_address:
#           wrong_address = str(wrong_address).split("és")[0]
#         if "(" in wrong_address:
#           wrong_address = str(wrong_address).split("(")[0]
#         location = geolocator.geocode(wrong_address)
#         if location:
#           folium.Marker(location = [location.latitude, location.longitude], popup = 'Esemény: {} <br> Helyszín: {} <br> Dátum: {}'.format(result_df['Esemény'].to_numpy(), result_df['Helyszín'].to_numpy(), result_df['Dátum'].to_numpy())).add_to(marker_cluster)
#         else:
#           st.error(f"Nem találtam a megadott címet javítva se: {wrong_address}")


