from ydata_profiling import ProfileReport
from data.loader import load_data

df = load_data()

profile = ProfileReport(df)
profile.to_file("report.html")
