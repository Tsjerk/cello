
# 🎻 Cello Plot

A smooth, color-aware alternative to violin plots — ideal for visualizing distributions with continuous or per-sample color information.

The **cello plot** computes a smoothed density over the data and renders it as a shaded violin-like shape, optionally with:

* Color blending based on value-specific colors
* Horizontal or vertical orientation
* Left/right asymmetry (half-cellos)
* Grouped distributions (2-D input)
* Full control over bandwidth and scale

---

## 🔧 Installation

Until a PyPI release is appropriate, you can install directly from Git:

```bash
pip install git+https://github.com/<yourname>/cello
```

Or simply copy the `cello.py` file into your project.

---

## ✨ Usage

### Basic example

```python
import numpy as np
import matplotlib.pyplot as plt
from cello import cello

values = np.random.randn(200)
cello(values, c='skyblue', position=1)
plt.show()
```

### Grouped distributions

```python
groups = np.array([
    np.random.randn(150) + i
    for i in range(3)
])
cello(groups, scale=12)
plt.show()
```

### With per-sample color

```python
x = np.random.randn(300)
colors = plt.cm.plasma((x - x.min()) / (x.max() - x.min()))
cello(x, c=colors, position=1, side='right')
plt.show()
```

### Horizontal layout

```python
cello(groups, horizontal=True, scale=8)
plt.show()
```

---

## 📌 Function signature

```python
cello(values, c=None, position=None, bw=0.5, cbw=None, scale=10,
      points=100, horizontal=False, side='both', ax=None, **kwargs)
```

| Parameter    | Description                                         |
| ------------ | --------------------------------------------------- |
| `values`     | 1D or 2D array of observations                      |
| `c`          | Single color, per-value colors, or per-group colors |
| `position`   | Baseline position(s) for the plot(s)                |
| `bw`         | Kernel-like smoothing bandwidth                     |
| `cbw`        | Bandwidth for color smoothing/blending              |
| `scale`      | Vertical (or horizontal) size scaling               |
| `horizontal` | Flip axes                                           |
| `side`       | `'both'`, `'left'`, or `'right'`                    |
| `ax`         | Axes to draw on                                     |

📤 The function returns a dictionary containing:

* The density grid (`points`, `density`)
* Plot elements (`mesh`, line handles)
* The `ax` object used
* For 2-D input: a list of per-group results

---

## 🧠 Interpretation

* Density is normalized using **total weight**, so cellos are comparable across datasets, independent of sample size.
* Color blending is performed by kernel-weighted averaging — smoothly transitions across the distribution.
* Shapes resemble violins but can express **continuous gradients**, making them useful for:

  * multimodal or spatial transcriptomics (gene/color mapping)
  * time series stratified distributions
  * cluster overlays
  * categorical distributions with continuous covariates

---

## ✅ Requirements

✅ NumPy
✅ Matplotlib

(No heavy dependencies.)

---

## 📍 Roadmap

* ✅ Recursive group plotting
* ✅ Color KDE blending
* ⬜ Legend utilities
* ⬜ Optional kernel choices
* ⬜ Interactive hover stats

Want to contribute? Pull requests are welcome.

---

## 📄 License

MIT License — feel free to use, modify, and share.

---

If you'd like, I can also:
✔ generate example images for the README
✔ write a minimal `pyproject.toml` for packaging
✔ add a gallery notebook
✔ set up CI for unit tests (optional)

Would you like me to produce the example plots so you can include thumbnails in the README?

