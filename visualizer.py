import matplotlib.pyplot as plt

def create_language_chart(data):

    labels = list(data.keys())
    values = list(data.values())

    plt.figure()
    plt.pie(values, labels=labels)

    filename = "chart.png"
    plt.savefig(filename)

    return filename