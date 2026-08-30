# TradeFlow Money Manager v2

Streamlit trading money-management dashboard with dynamic percentage sizing and 1/2/3/4/5/10-step compounding.

## Logic
- Base stake = current capital × selected risk %.
- After a WIN, the next stake = previous stake + previous profit.
- This continues until the selected compounding step count is reached.
- Completing the selected number of wins starts a new cycle using the then-current capital's base percentage.
- Any LOSS immediately resets the compounding cycle and the next stake uses the updated capital × risk %.

## Run
pip install -r requirements.txt
streamlit run app.py
