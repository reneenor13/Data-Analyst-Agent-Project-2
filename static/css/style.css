import base64
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np

def make_scatterplot_with_regression(x, y):
    plt.figure(figsize=(8, 6))
    plt.scatter(x, y, alpha=0.5)
    m, b = np.polyfit(x, y, 1)
    plt.plot(x, m*x + b, linestyle='--', color='red')
    plt.xlabel("Rank")
    plt.ylabel("Peak")
    plt.title("Scatterplot of Rank vs Peak")

    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    img_data = base64.b64encode(buf.read()).decode("utf-8")
    return f"data:image/png;base64,{img_data}"
