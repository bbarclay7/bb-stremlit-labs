
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from mcmc_lib import mcmc_simulation
import threading
_lock = threading.RLock()
from matplotlib.backends.backend_agg import RendererAgg


def plot_npv_differences(npv_differences):
    plt.figure(figsize=(10, 6))
    plt.hist(npv_differences, bins=50, color='skyblue', edgecolor='black', alpha=0.7)
    plt.axvline(0, color='red', linestyle='dashed', linewidth=2, label="No Difference (0)")
    plt.title('Distribution of NPV Difference (Stay in Current Job - Take Enhanced Retirement)')
    plt.xlabel('NPV Difference (Stay in Current Job - Take Enhanced Retirement)')
    plt.ylabel('Frequency')
    plt.legend()
    plt.grid(True)
    st.pyplot(plt.gcf())  # Display the plot in the Streamlit app

def plot_payment_timeline(option1_payment_timeline, option2_payment_timeline, time_horizon_months):
    # Calculate mean payments across all simulations
    mean_option1_payments = np.mean(option1_payment_timeline, axis=0)
    mean_option2_payments = np.mean(option2_payment_timeline, axis=0)
    cumulative_option1 = np.cumsum(mean_option1_payments)
    cumulative_option2 = np.cumsum(mean_option2_payments)

    # Plot the timelines
    months = list(range(1, time_horizon_months + 1))
    plt.figure(figsize=(14, 8))
    
    plt.subplot(2, 1, 1)
    plt.plot(months, mean_option1_payments, label="Option 1: Stay in Current Job", color='blue')
    plt.plot(months, mean_option2_payments, label="Option 2: Take Enhanced Retirement", color='green')
    plt.title('Monthly Expected Payments')
    plt.xlabel('Month')
    plt.ylabel('Payment ($)')
    plt.legend()
    plt.grid(True)

    plt.subplot(2, 1, 2)
    plt.plot(months, cumulative_option1, label="Option 1: Cumulative Payments", color='blue')
    plt.plot(months, cumulative_option2, label="Option 2: Cumulative Payments", color='green')
    plt.title('Cumulative Payments Over Time')
    plt.xlabel('Month')
    plt.ylabel('Cumulative Payment ($)')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    st.pyplot(plt.gcf())  # Display the plot in the Streamlit app

# Streamlit app layout
st.title("Enhanced Retirement Decision Analysis")
st.write("This tool helps you evaluate whether to take an enhanced retirement offer or continue employment by simulating possible outcomes based on your assumptions.")
st.write("Disclaimer: The information provided by this application is for general informational and educational purposes only. All information on the app is provided in good faith, however we make no representation or warranty of any kind, express or implied, regarding the accuracy, adequacy, validity, reliability, availability, or completeness of any information on the app. Under no circumstance shall we have any liability to you for any loss or damage of any kind incurred as a result of the use of the app or reliance on any information provided on the app. Your use of the app and your reliance on any information on the app is solely at your own risk. This application does not offer real-time data or comprehensive analysis and should not be used for making actual job-related or financial decisions. The output of the app should not be interpreted as a definite offer, career advice, or a guarantee of employment.")
# Blurb on how to interpret the graph
st.markdown("""
### Option 1: Stay in Current Job
- You continue receiving your monthly salary, but there is a risk that you may be laid off unexpectedly. If either event occurs, you transition to job hunting without receiving a lump sum.

### Option 2: Take Enhanced Retirement
- You receive a lump-sum payment (after taxes) and seek a new job. There’s a risk of not finding a comparable job, which would leave you reliant on the lump sum.

""")

# Input parameters

st.write("## Salary Information for current position")
yearly_salary_before_tax = st.slider("Annual Salary Before Tax for Current Job ($)", min_value=30000, max_value=400000, value=100000, step=5000)
monthly_tax_rate_option1 = st.slider("Monthly Tax Rate (%)", min_value=0.0, max_value=1.0, value=0.3, step=0.01)
monthly_salary_after_tax = (yearly_salary_before_tax / 12) * (1 - monthly_tax_rate_option1)
prob_job_loss = st.slider("Probability of Job Loss in the next 12 months (%)", min_value=0.0, max_value=100., value=10., step=1.) / 100. / 12.


st.write("## Enhanced retirement offer")
lump_sum = st.number_input("Lump Sum Before Tax ($)", value=75000)
lump_sum_tax_rate = st.slider("Lump Sum Tax Rate (%)", min_value=0.0, max_value=1.0, value=0.5, step=0.01)

st.write("## Job hunt parameters")
optimistic_months = st.slider(
    "Optimistic months to find a job",
    min_value=0., max_value=24., value=2., step=1.)

likely_months = st.slider(
    "Likely months to find a job",
    min_value=0., max_value=24., value=9., step=1.)

pessimistic_months = st.slider(
    "Pessimistic months to find a job",
    min_value=0., max_value=24., value=18., step=1.)

expected_new_job_salary = st.slider("Expected New Job Annual Salary ($)", min_value=30000, max_value=400000, value=90000, step=5000)

st.write("## Calculation constraints")
discount_rate = st.slider("Discount Rate (%) (for NPV calculation)", min_value=0.0, max_value=0.1, value=0.05, step=0.01)
time_horizon_months = st.slider("Time Horizon (Months)", min_value=12, max_value=60, value=24)



st.markdown("""## Implementation notes
The job search simulation we've developed utilizes a Monte Carlo Markov Chain (MCMC) approach, running 10,000 iterations to estimate the financial outcomes of continuing current employment versus accepting an enhanced retirement offer. It dynamically models the risk of job loss and the subsequent job-hunting phase, using user-defined optimistic, pessimistic, and most likely durations to shape the job-finding probabilities with a Beta-PERT distribution. Both employment scenarios—staying in the current job or opting for retirement—converge on identical job-hunting dynamics, providing a robust analysis of potential financial implications and aiding users in making informed decisions under uncertain job security conditions.
""")


# Run MCMC simulation
if st.button("Run Simulation"):
    options = {
        "monthly_salary_after_tax": monthly_salary_after_tax,
        "lump_sum": lump_sum,
        "lump_sum_tax_rate": lump_sum_tax_rate,
        "expected_new_job_monthly_salary": expected_new_job_salary / 12,
        "monthly_tax_rate_option1": monthly_tax_rate_option1,
        "discount_rate": discount_rate,
        "time_horizon_months": time_horizon_months,
        "prob_job_loss": prob_job_loss,
        "optimistic_months": int(optimistic_months),
        "likely_months": int(likely_months),
        "pessimistic_months": int(pessimistic_months),
    }

    npv_differences, option1_payment_timeline, option2_payment_timeline = mcmc_simulation(options, num_iterations=10000)

    # Plot results
    # matplotlib is not thread safe; streamlit recommends mutexing it
    _lock.acquire()
    plot_npv_differences(npv_differences)
    plot_payment_timeline(option1_payment_timeline, option2_payment_timeline, options["time_horizon_months"])
    _lock.release()

    # Summary statistics
    st.write(f"Mean NPV Difference (Stay in Current Job - Take Enhanced Retirement): ${np.mean(npv_differences):,.2f}")
    st.write(f"Probability Staying in Current Job is Superior: {np.mean(np.array(npv_differences) > 0) * 100:.2f}%")
    st.write(f"Probability Taking Enhanced Retirement is Superior: {np.mean(np.array(npv_differences) < 0) * 100:.2f}%")

    st.markdown("""
### How to Interpret the Graph:
1. **Histogram:** The x-axis represents the difference in NPV (Net Present Value) between staying in your current job (Option 1) and taking the enhanced retirement offer (Option 2). The y-axis represents the frequency of occurrences for different NPV differences across the simulated scenarios.
    - **Red Line (0 NPV Difference):** Marks the point where both options have the same NPV.
    - If the bars are mostly to the left (negative NPV difference), **Option 2 (Take Enhanced Retirement)** is generally better.
    - If the bars are mostly to the right (positive NPV difference), **Option 1 (Stay in Current Job)** is generally better.

2. **Payment Timeline:** The timeline shows expected monthly payments and cumulative payments for each option over the time horizon, allowing you to visualize cash flows and how each decision plays out over time.
""")
    
