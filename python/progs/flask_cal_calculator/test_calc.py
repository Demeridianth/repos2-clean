import calorie_calc



def test_calculate_bmr_tdee():
    assert calorie_calc.calculate_bmr_tdee('male', 90, 182, 35, 'light') == 2567.8125
    
    
# print(calorie_calc.calculate_bmr_tdee('male', 90, 182, 35, 'light'))