import functools
from pathlib import Path

import streamlit as st
from st_aggrid import AgGrid
from st_aggrid.shared import JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder
import numpy as np
import pandas as pd
import plotly.express as px
from util import fmt_float


chart = functools.partial(st.plotly_chart, use_container_width=True)
COMMON_ARGS = {
    "color": "symbol",
    "hover_data": [
        "account_name",
        "percent_of_account",
        "quantity",
        "total_gain_loss_dollar",
        "total_gain_loss_percent",
    ],
}


@st.cache_data
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Take Raw Fidelity Dataframe and return usable dataframe.
    - snake_case headers
    - Filter out unrelevant rows:
      - symbol is na
      - symbol is 50162D100 #LLEN
      - symbol is BRT2DP6D1 #MICROSOFT 401K PLAN - BTC SHRT-TERM INV
      - symbol is Pending Activity #LLEN
    - In numbers columns
      - Replace '--' with np.nan
      - Clean $ and % signs from values and convert to floats
    - In Cash accolunts
      - Fill in missing value of number coulmns
    - In BrokerageLink accounts
      - Rename account_number to MSFT or ORCL based on a mapping
      - Append account_number to account_name
    - Remove Symbol if the cost<=1

    Args:
        df (pd.DataFrame): Raw fidelity csv data

    Returns:
        pd.DataFrame: cleaned dataframe with features above
    """
    df = df.copy()
    df.columns = df.columns.str.lower().str.replace(" ", "_", regex=False).str.replace("/", "_", regex=False)


    df = df[
        ~( df['symbol'].isnull() | df['symbol'].isin(['50162D100', 'BRT2DP6D1', 'Pending Activity']) )
    ]


    df.type = df.type.fillna("unknown")


    price_index = df.columns.get_loc("last_price")
    cost_basis_index = df.columns.get_loc("average_cost_basis")
    df[df.columns[price_index : cost_basis_index + 1]] = df[
        df.columns[price_index : cost_basis_index + 1]
    ].replace('--', np.nan).transform(
        lambda s: 
        s.str.replace("$", "", regex=False).str.replace("%", "", regex=False).astype(float)
    )


    cash_symbol_fillin = {
            'last_price': 1.0,
            'average_cost_basis': 1.0,
            'last_price_change': 0,
            "total_gain_loss_dollar": 0,
            "total_gain_loss_percent": 0,
            "today's_gain_loss_dollar": 0,
            "today's_gain_loss_percent": 0,
    }
    for cash_symbol in ['SPAXX**', 'CORE**', 'FZDXX']:
        df.loc[df.query(f'symbol=="{cash_symbol}"').index, [ 
            c for c in cash_symbol_fillin.keys() 
        ]] = [
            v for v in cash_symbol_fillin.values() 
        ]

        df.loc[df.query(f'symbol=="{cash_symbol}"').index, 'quantity'] = df['current_value'] / 1.0
        df.loc[df.query(f'symbol=="{cash_symbol}"').index, 'cost_basis_total'] = df['current_value']

    bl_mapping = {'652837700':'MSFT','652837696':'ORCL'}
    for bl_number,bl_name in bl_mapping.items():
        df.loc[df.query(f'account_number=="{bl_number}"').index, 'account_number'] = bl_name

    for bl_account in ['BrokerageLink']:
        df.loc[df.query(f'account_name=="{bl_account}"').index, 'account_name'] = df['account_name']+' - '+df['account_number']


    df = df[ df['cost_basis_total'] > 1 ]


    quantity_index = df.columns.get_loc("quantity")
    most_relevant_columns = df.columns[quantity_index : cost_basis_index + 1]
    first_columns = df.columns[0:quantity_index]
    last_columns = df.columns[cost_basis_index + 1 :]
    df = df[[*most_relevant_columns, *first_columns, *last_columns]]

    return df


@st.cache_data
def filter_data(
    df: pd.DataFrame, account_selections: list[str], symbol_selections: list[str]
) -> pd.DataFrame:
    """
    Returns Dataframe with only accounts and symbols selected

    Args:
        df (pd.DataFrame): clean fidelity csv data, including account_name and symbol columns
        account_selections (list[str]): list of account names to include
        symbol_selections (list[str]): list of symbols to include

    Returns:
        pd.DataFrame: data only for the given accounts and symbols
    """
    df = df.copy()
    df = df[
        df.account_name.isin(account_selections) & df.symbol.isin(symbol_selections)
    ]

    return df


def main() -> None:
    st.header("Fidelity Account Overview :moneybag: :dollar: :bar_chart:")

    with st.expander("How to Use This"):
        st.write(Path("README.md").read_text())

    st.subheader("Upload your CSV from Fidelity")
    uploaded_data = st.file_uploader(
        "Drag and Drop or Click to Upload", type=".csv", accept_multiple_files=False
    )

    if uploaded_data is None:
        st.info("Using example data. Upload a file above to use your own data!")
        uploaded_data = open("data/current", "r")
    else:
        st.success("Uploaded your file!")

    df = pd.read_csv(uploaded_data)
    with st.expander("Raw Dataframe"):
        st.write(df)

    df = clean_data(df)
    with st.expander("Cleaned Data"):
        st.write(df)

    st.sidebar.subheader("Filter Displayed Accounts")

    accounts = list(df.account_name.unique())
    account_selections = st.sidebar.multiselect(
        "Select Accounts to View", options=accounts, default=accounts
    )
    st.sidebar.subheader("Filter Displayed Tickers")

    symbols = list(df.loc[df.account_name.isin(account_selections), "symbol"].unique())
    symbol_selections = st.sidebar.multiselect(
        "Select Ticker Symbols to View", options=symbols, default=symbols
    )

    df = filter_data(df, account_selections, symbol_selections)
    st.subheader("Selected Account and Ticker Data")
    cellsytle_jscode = JsCode(
        """
    function(params) {
        if (params.value > 0) {
            return {
                'color': 'white',
                'backgroundColor': 'forestgreen'
            }
        } else if (params.value < 0) {
            return {
                'color': 'white',
                'backgroundColor': 'crimson'
            }
        } else {
            return {
                'color': 'white',
                'backgroundColor': 'slategray'
            }
        }
    };
    """
    )

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_columns(
        (
            "last_price_change",
            "total_gain_loss_dollar",
            "total_gain_loss_percent",
            "today's_gain_loss_dollar",
            "today's_gain_loss_percent",
        ),
        cellStyle=cellsytle_jscode,
    )
    gb.configure_pagination(enabled=False)
    gb.configure_columns(("account_name", "symbol"), pinned=True)
    gridOptions = gb.build()

    AgGrid(df, gridOptions=gridOptions, allow_unsafe_jscode=True)

    def draw_bar(y_val: str, **kwargs) -> None:
        if not kwargs:
            kwargs = COMMON_ARGS
        else:
            kwargs = {**COMMON_ARGS, **kwargs}
        fig = px.bar(df, y=y_val, x="symbol", **kwargs)
        fig.update_layout(barmode="stack", xaxis={"categoryorder": "total descending"})
        chart(fig)

    account_plural = "s" if len(account_selections) > 1 else ""
    st.subheader(f"Value of Account{account_plural}")
    totals = df.groupby("account_name", as_index=False).sum()
    if len(account_selections) > 1:
        st.metric(
            "Total of All Accounts",
            f"${fmt_float(totals.current_value.sum())}",
            f"{fmt_float(totals.total_gain_loss_dollar.sum())}",
        )
    for column, row in zip(st.columns(len(totals)), totals.itertuples()):
        column.metric(
            row.account_name,
            f"${fmt_float(row.current_value)}",
            f"{fmt_float(row.total_gain_loss_dollar)}",
        )

    fig = px.bar(
        totals,
        y="account_name",
        x="current_value",
        color="account_name",
        text=[f"{fmt_float(v)}<br>{v/totals.current_value.sum()*100:.1f}%" for v in totals['current_value']],
    )
    fig.update_layout(barmode="stack", xaxis={"categoryorder": "total descending"})
    chart(fig)

    glfn = lambda v: 'gain' if v>=0 else 'loss'

    st.subheader("Value of each Symbol")
    draw_bar(
        y_val="current_value", 
        color="account_name", 
        text=[f"{v1}<br>{fmt_float(v2)}<br>{v3}% ({glfn(v3)})" for v1,v2,v3 in zip(df['account_name'], df['current_value'], df['total_gain_loss_percent'])],
    )

    def draw_sunburst(ldf,**kwargs) -> None:
        if not kwargs:
            kwargs = COMMON_ARGS
        else:
            kwargs = {**COMMON_ARGS, **kwargs}
        fig = px.sunburst(ldf, **kwargs)
        return fig

    st.subheader("Value of each Symbol per Account")
    fig = draw_sunburst(df, path=["account_name", "symbol"], values="current_value")
    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
    chart(fig)

    st.subheader("Value of each Symbol")
    fig = px.pie(
        df, 
        values="current_value", 
        names="symbol", 
        color='symbol', 
    )
    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
    fig.update_traces(textposition='inside', textinfo='percent+label')
    chart(fig)

    st.subheader("Total Value gained each Symbol")
    draw_bar(
        y_val="total_gain_loss_dollar",
        color="account_name", 
        text=[f"{v1}<br>{fmt_float(v2)} ({glfn(v2)})" for v1,v2 in zip(df['account_name'], df['total_gain_loss_dollar'])],
    )
 
    st.subheader("Total Percent Value gained each Symbol")
    draw_bar(
        y_val="total_gain_loss_percent",
        color="account_name", 
        text=[f"{v1}<br>{v2}% ({glfn(v2)})" for v1,v2 in zip(df['account_name'], df['total_gain_loss_percent'])],
    )


if __name__ == "__main__":
    st.set_page_config(
        "Fidelity Account View by Gerard Bentley",
        "📊",
        initial_sidebar_state="collapsed",
        layout="wide",
    )
    main()
