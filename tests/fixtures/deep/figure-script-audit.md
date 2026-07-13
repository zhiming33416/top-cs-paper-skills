# Existing plotting script notes

Figure 2 currently reports latency for the systems experiment.

Facts to preserve:
- Best observed median latency: 12.4 ms.
- Batch size 16.
- Existing output path: fig2.png.
- Manuscript reference: Figure 2.

Script excerpt:

```python
import matplotlib.pyplot as plt
plt.plot(tokens, latency)
plt.ylabel("Latency")
plt.savefig("fig2.png")
```

Known limitation: the script only exports PNG, does not set editable SVG text, and omits hardware and sequence-length labels.
