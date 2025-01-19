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
