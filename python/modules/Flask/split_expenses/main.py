from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error = None

    if request.method == 'POST':
        try:
            total_amount = float(request.form['total_amount'])
            number_of_people = int(request.form['number_of_people'])
            currency = request.form['currency']
            uneven = request.form.get('choice')

            if number_of_people < 1:
                raise ValueError('Number of people must be more than one')

            if uneven == 'yes':
                percentages = [float(request.form.get(f'percent_{i}')) for i in range(1, number_of_people + 1)]
                if sum(percentages) != 100:
                    raise ValueError("Percentages must add up to 100")

                result = [
                    {
                        'person': i + 1,
                        'amount': (percent / 100) * total_amount,
                        'percentage': percent
                    }
                    for i, percent in enumerate(percentages)
                ]
            else:
                share = total_amount / number_of_people
                result = [
                    {
                        'person': i + 1,
                        'amount': share,
                        'percentage': 100 / number_of_people
                    }
                    for i in range(number_of_people)
                ]

        except Exception as e:
            error = str(e)

    return render_template('index.html', result=result, error=error)

if __name__ == '__main__':
    app.run(debug=True)
