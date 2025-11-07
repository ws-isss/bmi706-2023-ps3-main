import altair as alt
import pandas as pd
import streamlit as st

### P1.2 ###

@st.cache
def load_data():
    cancer_df = pd.read_csv("https://raw.githubusercontent.com/hms-dbmi/bmi706-2022/main/cancer_data/cancer_ICD10.csv").melt(  # type: ignore
        id_vars=["Country", "Year", "Cancer", "Sex"],
        var_name="Age",
        value_name="Deaths",
    )
    pop_df = pd.read_csv("https://raw.githubusercontent.com/hms-dbmi/bmi706-2022/main/cancer_data/population.csv").melt(  # type: ignore
        id_vars=["Country", "Year", "Sex"],
        var_name="Age",
        value_name="Pop",
    )

    df = pd.merge(left=cancer_df, right=pop_df, how="left")
    df["Pop"] = df.groupby(["Country", "Sex", "Age"])["Pop"].fillna(method="bfill")
    df.dropna(inplace=True)

    df = df.groupby(["Country", "Year", "Cancer", "Age", "Sex"]).sum().reset_index()
    df["Rate"] = df["Deaths"] / df["Pop"] * 100_000
    return df

df = load_data()

### P1.2 ###


st.write("## Age-specific cancer mortality rates")

### P2.1 ###
# replace with st.slider
year = st.slider(
    "Select Year",
    int(df["Year"].min()),
    int(df["Year"].max()),
    int(df["Year"].min())
)
subset = df[df["Year"] == year]
### P2.1 ###


### P2.2 ###
# replace with st.radio
sex = st.radio(
    "Sex",
    options=["M", "F"],
    index=0
)
subset = subset[subset["Sex"] == sex]
### P2.2 ###


### P2.3 ###
# replace with st.multiselect
# (hint: can use current hard-coded values below as as `default` for selector)
countries_default = [
    "Austria",
    "Germany",
    "Iceland",
    "Spain",
    "Sweden",
    "Thailand",
    "Turkey",
]
countries = st.multiselect(
    "Countries",
    options=sorted(df["Country"].unique().tolist()),
    default=countries_default,
)
subset = subset[subset["Country"].isin(countries)]
### P2.3 ###


### P2.4 ###
# replace with st.selectbox
cancer = st.selectbox(
    "Cancer",
    options=sorted(df["Cancer"].unique().tolist()),
    index=sorted(df["Cancer"].unique().tolist()).index("Malignant neoplasm of stomach")
)
subset = subset[subset["Cancer"] == cancer]
### P2.4 ###


### P2.5 ###
ages = [
    "Age <5",
    "Age 5-14",
    "Age 15-24",
    "Age 25-34",
    "Age 35-44",
    "Age 45-54",
    "Age 55-64",
    "Age >64",
]

chart = (
    alt.Chart(subset)
    .mark_rect()
    .encode(
        x=alt.X("Age", sort=ages, title="Age"),
        y=alt.Y("Country", title="Country"),
        color=alt.Color(
            "Rate",
            title="Mortality rate per 100k",
            scale=alt.Scale(type="log", domain=[0.01, 1000], clamp=True, scheme="blues", reverse=True),
        ),
        tooltip=[alt.Tooltip("Rate:Q", title="Rate")]
    )
    .properties(
        title=f"{cancer} mortality rates for {'males' if sex == 'M' else 'females'} in {year}"
    )
)
### P2.5 ###

age_sel = alt.selection_point(fields=["Age"], empty="all")

countries_in_subset = subset["Country"].unique()
if len(countries_in_subset) != len(countries):
    if len(countries_in_subset) == 0:
        st.write("No data avaiable for given subset.")
    else:
        missing = set(countries) - set(countries_in_subset)
        st.write("No data available for " + ", ".join(missing) + ".")

### BONUS ###
bar = (
    alt.Chart(subset)
    .transform_filter(age_sel)
    .mark_bar()
    .encode(
        y=alt.Y("Country:N", sort="-x", title="Country"),
        x=alt.X("sum(Pop):Q", title="Sum of population size"),
        tooltip=[
            alt.Tooltip("sum(Pop):Q", title="Sum of population size", format=",d"),
            alt.Tooltip("Country:N",   title="Country"),
        ],
    )
)

final_chart = chart.add_params(age_sel) & bar

st.altair_chart(final_chart, use_container_width=True)
