import sys
import os
from amplpy import AMPL, Environment

def main(argc, argv):
    # Initialize AMPL environment
    ampl = AMPL(Environment('/Applications/ampl'))
    ampl.setOption('solver', 'cplex')
    
    model_directory = '/Users/username/Downloads/diet'
    
    model_text = """
    # Sets and Parameters
    set NUTR;
    set FOOD;
    param cost {FOOD} >= 0;
    param f_min {FOOD} >= 0;
    param f_max {FOOD} >= 0;
    param n_min {NUTR} >= 0;
    param n_max {NUTR} >= 0;
    param Amt {FOOD, NUTR} >= 0;

    # Variable
    var Buy {j in FOOD} >= f_min[j], <= f_max[j];

    # Objective - minimize cost
    minimize Total_Cost: sum {j in FOOD} cost[j] * Buy[j];

    # Fixed portions constraints with new limits
    subject to Beef_Requirement:
        Buy['BEEF'] = 3;  # 1 per meal * 3 meals
    
    subject to Cabb_Limit:
        Buy['CABB'] <= 5;  # Maximum 5 units per day
    
    subject to Egg_Limit:
        Buy['EGG'] <= 3;   # Maximum 3 units per day
    
    subject to Mush_Requirement:
        Buy['MUSH'] = 3;  # 1 per meal * 3 meals
    
    subject to Rame_Requirement:
        Buy['RAME'] = 3;  # 1 per meal * 3 meals

    # Energy constraint for daily total
    subject to Energy_Max:
        sum {j in FOOD} Amt[j,'Ene'] * Buy[j] <= 2100;

    # Daily nutrition constraints
    subject to Nutrition {i in NUTR: i != 'Ene'}:
        sum {j in FOOD} Amt[j,i] * Buy[j] >= n_min[i];
    """
    
    with open(os.path.join(model_directory, 'diet.mod'), 'w') as f:
        f.write(model_text)
    
    ampl.read(os.path.join(model_directory, 'diet.mod'))
    ampl.read_data(os.path.join(model_directory, 'diet.dat'))
    
    # Solve
    ampl.solve()
    
    # Get results
    total_cost = ampl.get_objective('Total_Cost')
    buy = ampl.get_variable('Buy')
    
    print('\nDaily Diet Plan with Limits:')
    print('- BEEF, MUSH, RAME: 3 units each (1 per meal)')
    print('- CABB: maximum 5 units per day')
    print('- EGG: maximum 3 units per day')
    print('-' * 85)
    print('Food      Daily Amount    Per Meal*    Cost/unit    Daily Cost    Energy(kcal)')
    print('-' * 85)
    
    daily_total_cost = 0
    daily_total_energy = 0
    
    foods = ['BEEF', 'CABB', 'EGG', 'MUSH', 'RAME', 'SMEN']
    
    for food in foods:
        amount = buy[food].value()
        if amount > 0.001:  # Only show non-zero amounts
            per_meal = amount / 3  # Average per meal
            cost_per_unit = ampl.getParameter('cost')[food]
            energy_per_unit = ampl.getParameter('Amt')[food, 'Ene']
            daily_cost = amount * cost_per_unit
            daily_energy = amount * energy_per_unit
            daily_total_cost += daily_cost
            daily_total_energy += daily_energy
            
            print(f'{food:8} {amount:10.2f} {per_meal:10.2f} {cost_per_unit:12.2f} ${daily_cost:10.2f} {daily_energy:12.1f}')
    
    print('-' * 85)
    print(f'Totals:{" "*29} ${daily_total_cost:10.2f} {daily_total_energy:12.1f}')
    
    print(f'\nPer Meal Average:')
    print(f'Cost: ${daily_total_cost/3:.2f}')
    print(f'Energy: {daily_total_energy/3:.1f} kcal')
    
    # Display nutrition content
    print('\nDaily Nutrition Analysis:')
    print('-' * 65)
    print('Nutrient   Current Amount   Minimum Required   Maximum Allowed')
    print('-' * 65)
    
    for nutr in ['Sod', 'Ene', 'Prot', 'VitD', 'Calc', 'Iron', 'Pota']:
        current = sum(buy[f].value() * ampl.getParameter('Amt')[f, nutr] for f in foods)
        min_req = ampl.getParameter('n_min')[nutr]
        max_req = ampl.getParameter('n_max')[nutr]
        print(f'{nutr:8} {current:15.1f} {min_req:17.1f} {max_req:17.1f}')
        
    print('\nNote: *Per Meal shows average - actual distribution may vary for CABB and EGG')

if __name__ == '__main__':
    try:
        main(len(sys.argv), sys.argv)
    except Exception as e:
        print(e)
        raise
