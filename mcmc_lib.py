import numpy as np

import numpy as np
from scipy.stats import beta

def simulate_job_search(number_of_months_looking, optimistic_months, likely_months, pessimistic_months):
    # Calculate alpha and beta for Beta-PERT distribution
    alpha = 1 + (4 * likely_months + optimistic_months - pessimistic_months) / (pessimistic_months - optimistic_months)
    beta_param = 1 + (4 * likely_months + pessimistic_months - optimistic_months) / (pessimistic_months - optimistic_months)
    
    # Calculate cumulative probability distribution over the range [optimistic, pessimistic]
    scale = pessimistic_months - optimistic_months
    x = np.linspace(0, 1, int(pessimistic_months - optimistic_months + 1))  # Normalized scale
    cumulative_probs = beta.cdf(x, alpha, beta_param)
    
    # Adjust probabilities to match the month indices starting from optimistic_months
    month_indices = np.arange(optimistic_months, pessimistic_months + 1)
    month_to_prob = dict(zip(month_indices, cumulative_probs))

    # Determine the probability threshold for each month
    for month in range(optimistic_months, number_of_months_looking + 1):
        if month in month_to_prob:
            current_prob = month_to_prob[month]
        else:
            current_prob = month_to_prob[pessimistic_months]  # Use last available probability for extended months

        # Simulate job finding based on the cumulative probability
        if np.random.rand() < current_prob:
            return True  # Job found within this month

    return False  # Job not found within the specified number of months



def mcmc_simulation(options, num_iterations=10000):
    npv_differences = []
    option1_payment_timeline = []
    option2_payment_timeline = []

    optimistic_months  = options["optimistic_months"]
    likely_months      = options["likely_months"]
    pessimistic_months = options["pessimistic_months"]

    
    for _ in range(num_iterations):

        new_job_salary = np.random.normal(options["expected_new_job_monthly_salary"], 24000/12)  
        
        monthly_salary_after_tax = options["monthly_salary_after_tax"]

        option1_income_stream = [monthly_salary_after_tax] * options["time_horizon_months"]
        option2_income_stream = [0] * options["time_horizon_months"]
        
        # Immediately apply the lump sum for Option 2
        option2_income_stream[0] = options["lump_sum"] * (1 - options["lump_sum_tax_rate"])

        option1_job_cut_happened = False
        option1_job_cut_month = None
        option1_new_job_happened = False
        option2_new_job_happened = False        
        
        for month in range(options["time_horizon_months"]):
            #if np.random.rand() <
            prob_job_loss = options["prob_job_loss"]
            
            # option 1 - stay
            if not option1_job_cut_happened:
                if np.random.rand() < prob_job_loss:
                    option1_job_cut_happened = True
                    option1_job_cut_month = month
                    # Clear subsequent months if job is lost
                    option1_income_stream[month:] = [0] * (options["time_horizon_months"] - month)
            else:
                if not option1_new_job_happened:
                    option1_new_job_happened = simulate_job_search(month - option1_job_cut_month, optimistic_months, likely_months, pessimistic_months)
                    
                if option1_new_job_happened:
                    option1_income_stream[month] = new_job_salary * (1 - options["monthly_tax_rate_option1"])                    
            
            # option 2 - enh retire
            if not option2_new_job_happened:
                option2_new_job_happened = simulate_job_search(month, optimistic_months, likely_months, pessimistic_months)
                        
            if option2_new_job_happened:
                option2_income_stream[month] = new_job_salary * (1 - options["monthly_tax_rate_option1"])

        option1_npv = sum([val / (1 + options["discount_rate"] / 12) ** idx for idx, val in enumerate(option1_income_stream)])
        option1_payment_timeline.append(option1_income_stream)

        option2_npv = sum([val / (1 + options["discount_rate"] / 12) ** idx for idx, val in enumerate(option2_income_stream)])
        option2_payment_timeline.append(option2_income_stream)

        npv_differences.append(option1_npv - option2_npv)

    return npv_differences, option1_payment_timeline, option2_payment_timeline
