# TouchProfiler

**TouchProfiler** is a modular performance diagnostics framework for TouchDesigner — designed for creators who need deep, actionable insight into the real-time behaviour of their networks.

It captures cook-time metrics, GPU load, memory usage, and dependency structures, then integrates with OpenAI's GPT API to provide intelligent, contextual optimisation suggestions. Whether you're building interactive installations, live AV systems, or computational artworks, TouchProfiler helps you move beyond guesswork — and into informed iteration.

---

## 🌐 Overview

TouchDesigner’s node-based paradigm empowers rapid experimentation — but scaling those experiments without visibility into system behaviour can be frustrating. 

**TouchProfiler** was built to solve this: by combining multi-frame performance sampling with automated graph traversal and large language model (LLM) reasoning, it becomes your intelligent co-pilot for profiling, debugging, and refining high-performance networks.

No UI panels. No black-box magic. Just data, structure, and informed guidance.

---

## ✅ Key Features

- 📊 **Live Metrics Sampling**  
  Gathers average cook time, GPU usage, cook count, and memory data over multiple frames.

- 🔗 **Dependency Graph Traversal**  
  Recursively maps the operator network using topological sorting, including input/output paths and key parameters.

- 🧠 **LLM-Powered Analysis**  
  Sends the full structural and performance snapshot to GPT models (e.g., gpt-4o) for contextual advice — such as identifying bottlenecks or suggesting refactors.

- 🧩 **Modular Design**  
  Built entirely with `Script CHOP` and `Text DAT` logic. Easily dropped into any project without interfering with rendering or control flows.

- 🧘 **Zero UI Overhead**  
  Fully headless operation — perfect for remote systems, background diagnostics, or embedded workflows.

---

## 📁 File Structure

```
TouchProfiler/
├── ProfilerCollector.tox       → Graph traversal & OP introspection
├── CookMetricsSampler.tox      → Multi-frame cook & memory metrics
├── ChatCaller.tox              → LLM interface (OpenAI API)
├── system_message              → GPT system prompt (performance analyst role)
├── input                       → Your project-specific question
├── output                      → GPT’s generated response
```

---

## ⚙️ Setup Guide

1. Place all `.tox` files into your `/project1` or other root container.
2. In each component, set the `Target COMP` parameter to the container you want to analyse.
3. In the `input` DAT, write your performance-related query.
   ```
   Example: Which nodes are performance bottlenecks and how should I optimise them?
   ```
4. Paste your OpenAI API key into the `apikey` field in `ChatCaller.tox`.
5. Trigger the `Send` pulse.

TouchProfiler will:
- Traverse the network and describe every relevant OP
- Sample performance metrics over a configurable number of frames
- Build a full system message including topology and metric summaries
- Send your query (along with this data) to the GPT model
- Output a structured, readable suggestion set in the `output` DAT

---

## 🧠 Example Use Case

### input
```
Evaluate the performance of my project.
```

### GPT response (typical output)
```
Your project seems to be running reasonably well based on the provided metrics. However, there are some areas that could be optimized to improve performance further:

1. **High Average Cook Times**:
   - While the cook times are generally low, the `ramp1`, `ramp2`, and `noise2` operators have the highest cook times within your project. You could inspect the configurations of these operators:
     - **Ramp Operators**: Review the resolution and antialias settings. If the resolution can be lower without impacting quality, adjust this.
     - **Noise Operators**: Consider reducing complexity, especially on noise2, which shows a higher GPU cook time.

2. **Redundant Channels**:
   - The `constant1` and `constant2` operators yield similar outputs and may be redundantly feeding into multiple operators. Review and consolidate constants if possible to save on processing cycles.

3. **Optimize Filters**:
   - For nodes like `reorder1` and `noise1` consistently using linear and nearest filters, check if more efficient filtering or reduced complexity could suffice.

4. **Feedback Loops**:
   - Feedback operators can cause high cooking times if not optimized. Review the content being processed in `feedback1` and `feedback2` to identify if they can be simplified or if the cooking frequency can be reduced.

5. **Memory Usage**:
   - Your average memory usage seems low, which is good. Ensure there are no memory leaks particularly with feedback operators that can sometimes accumulate data in memory.

6. **Eliminate Unneeded Operations**:
   - Evaluate your operator graph to see if there are any unnecessary nodes or if certain operations can be merged together.

Overall, while your project is functioning adequately, these adjustments can enhance performance further and contribute to smoother real-time interactions.
```

---


## 🧪 Example Project

The repository includes an example `.toe` file (`example_project.toe`) showcasing how TouchProfiler can be integrated into a layered, real-time feedback network.

You can preview the example patch in action here:  
▶️ [Watch on YouTube](https://www.youtube.com/watch?v=WavVlg3PZnk)

> _Conceptually inspired by the chaotic elegance of_ **Supermarket Sallad**.  
> *TouchProfiler helps reveal where the visual noise becomes computational noise.*

---

## 🧪 Metrics Collected

Each operator is sampled with the following metrics:

- `cookTime` (avg & std deviation)
- `gpuCookTime`
- `memoryUsed` (MB)
- `childrenCookTime`
- `cookCount`
- `cookAbsFrame`
- Composite Score = `avgCookTime × (1 + stdDev)`

Results are ranked by score and visualised via the `cookMetrics` DAT.

---

## 💬 Suggested Prompts

- “Which feedback loops cost the most, and are they necessary?”
- “Can I consolidate constants or math operators to optimise performance?”
- “Where is the GPU time being spent, and can it be deferred or cached?”
- “Is this patch architecture sustainable for real-time 4K rendering?”

---

## 🔒 Limitations

- Requires an active OpenAI API key (GPT-3.5, GPT-4, or GPT-4o)
- Max token limit for the full message is ~20K (nodes may be trimmed in large networks)
- Cyclic graphs are partially supported (nodes in feedback may be skipped)
- Visualisation of the OP tree is currently text-based only (graph view planned)

---

## 🔮 Roadmap

- TouchGraph visualisation with live heatmapping
- OSC/WebSocket bridge for remote profiling sessions
- Auto-refactor suggestions (experimental)
- LLM persona switching: `debugger`, `explainer`, `minimalist`, `GPU-optimizer`
- Token-aware sampler for very large networks

---

## 🧾 License

MIT License  
Free for personal, academic, and commercial use.

---

## 🙋 Author

**Saim Gülay**  
[github.com/saimgulay](https://github.com/saimgulay)

Built for those moments when your patch runs at 48fps, and you don’t know why.  
TouchProfiler doesn't guess — it shows you the why, and suggests the how.
