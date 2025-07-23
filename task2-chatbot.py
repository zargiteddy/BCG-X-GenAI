import pandas as pd
import re

# Load data
df = pd.read_csv('financial_summary.csv')

df['Fiscal Year'] = df['Fiscal Year'].astype(int)
companies = df['Company'].unique().tolist()

def extract_year(query):
    match = re.search(r'\b(20\d{2})\b', query)
    return int(match.group(1)) if match else None

def simple_chatbot(user_query):
    user_query = user_query.lower()
    year_requested = extract_year(user_query)

    # Extract company name
    company_found = None
    for company in companies:
        if company.lower() in user_query:
            company_found = company
            break

    if not company_found:
        return "Please specify a valid company from: " + ", ".join(companies)

    company_data = df[df['Company'] == company_found]

    # Filter by year if specified
    if year_requested:
        year_data = company_data[company_data['Fiscal Year'] == year_requested]
        if year_data.empty:
            return f"No data available for {company_found} in {year_requested}."
        data = year_data.iloc[0]
    else:
        data = company_data.sort_values('Fiscal Year', ascending=False).iloc[0]
        year_requested = int(data['Fiscal Year'])

    # Total revenue
    if "total revenue" in user_query:
        revenue = data['Total Revenue']
        return f"{company_found}'s total revenue in {year_requested} was ${revenue:,.0f}B."

    # Net income change
    elif "net income change" in user_query or "net income changed" in user_query:
        sorted_data = company_data.sort_values("Fiscal Year", ascending=False)
        if len(sorted_data) < 2:
            return f"Not enough data to determine {company_found}'s net income change."
        latest = sorted_data.iloc[0]
        prev = sorted_data.iloc[1]
        diff = latest['Net Income'] - prev['Net Income']
        perc_change = (diff / abs(prev['Net Income'])) * 100 if prev['Net Income'] != 0 else 0
        direction = "increased" if diff > 0 else "decreased"
        return (f"{company_found}'s net income {direction} by ${abs(diff):,.0f}B "
                f"({abs(perc_change):.2f}%) from {int(prev['Fiscal Year'])} to {int(latest['Fiscal Year'])}.")

    # Revenue growth
    elif "revenue growth" in user_query:
        if 'Revenue Growth (%)' not in data or pd.isna(data['Revenue Growth (%)']):
            return f"Revenue growth data is not available for {company_found} in {year_requested}."
        return f"{company_found}'s revenue growth in {year_requested} was {data['Revenue Growth (%)']:.2f}%."

    # Asset growth
    elif "asset growth" in user_query or "assets growth" in user_query:
        if 'Assets Growth (%)' not in company_data.columns:
            return "Asset growth data not available."
        avg_growth = company_data['Assets Growth (%)'].mean()
        return f"{company_found} has an average asset growth of {avg_growth:.2f}% over the available years."

    # Net income trend
    elif "net income trend" in user_query or ("net income" in user_query and "change" not in user_query):
        company_data_sorted = company_data.sort_values("Fiscal Year")
        if len(company_data_sorted) < 2:
            return f"Not enough data to analyze {company_found}'s net income trend."

        trends = []
        for i in range(len(company_data_sorted) - 1):
            y1 = int(company_data_sorted.iloc[i]['Fiscal Year'])
            y2 = int(company_data_sorted.iloc[i+1]['Fiscal Year'])
            n1 = company_data_sorted.iloc[i]['Net Income']
            n2 = company_data_sorted.iloc[i+1]['Net Income']
            direction = "increased" if n2 > n1 else "decreased" if n2 < n1 else "stayed the same"
            trends.append(f"{direction} from ${n1:,.0f}B in {y1} to ${n2:,.0f}B in {y2}")
        return f"{company_found}'s net income trend:\n- " + "\n- ".join(trends)

    else:
        return "Sorry, I can only answer financial queries like revenue, net income, growth, or trends."

# Interactive Loop
print("Financial Chatbot - Ask your questions!")
print(f"Available companies: {', '.join(companies)}")
print("Examples:")
print("- What is the total revenue of Apple in 2022?")
print("- How has Tesla’s net income changed over the last year?")
print("- What is Microsoft's revenue growth in 2021?")
print("- Tell me about Tesla's asset growth.")
print("- What is Apple's net income trend?")
print("Type 'exit' to turn off this chatbot.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() in ['exit']:
        print("Goodbye!")
        break
    print("Bot:", simple_chatbot(user_input))