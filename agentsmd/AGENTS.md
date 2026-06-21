<skills>

You have additional SKILLs documented in directories containing a "SKILL.md" file.

These skills are:
 - hf-cli -> "skills/hf-cli/SKILL.md"
 - hf-mcp -> "skills/hf-mcp/SKILL.md"
 - hf-mem -> "skills/hf-mem/SKILL.md"
 - huggingface-best -> "skills/huggingface-best/SKILL.md"
 - huggingface-community-evals -> "skills/huggingface-community-evals/SKILL.md"
 - huggingface-datasets -> "skills/huggingface-datasets/SKILL.md"
 - huggingface-gradio -> "skills/huggingface-gradio/SKILL.md"
 - huggingface-llm-trainer -> "skills/huggingface-llm-trainer/SKILL.md"
 - huggingface-local-models -> "skills/huggingface-local-models/SKILL.md"
 - huggingface-lora-space-builder -> "skills/huggingface-lora-space-builder/SKILL.md"
 - huggingface-paper-publisher -> "skills/huggingface-paper-publisher/SKILL.md"
 - huggingface-papers -> "skills/huggingface-papers/SKILL.md"
 - huggingface-spaces -> "skills/huggingface-spaces/SKILL.md"
 - huggingface-tool-builder -> "skills/huggingface-tool-builder/SKILL.md"
 - huggingface-trackio -> "skills/huggingface-trackio/SKILL.md"
 - huggingface-vision-trainer -> "skills/huggingface-vision-trainer/SKILL.md"
 - huggingface-zerogpu -> "skills/huggingface-zerogpu/SKILL.md"
 - train-sentence-transformers -> "skills/train-sentence-transformers/SKILL.md"
 - transformers-js -> "skills/transformers-js/SKILL.md"
 - trl-training -> "skills/trl-training/SKILL.md"

IMPORTANT: You MUST read the SKILL.md file whenever the description of the skills matches the user intent, or may help accomplish their task. 

<available_skills>

hf-cli: `Hugging Face Hub CLI (`hf`) for downloading, uploading, and managing models, datasets, spaces, buckets, repos, papers, jobs, and more on the Hugging Face Hub`
hf-mcp: `Use Hugging Face Hub via MCP server tools. Search models, datasets, Spaces, papers. Get repo details, fetch documentation, run compute jobs, and use Gradio Spaces as AI tools. Available when connected to the HF MCP server.`
hf-mem: `Hugging Face CLI to estimate the required memory to load Safetensors or GGUF model weights for inference from the Hugging Face Hub`
huggingface-best: `Find the best AI model for any task by querying Hugging Face leaderboards and benchmarks. Recommends top models based on task type, hardware constraints, and benchmark scores`
huggingface-community-evals: `Run evaluations for Hugging Face Hub models using inspect-ai and lighteval on local hardware. Use for backend selection, local GPU evals, and choosing between vLLM / Transformers / accelerate. Not for HF Jobs orchestration, model-card PRs, .eval_results publication, or community-evals automation.`
huggingface-datasets: `Explore, query, and extract data from any Hugging Face dataset using the Dataset Viewer REST API and npx tooling`
huggingface-gradio: `Build Gradio web UIs and demos in Python. Use when creating or editing Gradio apps, components, event listeners, layouts, or chatbots`
huggingface-llm-trainer: `Train or fine-tune language models using TRL on Hugging Face Jobs infrastructure. Covers SFT, DPO, GRPO and reward modeling training methods, plus GGUF conversion for local deployment`
huggingface-local-models: `Use to select models to run locally with llama.cpp and GGUF on CPU, Mac Metal, CUDA, or ROCm. Covers finding GGUFs, quant selection, running servers, exact GGUF file lookup, conversion, and OpenAI-compatible local serving.`
huggingface-lora-space-builder: `Build and publish a Gradio demo on Hugging Face Spaces for a user-provided LoRA. Covers picking the right base pipeline and `diffusers` inference recipe, designing a UI tailored to the LoRA's task and inputs, respecting model-card recommendations, and shipping to ZeroGPU hardware.`
huggingface-paper-publisher: `Publish and manage research papers on Hugging Face Hub. Supports creating paper pages, linking papers to models/datasets, claiming authorship, and generating professional markdown-based research articles.`
huggingface-papers: `Look up and read Hugging Face paper pages in markdown, and use the papers API for structured metadata such as authors, linked models/datasets/spaces, Github repo and project page. Use when the user shares a Hugging Face paper page URL, an arXiv URL or ID, or asks to summarize, explain, or analyze an AI research paper.`
huggingface-spaces: `Build, deploy, and maintain applications on Hugging Face Spaces — Gradio / Docker / Static SDKs, ZeroGPU and dedicated hardware, model loading, debugging, buckets, inference providers, community grants`
huggingface-tool-builder: `Build reusable scripts for Hugging Face Hub and API workflows. Useful for chaining API calls, enriching Hub metadata, or automating repeated tasks.`
huggingface-trackio: `Track and visualize ML training experiments with Trackio. Use when logging metrics during training (Python API), firing alerts for training diagnostics, or retrieving/analyzing logged metrics (CLI). Supports real-time dashboard visualization, alerts with webhooks, HF Space syncing, and JSON output for automation.`
huggingface-vision-trainer: `Train and fine-tune object detection models (RTDETRv2, YOLOS, DETR) and image classification models (timm and transformers models) using Transformers Trainer API on Hugging Face Jobs infrastructure or locally. Includes COCO dataset format support, Albumentations augmentation, mAP/mAR metrics, trackio tracking, hardware selection, and Hub persistence.`
huggingface-zerogpu: `Coding rules for Gradio Spaces using Hugging Face Spaces ZeroGPU hardware. Covers `@spaces.GPU`, duration and quota tuning, pickle-based process isolation, `gr.State` semantics across the worker boundary, the CUDA availability model, concurrency safety, and CUDA wheel-only build constraints.`
train-sentence-transformers: `Train or fine-tune sentence-transformers models across all three architectures: SentenceTransformer (bi-encoder embeddings), CrossEncoder (rerankers), and SparseEncoder (SPLADE). Covers loss selection, hard-negative mining, evaluators, distillation, LoRA, Matryoshka, and Hugging Face Hub publishing.`
transformers-js: `Run state-of-the-art machine learning models directly in JavaScript/TypeScript for NLP, computer vision, audio processing, and multimodal tasks. Works in Node.js and browsers with WebGPU/WASM using Hugging Face models.`
trl-training: `Train and fine-tune transformer language models using TRL (Transformers Reinforcement Learning). Supports SFT, DPO, GRPO, KTO, RLOO and Reward Model training via CLI commands.`
</available_skills>

Paths referenced within SKILL folders are relative to that SKILL. For example the hf-datasets `scripts/example.py` would be referenced as `hf-datasets/scripts/example.py`. 

</skills>
