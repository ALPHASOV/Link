## DevAI Dataset Usage Guide


> [!IMPORTANT]
> 
> As a **proof-of-concept**, we applied **Agent-as-a-Judge** to code generation tasks using **DevAI**, a benchmark consisting of 55 realistic AI development tasks with 365 hierarchical user requirements. The results show that **Agent-as-a-Judge** significantly outperforms traditional evaluation methods, providing reliable reward signals for scalable self-improvement in agentic systems.
> 
> You can access the dataset on [Hugging Face 🤗](https://huggingface.co/DEVAI-benchmark). Detailed usage instructions can be found in the [guidelines](../../benchmark/devai/README.md).

---

### Overview


<div align="center">
    <img src="../../assets/dataset.png" alt="Dataset" style="width: 100%; max-width: 600px;">
</div>


**DevAI** consists of a curated set of 55 tasks, each structured to facilitate agentic AI development. Each task includes the following components:

1. **User Query**: A plain text query describing the AI development task.
2. **Requirements**: A set of 365 hierarchical requirements, with dependencies connecting them to other tasks.
3. **Preferences**: A set of 125 optional preferences representing softer requirements.

The **DevAI** dataset is designed to evaluate agentic systems by giving them user queries and assessing how well they meet the specified requirements. Preferences serve as optional, softer evaluation criteria.

Each task is relatively small in scope but covers key AI development techniques, such as:

- Supervised Learning
- Reinforcement Learning
- Computer Vision
- Natural Language Processing
- Generative Models

These tasks simulate real-world problems that a research engineer might face, while also being computationally inexpensive—making them ideal for large-scale evaluations. The tasks are tagged across various AI fields, ensuring comprehensive evaluation coverage.

---

### Task Structure

Tasks in **DevAI** are organized as a **directed acyclic graph (DAG)**, where certain requirements depend on others being completed first. For example, visualizing results may depend on proper data loading and modeling. This structure ensures more detailed feedback than simple binary success metrics.

This hierarchical design prevents simple memorization-based solutions, making agentic capabilities essential for solving the tasks. Systems need to tackle the full development pipeline, rather than rely on memorization, as is typical in many foundation models.

<div align="center">
    <img src="../../assets/sample.jpeg" alt="Sample" style="width: 100%; max-width: 600px;">
</div> 


---

### How to Use the Dataset

1. **Developing an Agentic System**:
    - We hypothesize that your agentic system can receive a human query, similar to agents like **Devin**, **OpenHands**, **MetaGPT**, or **GPT-Pilot**. After processing, your agent will output a workspace.

2. **Collecting Trajectories**:
    - For accurate evaluation, we recommend collecting the output workspace and execution trajectories from your agent. You can refer to a sample trajectory we collected from **OpenHands** [here](../../benchmark/trajectories/OpenHands/39_Drug_Response_Prediction_SVM_GDSC_ML.json). The format follows the [trajectory-schema](../../benchmark/devai/trajectory-schema.json), and you can use [`validate_trajectory.py`](../../benchmark/devai/validate_trajectory.py) to verify the format.

3. **Input Constraints**:
    - Input the constraints shown in [constraints.json](../../benchmark/devai/constraints.json) into your system prompts to ensure the agentic system understands the task details clearly.

4. **Organizing Workspaces and Trajectories**:
    - Place the generated workspaces from your agentic systems in `benchmark/workspaces/{YOUR_AGENTIC_SYSTEM}` and the collected trajectories in `benchmark/trajectories/{YOUR_AGENTIC_SYSTEM}`. The workspace and trajectory names should follow the original instance name from the dataset. For example:
      - Workspace: `benchmark/workspaces/OpenHands/39_Drug_Response_Prediction_SVM_GDSC_ML`
      - Trajectory: `benchmark/trajectories/OpenHands/39_Drug_Response_Prediction_SVM_GDSC_ML.json`

---

For more details on how the dataset was collected and labeled, please refer to the [paper](https://arxiv.org/pdf/2410.10934).

